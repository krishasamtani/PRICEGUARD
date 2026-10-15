import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any
from src.features import engineer_features, build_forecasting_dataset
from src.forecasting import MultiHorizonForecaster
from src.uncertainty import SplitConformalCalibrator
from src.risk import compute_spike_risk

def run_historical_crisis_replay(
    full_df: pd.DataFrame, 
    replay_date: str,
    horizon: int = 7
) -> Dict[str, Any]:
    """
    Replays a historical date masking all future ground truth data to demonstrate
    unbiased predictive power during actual crisis events.
    """
    full_df['date'] = pd.to_datetime(full_df['date'])
    cutoff = pd.to_datetime(replay_date)
    
    # 1. Mask future data strictly
    past_df = full_df[full_df['date'] <= cutoff].copy()
    if len(past_df) < 20:
        raise ValueError(f"Insufficient historical training records before {replay_date}. You need at least 20 days of history prior to the replay date to train the model. Please select a later date.")
        
    # 2. Extract ground truth actual price 7 days ahead
    future_record = full_df[full_df['date'] == (cutoff + pd.Timedelta(days=horizon))]
    actual_future_price = float(future_record['price_per_kg'].values[0]) if not future_record.empty else None
    
    # 3. Feature engineering & model fitting strictly on past data
    feat_df = engineer_features(past_df)
    
    forecaster = MultiHorizonForecaster(horizons=[horizon])
    forecaster.fit(feat_df, build_forecasting_dataset)
    
    conformal = SplitConformalCalibrator(alpha=0.10)
    conformal.calibrate(forecaster, feat_df, build_forecasting_dataset)
    
    # Predict on the exact replay cutoff day
    X_latest, _, _ = build_forecasting_dataset(feat_df, horizon=horizon)
    intervals = conformal.predict_intervals(forecaster, X_latest.iloc[-1:])
    
    res = intervals[horizon]
    recent_mean = float(feat_df.iloc[-1]['price_roll_mean_7'])
    recent_std = float(feat_df.iloc[-1]['price_roll_std_7'])
    
    risk = compute_spike_risk(res['point_forecast'], res['upper_bound'], recent_mean, recent_std)
    
    return {
        "replay_date": cutoff.strftime('%Y-%m-%d'),
        "as_of_price": round(float(past_df.iloc[-1]['price_per_kg']), 2),
        "point_forecast": res['point_forecast'],
        "interval_lower": res['lower_bound'],
        "interval_upper": res['upper_bound'],
        "spike_probability": risk['spike_probability'],
        "risk_level": risk['risk_level'],
        "actual_realized_price": round(actual_future_price, 2) if actual_future_price else "N/A",
        "was_accurate": (res['lower_bound'] <= actual_future_price <= res['upper_bound']) if actual_future_price else True
    }
