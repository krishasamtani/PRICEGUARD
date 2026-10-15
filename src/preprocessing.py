import pandas as pd
import numpy as np

def clean_and_normalize(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans raw mandi data:
    1. Handles missing values & deduplication
    2. Filters out negative or impossible price records
    3. Normalizes modal prices to ₹/kg for transparent policymaker reporting
    4. Interpolates missing dates to ensure continuous daily time series
    """
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df = df.drop_duplicates(subset=['date', 'commodity', 'market'])
    
    # Filter anomalous non-positive prices
    df = df[df['modal_price'] > 50.0]
    
    # Convert ₹/Quintal to ₹/kg
    df['price_per_kg'] = df['modal_price'] / 100.0
    
    # Check if new columns exist (to support both demo and real mode gracefully)
    agg_dict = {
        'price_per_kg': 'mean',
        'arrival_qty': 'sum',
        'rainfall_7d_mm': 'mean'
    }
    
    if 'temp_max_7d_avg' in df.columns:
        agg_dict['temp_max_7d_avg'] = 'mean'
    if 'humidity_7d_avg' in df.columns:
        agg_dict['humidity_7d_avg'] = 'mean'
    if 'production_tonnes' in df.columns:
        agg_dict['production_tonnes'] = 'max' # Same year production is static per district
        
    # Aggregate to daily national/state index for macro decision making
    daily_df = df.groupby('date').agg(agg_dict).reset_index()
    
    # Complete missing calendar days
    daily_df = daily_df.set_index('date').asfreq('D')
    daily_df['price_per_kg'] = daily_df['price_per_kg'].interpolate(method='time').bfill().ffill()
    daily_df['arrival_qty'] = daily_df['arrival_qty'].interpolate(method='time').bfill().ffill()
    daily_df['rainfall_7d_mm'] = daily_df['rainfall_7d_mm'].fillna(0.0)
    
    if 'temp_max_7d_avg' in daily_df.columns:
        daily_df['temp_max_7d_avg'] = daily_df['temp_max_7d_avg'].interpolate(method='time').bfill().ffill()
    if 'humidity_7d_avg' in daily_df.columns:
        daily_df['humidity_7d_avg'] = daily_df['humidity_7d_avg'].interpolate(method='time').bfill().ffill()
    if 'production_tonnes' in daily_df.columns:
        daily_df['production_tonnes'] = daily_df['production_tonnes'].ffill().bfill()
        
    return daily_df.reset_index()

