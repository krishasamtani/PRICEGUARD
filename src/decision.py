import pandas as pd
from typing import Dict, Any

def evaluate_optimal_policy(sim_df: pd.DataFrame, risk_level: str) -> Dict[str, Any]:
    """
    Decision Support Heuristic:
    Balances Price Stabilization vs Buffer Conservation vs Fiscal Expenditure.
    """
    if risk_level == "LOW":
        recommended = sim_df.iloc[0]
        rationale = "Market is in natural equilibrium. Retain buffer stock for future seasonal volatility."
    elif risk_level == "MODERATE":
        recommended = sim_df.iloc[1] # 5k MT
        rationale = "Targeted open-market sale stabilizes spot volatility without depleting core reserves."
    elif risk_level in ["HIGH", "CRITICAL"]:
        # Choose 10k or 20k MT based on remaining buffer ratio
        recommended = sim_df.iloc[2] if sim_df.iloc[2]["Buffer Remaining (MT)"] > 15000 else sim_df.iloc[1]
        rationale = "Strategic liquidation immediately checks speculative hoarding while preserving critical floor reserves."
    else:
        recommended = sim_df.iloc[1]
        rationale = "Balanced supply injection recommended."
        
    return {
        "recommended_scenario": recommended["Scenario"],
        "release_mt": recommended["Release Volume (MT)"],
        "target_price": recommended["Simulated Price (₹/kg)"],
        "expected_drop": recommended["Price Reduction (₹/kg)"],
        "buffer_retained": recommended["Buffer Remaining (MT)"],
        "estimated_budget_lakhs": recommended["Intervention Cost (₹ Lakhs)"],
        "policymaker_rationale": rationale
    }
