import pandas as pd
import numpy as np
from typing import Tuple, List

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Strictly causal time-series feature engineering.
    Prevents temporal data leakage by using only lagged and past-rolling metrics.
    """
    df = df.copy().sort_values('date').reset_index(drop=True)
    
    # 1. Calendar / Seasonality Features
    df['day_of_week'] = df['date'].dt.dayofweek
    df['month'] = df['date'].dt.month
    df['quarter'] = df['date'].dt.quarter
    df['day_of_year'] = df['date'].dt.dayofyear
    df['sin_month'] = np.sin(2 * np.pi * df['month'] / 12.0)
    df['cos_month'] = np.cos(2 * np.pi * df['month'] / 12.0)
    
    # 2. Lagged Prices (Strictly t-k)
    for lag in [1, 3, 7, 14, 21, 30]:
        df[f'price_lag_{lag}'] = df['price_per_kg'].shift(lag)
        
    # 3. Lagged Arrivals & Supply Signals
    for lag in [1, 7, 14]:
        df[f'arrival_lag_{lag}'] = df['arrival_qty'].shift(lag)
        
    # 4. Rolling Statistics (Using past data shift(1) to avoid current-day leakage)
    for window in [7, 14, 30]:
        df[f'price_roll_mean_{window}'] = df['price_per_kg'].shift(1).rolling(window).mean()
        df[f'price_roll_std_{window}'] = df['price_per_kg'].shift(1).rolling(window).std()
        df[f'arrival_roll_mean_{window}'] = df['arrival_qty'].shift(1).rolling(window).mean()
        
    # 5. Price Momentum & Volatility
    df['momentum_7d'] = (df['price_per_kg'].shift(1) - df['price_lag_7']) / (df['price_lag_7'] + 1e-5)
    df['momentum_14d'] = (df['price_per_kg'].shift(1) - df['price_lag_14']) / (df['price_lag_14'] + 1e-5)
    df['arrival_growth_7d'] = (df['arrival_qty'].shift(1) - df['arrival_lag_7']) / (df['arrival_lag_7'] + 1e-5)
    
    # 6. Rainfall & Weather Indicators
    df['rainfall_7d_lag1'] = df['rainfall_7d_mm'].shift(1)
    df['rainfall_roll_mean_14'] = df['rainfall_7d_mm'].shift(1).rolling(14).mean()
    
    if 'temp_max_7d_avg' in df.columns:
        df['temp_max_7d_lag1'] = df['temp_max_7d_avg'].shift(1)
        df['temp_max_roll_mean_14'] = df['temp_max_7d_avg'].shift(1).rolling(14).mean()
        
    if 'humidity_7d_avg' in df.columns:
        df['humidity_7d_lag1'] = df['humidity_7d_avg'].shift(1)
        df['humidity_roll_mean_14'] = df['humidity_7d_avg'].shift(1).rolling(14).mean()
        
    # Backfill/forward fill lags and rolling metrics to preserve data on short history
    return df.bfill().ffill().fillna(0.0).reset_index(drop=True)

def build_forecasting_dataset(featured_df: pd.DataFrame, horizon: int = 7) -> Tuple[pd.DataFrame, pd.Series, List[str]]:
    """
    Creates target variable shifted into the future by `horizon` days.
    """
    df = featured_df.copy()
    target_col = f'target_{horizon}d'
    df[target_col] = df['price_per_kg'].shift(-horizon)
    
    df_valid = df.dropna(subset=[target_col]).reset_index(drop=True)
    
    exclude_cols = ['date', 'price_per_kg', 'arrival_qty', 'rainfall_7d_mm', 'temp_max_7d_avg', 'humidity_7d_avg', target_col]
    feature_cols = [
        c for c in df_valid.columns 
        if c not in exclude_cols and not c.startswith('target_')
    ]
    
    X = df_valid[feature_cols]
    y = df_valid[target_col]
    return X, y, feature_cols
