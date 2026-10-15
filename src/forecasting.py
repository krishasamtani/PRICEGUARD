import xgboost as xgb
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
from sklearn.metrics import mean_absolute_error, mean_squared_error

class MultiHorizonForecaster:
    """
    Direct Multi-Horizon Forecasting Engine using tuned Gradient Boosted Trees.
    """
    def __init__(self, horizons=[7, 14]):
        self.horizons = horizons
        self.models = {}
        self.feature_names = []
        self.metrics = {}
        
    def fit(self, df_featured: pd.DataFrame, feature_builder_func) -> Dict[int, Dict[str, float]]:
        self.metrics = {}
        for h in self.horizons:
            X, y, features = feature_builder_func(df_featured, horizon=h)
            self.feature_names = features
            
            # Time-based train-test split (85% train, 15% validation)
            if len(X) <= 2:
                X_train, y_train = X, y
                X_val, y_val = X, y
            else:
                split_idx = max(min(int(len(X) * 0.85), len(X) - 1), 1)
                X_train, y_train = X.iloc[:split_idx], y.iloc[:split_idx]
                X_val, y_val = X.iloc[split_idx:], y.iloc[split_idx:]
            
            model = xgb.XGBRegressor(
                n_estimators=180,
                max_depth=5,
                learning_rate=0.04,
                subsample=0.85,
                colsample_bytree=0.85,
                random_state=42,
                n_jobs=-1
            )
            model.fit(X_train, y_train)
            self.models[h] = model
            
            # Validation metrics
            preds = model.predict(X_val)
            mae = mean_absolute_error(y_val, preds)
            rmse = np.sqrt(mean_squared_error(y_val, preds))
            smape = 100 * np.mean(2 * np.abs(preds - y_val) / (np.abs(preds) + np.abs(y_val) + 1e-5))
            
            self.metrics[h] = {
                "MAE": round(float(mae), 3),
                "RMSE": round(float(rmse), 3),
                "sMAPE": round(float(smape), 2)
            }
        return self.metrics

    def predict_point(self, X_latest: pd.DataFrame) -> Dict[int, float]:
        forecasts = {}
        for h, model in self.models.items():
            preds = model.predict(X_latest)
            forecasts[h] = float(preds[0])
        return forecasts
