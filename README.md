# PRICEGUARD DSS 🛡️
**Predictive Price Intelligence & Buffer Stock Decision Support System**

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI%200.110-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit%201.32-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io)
[![XGBoost](https://img.shields.io/badge/ML%20Engine-XGBoost-EB8921?style=flat)](https://xgboost.readthedocs.io)
[![Docker](https://img.shields.io/badge/Container-Docker%20Ready-2496ED?style=flat&logo=docker&logoColor=white)](https://www.docker.com)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)

PRICEGUARD is an end-to-end Machine Learning Decision Support System (DSS) designed for the **Department of Consumer Affairs (Govt. of India)** to monitor, forecast, explain, and simulate market interventions for essential agricultural commodities like **Onion** and **Tur (Pigeon Pea)**.

---

## 🏛️ System Architecture

```text
┌──────────────────────────────────────────────────────────────────────────┐
│                             PRICEGUARD DSS                               │
└──────────────────────────────────────────────────────────────────────────┘
           │                                                │
           ▼                                                ▼
┌─────────────────────────┐                      ┌─────────────────────────┐
│   Streamlit Dashboard   │                      │   FastAPI REST Engine   │
│   (Port 8501)           │                      │   (Port 8000 /docs)     │
└──────────┬──────────────┘                      └──────────┬──────────────┘
           │                                                │
           └───────────────────────┬────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                           ML Services Layer                              │
├──────────────────────────────────────────────────────────────────────────┤
│  • Time-Series Feature Engineering (t-1 Causal Anti-Leakage)             │
│  • Multi-Horizon XGBoost Regressors (T+7 and T+14 Horizons)              │
│  • Split Conformal Prediction Intervals (MAPIE 90% Confidence Bounds)    │
│  • Local Factor Attributions (TreeSHAP Policy Translator)                │
│  • What-If Supply Elasticity Buffer Stock Simulator                      │
│  • Automated Optimal Policy Decision Heuristics                          │
│  • Historical Crisis Replay Backtesting Engine                           │
│  • Executive Situation Briefing Document Generator                       │
└──────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                              Data Sources                                │
├──────────────────────────────────────────────────────────────────────────┤
│  • Agmarknet Wholesale Mandi Prices & Daily Arrivals (Maharashtra, etc.) │
│  • NASA POWER Meteorological Weather (Precipitation, Temp, Humidity)     │
│  • Crop Production & Macro Baselines                                     │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Key Features

* **RESTful Microservice API**: Full-featured, asynchronous **FastAPI** backend with automated Swagger (`/docs`) and ReDoc (`/redoc`) API documentation.
* **Multi-Horizon Price Forecasting**: Causal lag and rolling window features fed into tuned **XGBoost** models to predict wholesale rates 7 and 14 days ahead.
* **Conformal Prediction Intervals (MAPIE)**: Distribution-free, statistically rigorous uncertainty bounds (90% CI) surrounding point forecasts.
* **Explainable AI (TreeSHAP)**: Deconstructs model decisions into plain-language policy drivers (rainfall anomalies, arrival drops, momentum).
* **What-If Buffer Simulator**: Causally projects retail price equilibrium under variable government buffer stock releases (5,000 to 20,000 MT).
* **Geographic Mandi Intelligence**: District-level spatial matrix mapping spot rates, arrival volumes, and vulnerability tiers.
* **Historical Crisis Replay**: Masks future data to backtest predictive performance during major historical market spikes.
* **Automated Situation Briefing**: Generates and downloads official executive memos ready for departmental briefings.

---

## 📁 Repository Structure

```text
PRICEGUARD/
├── backend/                       # FastAPI REST API Backend
│   ├── main.py                    # Application entrypoint & CORS middleware
│   ├── config.py                  # Environment & YAML settings
│   ├── schemas/                   # Pydantic v2 Request/Response validation models
│   │   ├── common.py
│   │   ├── forecast.py
│   │   ├── risk.py
│   │   ├── explainability.py
│   │   ├── geography.py
│   │   ├── simulation.py
│   │   ├── decision.py
│   │   ├── replay.py
│   │   └── report.py
│   ├── routers/                   # Modular REST endpoint controllers
│   │   ├── health.py              # /api/v1/health & /api/v1/metadata
│   │   ├── data.py                # /api/v1/data/summary & history
│   │   ├── forecast.py            # /api/v1/forecast
│   │   ├── risk.py                # /api/v1/risk/evaluate
│   │   ├── explainability.py      # /api/v1/explain
│   │   ├── geography.py           # /api/v1/geography/mandis
│   │   ├── simulation.py          # /api/v1/simulation/buffer-intervention
│   │   ├── decision.py            # /api/v1/decision/recommend
│   │   ├── replay.py              # /api/v1/replay/crisis
│   │   └── report.py              # /api/v1/report/briefing & download
│   └── services/                  # Business logic & cached ML model manager
│       └── ml_service.py
├── src/                           # Core ML Algorithms & Data Processing
│   ├── ingestion.py               # Agmarknet, NASA Weather & Crop data loaders
│   ├── preprocessing.py           # Data normalization, price conversion & interpolation
│   ├── features.py                # Strict t-1 causal lag/rolling feature engineering
│   ├── forecasting.py             # Multi-horizon XGBoost training & inference
│   ├── uncertainty.py             # Inductive Split Conformal Prediction engine
│   ├── risk.py                    # Anomaly Z-score & spike probability classification
│   ├── explainability.py          # TreeSHAP attribution & policy factor translator
│   ├── simulation.py              # Buffer stock intervention sensitivity simulator
│   ├── decision.py                # Optimal policy evaluation heuristics
│   ├── historical_replay.py       # Time-series masking & historical validation
│   ├── reporting.py               # Official situation report brief generator
│   └── data_generator.py          # Fallback synthetic calibrated demo generator
├── tests/                         # Automated Pytest Suite
│   └── test_api.py                # Comprehensive test coverage for all endpoints
├── config/
│   └── config.yaml                # System parameters & risk thresholds
├── data/
│   └── raw/                       # Mandi, Weather & Production CSV data
├── app.py                         # Interactive Streamlit Web Console
├── run_backend.py                 # Standalone backend server launcher (Uvicorn)
├── run_app.py                     # Unified concurrent launcher (Backend + Dashboard)
├── requirements.txt               # Project dependencies
├── Dockerfile                     # Production containerization
├── docker-compose.yml             # Multi-container orchestration
├── .gitignore                     # Git ignore rules
├── setup_git.bat                  # Windows 1-click Git initialization script
├── setup_git.ps1                  # PowerShell Git initialization script
└── GITHUB_SETUP_GUIDE.md          # Step-by-step GitHub publishing guide
```

---

## 🛠️ Installation & Quick Start

### 1. Clone or Open the Repository
```bash
cd PRICEGUARD
```

### 2. Create and Activate Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 🏃 Running the Application

### Option A: Run Full Stack (Backend + Dashboard Concurrently)
```bash
python run_app.py
```
* **FastAPI Backend**: [http://localhost:8000](http://localhost:8000)
* **Interactive Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
* **Streamlit Dashboard**: [http://localhost:8501](http://localhost:8501)

### Option B: Run FastAPI Backend Only
```bash
python run_backend.py --port 8000 --reload
```

### Option C: Run Streamlit UI Only
```bash
streamlit run app.py
```

### Option D: Run with Docker Compose
```bash
docker-compose up --build
```

---

## 📡 REST API Reference

| HTTP Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/health` | System health check and active commodity status |
| `GET` | `/api/v1/metadata` | System configurations, horizons, and risk thresholds |
| `GET` | `/api/v1/data/summary` | Record count, date range, and current market baseline |
| `GET` | `/api/v1/data/history` | Historical spot prices, arrivals, and rainfall metrics |
| `GET` | `/api/v1/forecast` | 7-day and 14-day forecasts with 90% Conformal Intervals |
| `GET` | `/api/v1/risk/evaluate` | Z-score anomaly metric, spike probability, and risk tier |
| `GET` | `/api/v1/explain` | Ranked TreeSHAP economic driving factors & policy narratives |
| `GET` | `/api/v1/geography/mandis` | Spatial wholesale mandi hub matrix and vulnerability tiers |
| `POST` | `/api/v1/simulation/buffer-intervention` | What-If simulation under varying liquidation quotas (5k-20k MT) |
| `GET` | `/api/v1/decision/recommend` | Automated optimal policy recommendation & budget estimate |
| `POST` | `/api/v1/replay/crisis` | Historical backtesting masking subsequent ground truth |
| `GET` | `/api/v1/report/briefing` | Formatted official Department Executive Situation Brief |
| `GET` | `/api/v1/report/download` | Download executive briefing as a `.txt` attachment |

### 💡 Example cURL Requests

#### 1. Get 7-Day & 14-Day Forecast with 90% Confidence Bounds
```bash
curl -X GET "http://localhost:8000/api/v1/forecast?commodity=Onion"
```

#### 2. Evaluate Spike Risk
```bash
curl -X GET "http://localhost:8000/api/v1/risk/evaluate?commodity=Onion"
```

#### 3. Run What-If Buffer Simulation (POST)
```bash
curl -X POST "http://localhost:8000/api/v1/simulation/buffer-intervention" \
     -H "Content-Type: application/json" \
     -d '{
       "commodity": "Onion",
       "buffer_stock_available": 50000,
       "elasticity": -0.18,
       "holding_cost_per_mt": 450,
       "transport_cost_per_mt": 850
     }'
```

#### 4. Download Executive Briefing Document
```bash
curl -O -J "http://localhost:8000/api/v1/report/download?commodity=Onion"
```

---

## 🧪 Automated Testing

Run the test suite with **pytest**:
```bash
pytest tests/ -v
```

---

## 🌐 Publishing to GitHub

See the detailed [GITHUB_SETUP_GUIDE.md](file:///c:/Users/AI&DS/Downloads/PRICEGUARD_UPDATED%20(1)/PRICEGUARD/GITHUB_SETUP_GUIDE.md) or run the automated script:

```cmd
setup_git.bat
```
*(Or in PowerShell: `.\setup_git.ps1`)*

---

## 🛡️ License
Designed for the Department of Consumer Affairs, Government of India.
