import pytest

def test_complete_platform_end_to_end_user_journey(client):
    # 1. User Registration
    reg_res = client.post("/api/v1/auth/register", json={
        "email": "e2e_investor@intelligence.ai",
        "password": "SecurePassword2026!",
        "full_name": "E2E Platform Investor"
    })
    assert reg_res.status_code == 201

    # 2. Login
    login_res = client.post("/api/v1/auth/login-json", json={
        "email": "e2e_investor@intelligence.ai",
        "password": "SecurePassword2026!"
    })
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Create Virtual Portfolio
    port_res = client.post("/api/v1/portfolios/", json={
        "name": "Main Growth Strategy",
        "type": "VIRTUAL_TRADING",
        "initial_cash": 100000.0
    }, headers=headers)
    assert port_res.status_code == 201
    port_id = port_res.json()["id"]

    # 4. Place Virtual Market BUY Trades
    buy_nvda = client.post(f"/api/v1/trading/{port_id}/orders", json={
        "ticker": "NVDA", "side": "BUY", "type": "MARKET", "quantity": 100.0
    }, headers=headers)
    assert buy_nvda.status_code == 201
    assert buy_nvda.json()["status"] == "FILLED"

    buy_tsmc = client.post(f"/api/v1/trading/{port_id}/orders", json={
        "ticker": "TSMC", "side": "BUY", "type": "MARKET", "quantity": 100.0
    }, headers=headers)
    assert buy_tsmc.status_code == 201
    assert buy_tsmc.json()["status"] == "FILLED"

    # 5. Check Valuation
    val_res = client.get(f"/api/v1/portfolios/{port_id}/valuation", headers=headers)
    assert val_res.status_code == 200
    val_data = val_res.json()
    assert len(val_data["holdings"]) == 2
    assert val_data["virtual_cash_balance"] < 100000.0
    assert val_data["holdings_value"] > 0

    # 6. Check Risk Metrics
    risk_res = client.get(f"/api/v1/risk-anomalies/portfolios/{port_id}/risk", headers=headers)
    assert risk_res.status_code == 200
    risk = risk_res.json()
    assert risk["portfolio_beta"] > 0.3 # NVDA and TSMC weighted beta including cash
    assert risk["concentration_hhi"] > 0.0

    # 7. Inject Market Anomaly: 8% drop on TSMC
    inj_res = client.post("/api/v1/market/anomalies/inject", json={
        "ticker": "TSMC",
        "price_change_pct": -0.082,
        "headline": "TSMC Incurs 8.2% Intraday Drawdown",
        "content": "Power disruption in Tainan halts packaging operations, creating global semiconductor delays."
    })
    assert inj_res.status_code == 200

    # 8. Run Anomaly Scanner
    scan_res = client.post("/api/v1/risk-anomalies/anomalies/scan", headers=headers)
    assert scan_res.status_code == 200

    # 9. Verify Notification Delivered to User
    alerts_res = client.get("/api/v1/risk-anomalies/alerts", headers=headers)
    assert alerts_res.status_code == 200
    alerts = alerts_res.json()
    assert len(alerts) >= 1
    target_alert = alerts[0]
    assert target_alert["ticker"] == "TSMC"
    assert target_alert["portfolio_exposure_pct"] > 0

    # Mark alert read
    client.put(f"/api/v1/risk-anomalies/alerts/{target_alert['id']}/read", headers=headers)

    # 10. Explain Impact via RAG & Supply Chain Knowledge Graph
    explain_res = client.post("/api/v1/ai/explain-impact", json={
        "portfolio_id": port_id,
        "ticker": "TSMC",
        "event_description": "TSMC 8.2% drop from packaging disruption",
        "price_change_pct": -0.082
    }, headers=headers)
    assert explain_res.status_code == 200
    explain_data = explain_res.json()
    assert explain_data["abstention"] is False
    assert len(explain_data["evidence_citations"]) >= 1
    assert "DISCLAIMER" in explain_data["regulatory_disclaimer"]
    # Check that connected holding NVDA is identified in supply chain risk
    assert any("NVDA" in link["target_ticker"] or "NVDA" in link["source_ticker"] for link in explain_data["supply_chain_links"])

    # 11. Create Investment Journal Entry
    journal_res = client.post("/api/v1/journal/", json={
        "portfolio_id": port_id,
        "ticker": "NVDA",
        "thesis_title": "AI Hardware Supercycle",
        "thesis_content": "Datacenter transformation and Blackwell GPU ramp will sustain 65%+ gross margins for 3 years.",
        "rationale": "High switching cost and CUDA software moat.",
        "target_price": 180.0,
        "confidence_rating": 4
    }, headers=headers)
    assert journal_res.status_code == 201
    entry_id = journal_res.json()["id"]

    # 12. Run AI Thesis Reflection
    reflect_res = client.post(f"/api/v1/journal/{entry_id}/reflect", headers=headers)
    assert reflect_res.status_code == 200
    entry_updated = reflect_res.json()
    assert entry_updated["ai_reflection"] is not None
    assert "Thesis Review for NVDA" in entry_updated["ai_reflection"]
    assert "does not advise" in entry_updated["ai_reflection"]
