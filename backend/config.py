import os
from pathlib import Path
import yaml
from typing import List, Dict, Any

# Root directory of the PRICEGUARD project
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config" / "config.yaml"
DATA_RAW_DIR = BASE_DIR / "data" / "raw"

class Settings:
    PROJECT_NAME: str = "PRICEGUARD API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DESCRIPTION: str = (
        "Enterprise RESTful Price Intelligence & Buffer Stock Decision Support System (DSS) "
        "designed for Department of Consumer Affairs (Govt. of India)."
    )
    
    # Allowed CORS Origins
    CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:8501",  # Streamlit default
        "http://localhost:3000",  # React default
        "http://localhost:5173",  # Vite default
        "http://127.0.0.1:8501",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "*"
    ]
    
    # Defaults
    COMMODITIES: List[str] = ["Onion", "Tur"]
    HORIZONS: List[int] = [7, 14]
    CONFIDENCE_LEVEL: float = 0.90
    ALPHA: float = 0.10
    DEFAULT_BUFFER_STOCK: float = 50000.0
    DEFAULT_ELASTICITY: float = -0.18
    HOLDING_COST_PER_MT: float = 450.0
    LOGISTICS_COST_PER_MT: float = 850.0

    def __init__(self):
        if CONFIG_PATH.exists():
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    cfg = yaml.safe_load(f) or {}
                if "system" in cfg:
                    self.PROJECT_NAME = cfg["system"].get("app_name", self.PROJECT_NAME)
                    self.VERSION = cfg["system"].get("version", self.VERSION)
                if "commodities" in cfg:
                    self.COMMODITIES = cfg.get("commodities", self.COMMODITIES)
                if "conformal" in cfg:
                    self.CONFIDENCE_LEVEL = cfg["conformal"].get("confidence_level", self.CONFIDENCE_LEVEL)
                    self.ALPHA = cfg["conformal"].get("alpha", self.ALPHA)
                if "simulation" in cfg:
                    sim = cfg["simulation"]
                    self.DEFAULT_BUFFER_STOCK = sim.get("default_buffer_stock", self.DEFAULT_BUFFER_STOCK)
                    self.DEFAULT_ELASTICITY = sim.get("default_elasticity", self.DEFAULT_ELASTICITY)
                    self.HOLDING_COST_PER_MT = sim.get("holding_cost_per_mt", self.HOLDING_COST_PER_MT)
                    self.LOGISTICS_COST_PER_MT = sim.get("logistics_cost_per_mt", self.LOGISTICS_COST_PER_MT)
            except Exception as e:
                print(f"[CONFIG WARNING] Could not load yaml config: {e}. Using built-in defaults.")

settings = Settings()
