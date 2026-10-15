import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_synthetic_commodity_data(commodity="Onion", days=1200, seed=42) -> pd.DataFrame:
    """
    Generates realistic, physically consistent synthetic data for Onion and Tur
    including prices, arrival quantities, rainfall anomalies, and seasonal spikes.
    """
    np.random.seed(seed if commodity == "Onion" else seed + 101)
    
    end_date = datetime.today()
    start_date = end_date - timedelta(days=days - 1)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    n = len(dates)
    
    t = np.linspace(0, (days / 365.25) * 2 * np.pi, n)
    
    if commodity == "Onion":
        # Base price around ₹22/kg with cyclical seasonality (peak in Sep-Nov)
        base_price = 24.0 + 3.0 * (dates.dayofyear / 365.25)
        seasonal_cycle = 12.0 * np.sin(t - 1.2) + 5.0 * np.sin(2 * t)
        noise = np.random.normal(0, 2.5, n)
        
        # Inject historical price crises (e.g., post-monsoon crop damage)
        crisis_1 = 35.0 * np.exp(-0.5 * ((np.arange(n) - (n - 220)) / 18) ** 2)
        crisis_2 = 45.0 * np.exp(-0.5 * ((np.arange(n) - (n - 60)) / 14) ** 2)
        
        prices_kg = np.maximum(base_price + seasonal_cycle + noise + crisis_1 + crisis_2, 8.0)
        
        # Inverted supply: High price correlates with low mandi arrivals
        base_arrivals = 1200.0 - (prices_kg * 18.0) + np.random.normal(0, 60, n)
        arrivals_mt = np.maximum(base_arrivals, 80.0)
        
        # Rainfall in Maharashtra / Nashik belt (monsoon peak Jun-Sep)
        rainfall_base = 8.0 * np.maximum(np.sin(t - 0.5), 0) ** 2
        rainfall_7d = rainfall_base * 7.0 + np.random.exponential(12.0, n) * (rainfall_base > 0.5)
        
        markets = ["Lasalgaon", "Pimpalgaon", "Nashik", "Azadpur (Delhi)", "Solapur"]
        state = "Maharashtra"

    else: # Tur / Arhar
        base_price = 85.0 + 8.0 * (dates.dayofyear / 365.25)
        seasonal_cycle = 14.0 * np.sin(t - 0.8)
        noise = np.random.normal(0, 3.5, n)
        
        # Supply gap spike
        crisis_1 = 40.0 * np.exp(-0.5 * ((np.arange(n) - (n - 150)) / 25) ** 2)
        prices_kg = np.maximum(base_price + seasonal_cycle + noise + crisis_1, 45.0)
        
        base_arrivals = 600.0 - (prices_kg * 3.5) + np.random.normal(0, 30, n)
        arrivals_mt = np.maximum(base_arrivals, 40.0)
        
        rainfall_base = 6.0 * np.maximum(np.sin(t - 0.4), 0) ** 2
        rainfall_7d = rainfall_base * 7.0 + np.random.exponential(10.0, n) * (rainfall_base > 0.5)
        
        markets = ["Kalaburagi (Gulbarga)", "Latur", "Akola", "Nagpur", "Indore"]
        state = "Karnataka"

    # Convert ₹/kg to Mandi standard ₹/Quintal (1 Quintal = 100 kg)
    modal_price_quintal = prices_kg * 100.0
    min_price_quintal = modal_price_quintal * np.random.uniform(0.88, 0.95, n)
    max_price_quintal = modal_price_quintal * np.random.uniform(1.05, 1.15, n)
    
    records = []
    for i in range(n):
        market_choice = markets[i % len(markets)]
        records.append({
            "date": dates[i],
            "state": state,
            "district": market_choice.split()[0],
            "market": market_choice,
            "commodity": commodity,
            "min_price": round(float(min_price_quintal[i]), 2),
            "max_price": round(float(max_price_quintal[i]), 2),
            "modal_price": round(float(modal_price_quintal[i]), 2),
            "arrival_qty": round(float(arrivals_mt[i]), 2),
            "rainfall_7d_mm": round(float(rainfall_7d[i]), 2)
        })
        
    return pd.DataFrame(records)
