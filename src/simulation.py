import numpy as np
import pandas as pd
from typing import Dict, List, Any

def run_intervention_simulation(
    current_price: float,
    forecast_price: float,
    recent_daily_arrivals: float,
    buffer_stock_available: float,
    elasticity: float = -0.18,
    holding_cost: float = 450.0,
    transport_cost: float = 850.0
) -> pd.DataFrame:
    """
    Scenario Sensitivity Simulator:
    Estimates market price equilibrium under varying buffer stock liquidation quotas.
    
    Formula:
      Delta Price % = Elasticity * (Intervention MT / Weekly Mandi Supply MT)
    """
    scenarios = [
        {"name": "No Intervention", "qty_mt": 0.0},
        {"name": "Targeted Release (5k MT)", "qty_mt": min(5000.0, buffer_stock_available)},
        {"name": "Strategic Release (10k MT)", "qty_mt": min(10000.0, buffer_stock_available)},
        {"name": "Aggressive Release (20k MT)", "qty_mt": min(20000.0, buffer_stock_available)}
    ]
    
    baseline_weekly_supply = max(recent_daily_arrivals * 7.0, 1000.0)
    results = []
    
    for sc in scenarios:
        qty = sc["qty_mt"]
        shock_ratio = qty / baseline_weekly_supply
        price_drop_pct = elasticity * shock_ratio
        
        simulated_price = forecast_price * (1.0 + price_drop_pct)
        simulated_price = max(simulated_price, current_price * 0.65) # Floor at realistic production cost
        
        buffer_remaining = buffer_stock_available - qty
        cost_lakhs = (qty * (transport_cost + holding_cost)) / 100000.0
        
        price_drop_inr = forecast_price - simulated_price
        
        results.append({
            "Scenario": sc["name"],
            "Release Volume (MT)": int(qty),
            "Simulated Price (₹/kg)": round(simulated_price, 2),
            "Price Reduction (₹/kg)": round(price_drop_inr, 2),
            "Buffer Remaining (MT)": int(buffer_remaining),
            "Intervention Cost (₹ Lakhs)": round(cost_lakhs, 2),
            "Market Risk Post-Release": "LOW" if simulated_price <= current_price * 1.08 else ("MODERATE" if simulated_price <= current_price * 1.20 else "HIGH")
        })
        
    return pd.DataFrame(results)
