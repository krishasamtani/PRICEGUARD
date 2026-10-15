import numpy as np
import pandas as pd
from typing import Tuple, Dict, Any

def compute_spike_risk(
    forecast_price: float, 
    upper_bound: float, 
    recent_mean: float, 
    recent_std: float
) -> Dict[str, Any]:
    """
    Evaluates price anomaly risk levels and empirical spike probabilities.
    """
    safe_std = max(recent_std, 1.0)
    z_score = (forecast_price - recent_mean) / safe_std
    z_upper = (upper_bound - recent_mean) / safe_std
    
    # Calculate calibrated spike probability using logistic CDF mapping
    spike_prob = 1.0 / (1.0 + np.exp(-1.8 * (z_score - 1.2)))
    spike_prob = float(np.clip(spike_prob, 0.02, 0.98))
    
    # Risk Classification
    if z_score >= 2.0 or z_upper >= 2.8:
        risk_level = "CRITICAL"
        color = "red"
        action_summary = "Emergency buffer liquidation recommended within 48-72 hours."
    elif z_score >= 1.5 or z_upper >= 2.2:
        risk_level = "HIGH"
        color = "orange"
        action_summary = "Prepare strategic procurement and market intervention notice."
    elif z_score >= 1.0:
        risk_level = "MODERATE"
        color = "yellow"
        action_summary = "Heightened monitoring of primary wholesale trading mandis."
    else:
        risk_level = "LOW"
        color = "green"
        action_summary = "Normal seasonal market price fluctuations. Maintain reserves."
        
    return {
        "z_score": round(float(z_score), 2),
        "spike_probability": round(spike_prob * 100.0, 1),
        "risk_level": risk_level,
        "badge_color": color,
        "action_summary": action_summary
    }
