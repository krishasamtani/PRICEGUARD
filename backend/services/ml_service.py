import os
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple, List, Optional
import pandas as pd
import numpy as np

from src.ingestion import load_data
from src.preprocessing import clean_and_normalize
from src.features import engineer_features, build_forecasting_dataset
from src.forecasting import MultiHorizonForecaster
from src.uncertainty import SplitConformalCalibrator
from src.risk import compute_spike_risk
from src.explainability import ModelExplainer
from src.simulation import run_intervention_simulation
from src.decision import evaluate_optimal_policy
from src.historical_replay import run_historical_crisis_replay
from src.reporting import generate_executive_brief
from backend.config import settings, DATA_RAW_DIR

class PRICEGUARDMLService:
    """
    Centralized, thread-safe Service Orchestrator for the PRICEGUARD Decision Support System.
    Caches processed features, trained XGBoost multi-horizon models, and conformal quantiles.
    """
    def __init__(self):
        self._lock = threading.Lock()
        self._cache: Dict[str, Dict[str, Any]] = {}
        
    def _get_cache_key(self, commodity: str, force_demo: bool) -> str:
        return f"{commodity.lower()}_{'demo' if force_demo else 'live'}"

    def get_pipeline_data(self, commodity: str = "Onion", force_demo: bool = False) -> Tuple[pd.DataFrame, bool]:
        """Loads and pre-processes features with caching."""
        cache_key = self._get_cache_key(commodity, force_demo)
        with self._lock:
            if cache_key in self._cache and "df_feat" in self._cache[cache_key]:
                return self._cache[cache_key]["df_feat"], self._cache[cache_key]["is_demo"]
        
        raw_df, is_demo = load_data(commodity=commodity, raw_data_dir=str(DATA_RAW_DIR), force_demo=force_demo)
        clean_df = clean_and_normalize(raw_df)
        feat_df = engineer_features(clean_df)
        
        with self._lock:
            if cache_key not in self._cache:
                self._cache[cache_key] = {}
            self._cache[cache_key]["df_feat"] = feat_df
            self._cache[cache_key]["is_demo"] = is_demo
            
        return feat_df, is_demo

    def get_trained_models(self, commodity: str = "Onion", force_demo: bool = False) -> Tuple[MultiHorizonForecaster, SplitConformalCalibrator]:
        """Retrieves or trains cached XGBoost and conformal calibrators."""
        cache_key = self._get_cache_key(commodity, force_demo)
        with self._lock:
            if cache_key in self._cache and "forecaster" in self._cache[cache_key]:
                return self._cache[cache_key]["forecaster"], self._cache[cache_key]["conformal"]
                
        feat_df, is_demo = self.get_pipeline_data(commodity, force_demo)
        
        forecaster = MultiHorizonForecaster(horizons=settings.HORIZONS)
        forecaster.fit(feat_df, build_forecasting_dataset)
        
        conformal = SplitConformalCalibrator(alpha=settings.ALPHA)
        conformal.calibrate(forecaster, feat_df, build_forecasting_dataset)
        
        with self._lock:
            self._cache[cache_key]["forecaster"] = forecaster
            self._cache[cache_key]["conformal"] = conformal
            
        return forecaster, conformal

    def get_full_forecast(self, commodity: str = "Onion", force_demo: bool = False) -> Dict[str, Any]:
        """Calculates multi-horizon forecasts with conformal uncertainty bounds and metrics."""
        feat_df, is_demo = self.get_pipeline_data(commodity, force_demo)
        forecaster, conformal = self.get_trained_models(commodity, force_demo)
        
        X_latest, _, _ = build_forecasting_dataset(feat_df, horizon=7)
        latest_row = X_latest.iloc[-1:]
        
        raw_intervals = conformal.predict_intervals(forecaster, latest_row)
        current_price = float(feat_df.iloc[-1]['price_per_kg'])
        recent_arrivals = float(feat_df.iloc[-1]['arrival_qty'])
        recent_mean = float(feat_df.iloc[-1]['price_roll_mean_7'])
        recent_std = float(feat_df.iloc[-1]['price_roll_std_7'])
        as_of_date = feat_df.iloc[-1]['date'].strftime('%Y-%m-%d')
        
        # Structure intervals
        intervals_out = {}
        for h, data in raw_intervals.items():
            intervals_out[h] = {
                "horizon_days": int(h),
                "point_forecast": float(data["point_forecast"]),
                "lower_bound": float(data["lower_bound"]),
                "upper_bound": float(data["upper_bound"]),
                "interval_width": float(data["interval_width"]),
                "coverage_guarantee": data.get("coverage_guarantee", "90%")
            }
            
        # Recent 60 days history
        recent_tail = feat_df.tail(60)
        history_points = [
            {
                "date": row["date"].strftime('%Y-%m-%d'),
                "price_per_kg": round(float(row["price_per_kg"]), 2),
                "arrival_qty": round(float(row["arrival_qty"]), 2)
            }
            for _, row in recent_tail.iterrows()
        ]
        
        return {
            "commodity": commodity,
            "current_price": round(current_price, 2),
            "recent_7d_mean": round(recent_mean, 2),
            "recent_7d_std": round(recent_std, 2),
            "recent_arrivals": round(recent_arrivals, 2),
            "is_demo": is_demo,
            "as_of_date": as_of_date,
            "intervals": intervals_out,
            "metrics": forecaster.metrics,
            "recent_history": history_points
        }

    def evaluate_risk(self, commodity: str = "Onion", force_demo: bool = False) -> Dict[str, Any]:
        """Computes spike anomaly probability and risk tier."""
        forecast_data = self.get_full_forecast(commodity, force_demo)
        h7 = forecast_data["intervals"][7]
        
        risk = compute_spike_risk(
            forecast_price=h7["point_forecast"],
            upper_bound=h7["upper_bound"],
            recent_mean=forecast_data["recent_7d_mean"],
            recent_std=forecast_data["recent_7d_std"]
        )
        
        return {
            "commodity": commodity,
            "risk_level": risk["risk_level"],
            "z_score": risk["z_score"],
            "spike_probability": risk["spike_probability"],
            "badge_color": risk["badge_color"],
            "action_summary": risk["action_summary"],
            "current_price": forecast_data["current_price"],
            "forecast_price_7d": h7["point_forecast"],
            "upper_bound_7d": h7["upper_bound"],
            "recent_mean_7d": forecast_data["recent_7d_mean"]
        }

    def get_explainability(self, commodity: str = "Onion", horizon: int = 7, top_k: int = 4, force_demo: bool = False) -> Dict[str, Any]:
        """Computes TreeSHAP local attribution drivers for recent prediction."""
        feat_df, _ = self.get_pipeline_data(commodity, force_demo)
        forecaster, _ = self.get_trained_models(commodity, force_demo)
        
        X_latest, _, _ = build_forecasting_dataset(feat_df, horizon=horizon)
        latest_row = X_latest.iloc[-1:]
        
        explainer = ModelExplainer(forecaster, horizon=horizon)
        top_drivers = explainer.explain_instance(latest_row, top_k=top_k)
        
        return {
            "commodity": commodity,
            "horizon": horizon,
            "top_drivers": top_drivers,
            "scientific_guardrail": (
                "Feature attributions represent model associations and relative weight contributions, "
                "not counterfactual physical causation."
            )
        }

    def get_geography(self, commodity: str = "Onion", force_demo: bool = False) -> Dict[str, Any]:
        """Returns geographic mandi spatial distribution and vulnerability matrix."""
        forecast_data = self.get_full_forecast(commodity, force_demo)
        current_price = forecast_data["current_price"]
        
        # Coordinated real & representative hub mandis
        hubs = [
            {"mandi_name": "Lasalgaon (MH)", "state": "Maharashtra", "lat": 20.1462, "lon": 74.2285, "factor": 1.02, "qty": 720, "vuln": "HIGH"},
            {"mandi_name": "Nashik (MH)", "state": "Maharashtra", "lat": 19.9975, "lon": 73.7898, "factor": 0.98, "qty": 640, "vuln": "HIGH"},
            {"mandi_name": "Azadpur (DL)", "state": "Delhi", "lat": 28.7165, "lon": 77.1728, "factor": 1.08, "qty": 850, "vuln": "HIGH"},
            {"mandi_name": "Solapur (MH)", "state": "Maharashtra", "lat": 17.6599, "lon": 75.9064, "factor": 0.95, "qty": 410, "vuln": "MODERATE"},
            {"mandi_name": "Kalaburagi (KA)", "state": "Karnataka", "lat": 17.3297, "lon": 76.8343, "factor": 1.01, "qty": 320, "vuln": "LOW"},
            {"mandi_name": "Latur (MH)", "state": "Maharashtra", "lat": 18.4088, "lon": 76.5604, "factor": 0.99, "qty": 530, "vuln": "MODERATE"},
            {"mandi_name": "Indore (MP)", "state": "Madhya Pradesh", "lat": 22.7196, "lon": 75.8577, "factor": 1.04, "qty": 480, "vuln": "MODERATE"}
        ]
        
        mandis = []
        high_risk_count = 0
        for h in hubs:
            spot = round(current_price * h["factor"], 2)
            if h["vuln"] == "HIGH":
                high_risk_count += 1
            mandis.append({
                "mandi_name": h["mandi_name"],
                "state": h["state"],
                "latitude": h["lat"],
                "longitude": h["lon"],
                "spot_rate": spot,
                "arrival_tonnes": float(h["qty"]),
                "vulnerability_tier": h["vuln"]
            })
            
        return {
            "commodity": commodity,
            "mandis": mandis,
            "total_reporting_mandis": len(mandis),
            "high_vulnerability_count": high_risk_count
        }

    def simulate_buffer(
        self,
        commodity: str = "Onion",
        buffer_stock_available: float = 50000.0,
        elasticity: float = -0.18,
        holding_cost: float = 450.0,
        transport_cost: float = 850.0,
        override_current_price: Optional[float] = None,
        override_forecast_price: Optional[float] = None,
        override_daily_arrivals: Optional[float] = None,
        force_demo: bool = False
    ) -> Dict[str, Any]:
        """Runs scenario sensitivity simulation under price elasticity."""
        forecast_data = self.get_full_forecast(commodity, force_demo)
        
        current_p = override_current_price if override_current_price is not None else forecast_data["current_price"]
        forecast_p = override_forecast_price if override_forecast_price is not None else forecast_data["intervals"][7]["point_forecast"]
        arrivals = override_daily_arrivals if override_daily_arrivals is not None else forecast_data["recent_arrivals"]
        
        sim_df = run_intervention_simulation(
            current_price=current_p,
            forecast_price=forecast_p,
            recent_daily_arrivals=arrivals,
            buffer_stock_available=buffer_stock_available,
            elasticity=elasticity,
            holding_cost=holding_cost,
            transport_cost=transport_cost
        )
        
        scenarios = []
        for _, row in sim_df.iterrows():
            scenarios.append({
                "scenario": row["Scenario"],
                "release_volume_mt": int(row["Release Volume (MT)"]),
                "simulated_price": float(row["Simulated Price (₹/kg)"]),
                "price_reduction": float(row["Price Reduction (₹/kg)"]),
                "buffer_remaining_mt": int(row["Buffer Remaining (MT)"]),
                "intervention_cost_lakhs": float(row["Intervention Cost (₹ Lakhs)"]),
                "market_risk_post_release": str(row["Market Risk Post-Release"])
            })
            
        return {
            "commodity": commodity,
            "baseline_spot_price": current_p,
            "baseline_forecast_price": forecast_p,
            "available_buffer_mt": buffer_stock_available,
            "elasticity_applied": elasticity,
            "scenarios": scenarios
        }

    def recommend_decision(
        self,
        commodity: str = "Onion",
        buffer_stock_available: float = 50000.0,
        elasticity: float = -0.18,
        force_demo: bool = False
    ) -> Dict[str, Any]:
        """Generates optimal policy recommendation based on risk tier and simulated scenarios."""
        sim_res = self.simulate_buffer(
            commodity=commodity,
            buffer_stock_available=buffer_stock_available,
            elasticity=elasticity,
            force_demo=force_demo
        )
        risk_res = self.evaluate_risk(commodity=commodity, force_demo=force_demo)
        
        # Convert back to dataframe format expected by decision heuristic
        sim_df = pd.DataFrame([
            {
                "Scenario": s["scenario"],
                "Release Volume (MT)": s["release_volume_mt"],
                "Simulated Price (₹/kg)": s["simulated_price"],
                "Price Reduction (₹/kg)": s["price_reduction"],
                "Buffer Remaining (MT)": s["buffer_remaining_mt"],
                "Intervention Cost (₹ Lakhs)": s["intervention_cost_lakhs"],
                "Market Risk Post-Release": s["market_risk_post_release"]
            }
            for s in sim_res["scenarios"]
        ])
        
        policy = evaluate_optimal_policy(sim_df, risk_res["risk_level"])
        
        return {
            "commodity": commodity,
            "assessed_risk_level": risk_res["risk_level"],
            "recommended_scenario": policy["recommended_scenario"],
            "release_mt": policy["release_mt"],
            "target_price": policy["target_price"],
            "expected_drop": policy["expected_drop"],
            "buffer_retained": policy["buffer_retained"],
            "estimated_budget_lakhs": policy["estimated_budget_lakhs"],
            "policymaker_rationale": policy["policymaker_rationale"]
        }

    def replay_crisis(self, commodity: str = "Onion", replay_date: str = "2026-01-20", horizon: int = 7, force_demo: bool = False) -> Dict[str, Any]:
        """Executes historical backtest masking subsequent ground truth."""
        feat_df, _ = self.get_pipeline_data(commodity, force_demo)
        rep_res = run_historical_crisis_replay(feat_df, replay_date=replay_date, horizon=horizon)
        
        actual_price = rep_res["actual_realized_price"]
        actual_float = float(actual_price) if actual_price is not None and str(actual_price) != "N/A" else None
        
        return {
            "commodity": commodity,
            "replay_date": rep_res["replay_date"],
            "as_of_price": rep_res["as_of_price"],
            "point_forecast": rep_res["point_forecast"],
            "interval_lower": rep_res["interval_lower"],
            "interval_upper": rep_res["interval_upper"],
            "spike_probability": rep_res["spike_probability"],
            "risk_level": rep_res["risk_level"],
            "actual_realized_price": actual_float,
            "was_accurate": rep_res["was_accurate"]
        }

    def generate_report(self, commodity: str = "Onion", buffer_stock_available: float = 50000.0, force_demo: bool = False) -> Dict[str, Any]:
        """Generates executive briefing memo."""
        feat_df, is_demo = self.get_pipeline_data(commodity, force_demo)
        forecast_data = self.get_full_forecast(commodity, force_demo)
        risk_res = self.evaluate_risk(commodity, force_demo)
        explain_res = self.get_explainability(commodity, horizon=7, top_k=4, force_demo=force_demo)
        decision_res = self.recommend_decision(commodity, buffer_stock_available=buffer_stock_available, force_demo=force_demo)
        
        policy_rep = {
            "recommended_scenario": decision_res["recommended_scenario"],
            "release_mt": decision_res["release_mt"],
            "target_price": decision_res["target_price"],
            "expected_drop": decision_res["expected_drop"],
            "buffer_retained": decision_res["buffer_retained"],
            "estimated_budget_lakhs": decision_res["estimated_budget_lakhs"],
            "policymaker_rationale": decision_res["policymaker_rationale"]
        }
        
        report_text = generate_executive_brief(
            commodity=commodity,
            current_price=forecast_data["current_price"],
            intervals=forecast_data["intervals"],
            risk=risk_res,
            top_drivers=explain_res["top_drivers"],
            recommendation=policy_rep,
            is_demo=is_demo
        )
        
        return {
            "commodity": commodity,
            "generated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "report_text": report_text,
            "risk_level": risk_res["risk_level"],
            "recommended_action": risk_res["action_summary"]
        }

# Global singleton service instance
ml_service = PRICEGUARDMLService()
