import pytest

@pytest.fixture
def auth_headers(client):
    client.post("/api/v1/auth/register", json={"email": "risk_analyst@example.com", "password": "pass"})
    res = client.post("/api/v1/auth/login-json", json={"email": "risk_analyst@example.com", "password": "pass"})
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_valuation_stale_fallback_when_quote_missing(client, auth_headers):
    # Create manual tracking portfolio to inject arbitrary ticker
    port_res = client.post("/api/v1/portfolios/", json={
        "name": "Fallback Test Portfolio",
        "type": "MANUAL_TRACKING"
    }, headers=auth_headers)
    port_id = port_res.json()["id"]

    # Add a ticker that does not exist in live quote cache
    client.post(f"/api/v1/portfolios/{port_id}/holdings", json={
        "ticker": "OBSCURE_CO",
        "quantity": 100.0,
        "cost_basis": 42.50
    }, headers=auth_headers)

    # Fetch valuation
    val_res = client.get(f"/api/v1/portfolios/{port_id}/valuation", headers=auth_headers)
    assert val_res.status_code == 200
    data = val_res.json()
    assert len(data["holdings"]) == 1
    h = data["holdings"][0]
    assert h["ticker"] == "OBSCURE_CO"
    assert h["current_price"] == 42.50 # Fallback to cost basis
    assert h["is_stale"] is True
    assert h["price_source"] == "COST_BASIS_FALLBACK"
    assert h["market_value"] == 4250.0

def test_risk_metrics_hhi_beta_var_calculations(client, auth_headers):
    port_res = client.post("/api/v1/portfolios/", json={
        "name": "Risk Metrics Portfolio",
        "type": "VIRTUAL_TRADING",
        "initial_cash": 100000.0
    }, headers=auth_headers)
    port_id = port_res.json()["id"]

    # Buy NVDA (beta ~1.75) and AAPL (beta ~1.10)
    client.post(f"/api/v1/trading/{port_id}/orders", json={
        "ticker": "NVDA", "side": "BUY", "type": "MARKET", "quantity": 100.0
    }, headers=auth_headers)
    client.post(f"/api/v1/trading/{port_id}/orders", json={
        "ticker": "AAPL", "side": "BUY", "type": "MARKET", "quantity": 100.0
    }, headers=auth_headers)

    risk_res = client.get(f"/api/v1/risk-anomalies/portfolios/{port_id}/risk", headers=auth_headers)
    assert risk_res.status_code == 200
    risk = risk_res.json()

    assert risk["concentration_hhi"] >= 0.0
    assert risk["top_3_concentration_pct"] > 0.0
    assert risk["portfolio_beta"] > 0.0
    assert risk["annualized_volatility"] > 0.0
    assert risk["value_at_risk_95_1d"] > 0.0
    assert risk["benchmark_ticker"] == "SPY"

def test_anomaly_injection_and_affected_portfolio_detection(client, auth_headers):
    port_res = client.post("/api/v1/portfolios/", json={
        "name": "Anomaly Target Portfolio",
        "type": "VIRTUAL_TRADING",
        "initial_cash": 100000.0
    }, headers=auth_headers)
    port_id = port_res.json()["id"]

    # Buy 150 shares of TSMC
    client.post(f"/api/v1/trading/{port_id}/orders", json={
        "ticker": "TSMC", "side": "BUY", "type": "MARKET", "quantity": 150.0
    }, headers=auth_headers)

    # 1. Inject an 8.5% price drop on TSMC
    inj_res = client.post("/api/v1/market/anomalies/inject", json={
        "ticker": "TSMC",
        "price_change_pct": -0.085,
        "headline": "TSMC Fab Outage Triggers 8.5% Plunge",
        "content": "A sudden fab disruption led to major selling across semiconductor supply chains."
    })
    assert inj_res.status_code == 200
    assert inj_res.json()["ticker"] == "TSMC"

    # 2. Trigger Consolidated Anomaly Scan
    scan_res = client.post("/api/v1/risk-anomalies/anomalies/scan", headers=auth_headers)
    assert scan_res.status_code == 200
    alerts = scan_res.json()
    assert len(alerts) >= 1

    # Find the alert for our portfolio
    tsmc_alert = next((a for a in alerts if a["ticker"] == "TSMC" and a["portfolio_id"] == port_id), None)
    assert tsmc_alert is not None
    assert tsmc_alert["event_type"] == "PRICE_DROP"
    assert tsmc_alert["portfolio_exposure_pct"] > 0.0
    assert tsmc_alert["status"] == "DELIVERED"

    # 3. Read alerts endpoint
    user_alerts = client.get("/api/v1/risk-anomalies/alerts", headers=auth_headers).json()
    assert len(user_alerts) >= 1

    # 4. Mark alert as READ
    read_res = client.put(f"/api/v1/risk-anomalies/alerts/{tsmc_alert['id']}/read", headers=auth_headers)
    assert read_res.status_code == 200
    assert read_res.json()["status"] == "READ"
