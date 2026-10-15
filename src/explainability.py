import shap
import pandas as pd
import numpy as np
from typing import List, Dict, Any

class ModelExplainer:
    """
    Translates TreeSHAP local attribution values into human-readable policy factors.
    """
    def __init__(self, forecaster, horizon: int = 7):
        self.model = forecaster.models[horizon]
        self.explainer = shap.TreeExplainer(self.model)
        self.feature_names = forecaster.feature_names
        
    def explain_instance(self, X_instance: pd.DataFrame, top_k: int = 4) -> List[Dict[str, Any]]:
        shap_values = self.explainer.shap_values(X_instance)
        sv = shap_values[0]
        
        feature_impacts = []
        for feat_name, impact, val in zip(self.feature_names, sv, X_instance.iloc[0].values):
            feature_impacts.append({
                "feature": feat_name,
                "impact": float(impact),
                "abs_impact": abs(float(impact)),
                "actual_value": float(val),
                "policy_driver": self._map_to_policy_language(feat_name, impact, val)
            })
            
        feature_impacts = sorted(feature_impacts, key=lambda x: x['abs_impact'], reverse=True)
        return feature_impacts[:top_k]

    def _map_to_policy_language(self, feat: str, impact: float, val: float) -> str:
        direction = "upward pressure" if impact > 0 else "downward pressure"
        if "arrival" in feat:
            return f"Mandi supply level ({feat}: {val:.1f}) is exerting {direction} on retail rates."
        elif "rainfall" in feat:
            return f"Recent precipitation anomaly ({val:.1f} mm) is influencing supply continuity ({direction})."
        elif "momentum" in feat:
            return f"Wholesale price velocity ({val * 100:.1f}%) is driving short-term {direction}."
        elif "lag" in feat:
            return f"Historical baseline price point (₹{val:.1f}/kg) is anchoring the forecast ({direction})."
        elif "month" in feat or "day" in feat:
            return f"Seasonal agricultural harvest cycle is creating natural {direction}."
        else:
            return f"Market technical indicator '{feat}' contributed {impact:+.2f} ₹/kg to prediction."
