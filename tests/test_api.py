import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_check():
    """Test health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "Onion" in data["active_commodities"]

def test_metadata():
    """Test system metadata endpoint."""
    response = client.get("/api/v1/metadata")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "supported_horizons" in data["data"]

def test_data_summary():
    """Test market data summary for Onion."""
    response = client.get("/api/v1/data/summary?commodity=Onion")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "latest_spot_price" in data["data"]
    assert data["data"]["total_records"] > 0

def test_data_history():
    """Test historical time series retrieval."""
    response = client.get("/api/v1/data/history?commodity=Onion&days=14")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) == 14

def test_forecast():
    """Test multi-horizon forecast with conformal prediction intervals."""
    response = client.get("/api/v1/forecast?commodity=Onion")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    forecast_data = data["data"]
    assert "7" in forecast_data["intervals"]
    h7 = forecast_data["intervals"]["7"]
    assert h7["point_forecast"] > 0
    assert h7["lower_bound"] <= h7["upper_bound"]
    assert "MAE" in forecast_data["metrics"]["7"]

def test_risk_evaluate():
    """Test market spike risk scoring."""
    response = client.get("/api/v1/risk/evaluate?commodity=Onion")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    risk = data["data"]
    assert risk["risk_level"] in ["LOW", "MODERATE", "HIGH", "CRITICAL"]
    assert 0 <= risk["spike_probability"] <= 100

def test_explainability():
    """Test TreeSHAP feature attributions."""
    response = client.get("/api/v1/explain?commodity=Onion&horizon=7&top_k=4")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    explain = data["data"]
    assert len(explain["top_drivers"]) > 0
    assert "policy_driver" in explain["top_drivers"][0]

def test_geography():
    """Test geographic mandi spatial matrix."""
    response = client.get("/api/v1/geography/mandis?commodity=Onion")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    geo = data["data"]
    assert geo["total_reporting_mandis"] > 0
    assert len(geo["mandis"]) > 0

def test_simulation_get_and_post():
    """Test buffer stock simulation via GET and POST."""
    # GET
    res_get = client.get("/api/v1/simulation/buffer-intervention?commodity=Onion&buffer_stock_available=50000")
    assert res_get.status_code == 200
    assert len(res_get.json()["data"]["scenarios"]) == 4

    # POST
    payload = {
        "commodity": "Onion",
        "buffer_stock_available": 60000,
        "elasticity": -0.18,
        "holding_cost_per_mt": 450.0,
        "transport_cost_per_mt": 850.0
    }
    res_post = client.post("/api/v1/simulation/buffer-intervention", json=payload)
    assert res_post.status_code == 200
    assert res_post.json()["data"]["available_buffer_mt"] == 60000

def test_decision_recommend():
    """Test optimal policy decision recommendation."""
    response = client.get("/api/v1/decision/recommend?commodity=Onion")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    rec = data["data"]
    assert "recommended_scenario" in rec
    assert rec["release_mt"] >= 0

def test_crisis_replay():
    """Test historical crisis replay."""
    # Fetch valid date from history that has at least 25 historical days
    hist = client.get("/api/v1/data/history?commodity=Onion&days=60").json()["data"]
    test_date = hist[-5]["date"] # Safe replay date with plenty of historical records

    response = client.post("/api/v1/replay/crisis", json={
        "commodity": "Onion",
        "replay_date": test_date,
        "horizon": 7
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "point_forecast" in data["data"]
    assert "was_accurate" in data["data"]

def test_report_generation_and_download():
    """Test briefing memo generation and text download."""
    # GET memo
    res_memo = client.get("/api/v1/report/briefing?commodity=Onion")
    assert res_memo.status_code == 200
    assert "DEPARTMENT OF CONSUMER AFFAIRS" in res_memo.json()["data"]["report_text"]

    # Download stream
    res_dl = client.get("/api/v1/report/download?commodity=Onion")
    assert res_dl.status_code == 200
    assert "attachment;" in res_dl.headers.get("content-disposition", "")
    assert b"DEPARTMENT OF CONSUMER AFFAIRS" in res_dl.content

def test_openapi_schema():
    """Test OpenAPI schema generation."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "paths" in schema
    assert "/api/v1/forecast" in schema["paths"]
