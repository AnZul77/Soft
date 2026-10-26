import pytest
from app.models.order import OrderStatus

@pytest.fixture
def auth_headers(client):
    client.post("/api/v1/auth/register", json={
        "email": "audit_tester@example.com",
        "password": "pass",
        "full_name": "Audit Tester"
    })
    res = client.post("/api/v1/auth/login-json", json={
        "email": "audit_tester@example.com",
        "password": "pass"
    })
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_market_sell_committed_limit_shares_invariant(client, auth_headers):
    # Create virtual portfolio
    port_res = client.post("/api/v1/portfolios/", json={
        "name": "Limit Sell Invariant Portfolio",
        "type": "VIRTUAL_TRADING",
        "initial_cash": 100000.0
    }, headers=auth_headers)
    port_id = port_res.json()["id"]

    # Buy 20 shares of NVDA
    client.post(f"/api/v1/trading/{port_id}/orders", json={
        "ticker": "NVDA", "side": "BUY", "type": "MARKET", "quantity": 20.0
    }, headers=auth_headers)

    # Place a LIMIT SELL order for 15 shares of NVDA at a high price ($300.00)
    limit_sell = client.post(f"/api/v1/trading/{port_id}/orders", json={
        "ticker": "NVDA", "side": "SELL", "type": "LIMIT", "quantity": 15.0, "limit_price": 300.00
    }, headers=auth_headers)
    assert limit_sell.status_code == 201
    assert limit_sell.json()["status"] == "PENDING"

    # Now attempt a MARKET SELL of 10 shares: holding is 20, but 15 are committed, only 5 available!
    # This MUST be rejected because available (5) < requested (10)
    market_sell_fail = client.post(f"/api/v1/trading/{port_id}/orders", json={
        "ticker": "NVDA", "side": "SELL", "type": "MARKET", "quantity": 10.0
    }, headers=auth_headers)
    assert market_sell_fail.status_code == 400
    assert "Insufficient shares" in market_sell_fail.json()["detail"]

    # Market sell of 5 shares should succeed
    market_sell_ok = client.post(f"/api/v1/trading/{port_id}/orders", json={
        "ticker": "NVDA", "side": "SELL", "type": "MARKET", "quantity": 5.0
    }, headers=auth_headers)
    assert market_sell_ok.status_code == 201
    assert market_sell_ok.json()["status"] == "FILLED"

def test_portfolio_rename_soft_delete_and_ledger_preservation(client, auth_headers):
    # 1. Create portfolio
    port_res = client.post("/api/v1/portfolios/", json={
        "name": "Original Name",
        "type": "VIRTUAL_TRADING",
        "initial_cash": 50000.0
    }, headers=auth_headers)
    port_id = port_res.json()["id"]

    # 2. Rename portfolio via PUT
    rename_res = client.put(f"/api/v1/portfolios/{port_id}", json={
        "name": "Renamed Alpha Strategy"
    }, headers=auth_headers)
    assert rename_res.status_code == 200
    assert rename_res.json()["name"] == "Renamed Alpha Strategy"

    # 3. Place an order so orders & cash transactions exist
    order_res = client.post(f"/api/v1/trading/{port_id}/orders", json={
        "ticker": "AAPL", "side": "BUY", "type": "MARKET", "quantity": 10.0
    }, headers=auth_headers)
    assert order_res.status_code == 201

    # 4. Soft delete portfolio
    del_res = client.delete(f"/api/v1/portfolios/{port_id}", headers=auth_headers)
    assert del_res.status_code == 204

    # 5. List portfolios: should not include deleted portfolio
    list_res = client.get("/api/v1/portfolios/", headers=auth_headers)
    assert list_res.status_code == 200
    assert not any(p["id"] == port_id for p in list_res.json())

    # 6. Check audit log for deletion event
    audit_res = client.get("/api/v1/auth/audit-logs", headers=auth_headers)
    assert audit_res.status_code == 200
    actions = [a["action"] for a in audit_res.json()]
    assert "PORTFOLIO_DELETED" in actions
    assert "PORTFOLIO_UPDATED" in actions

def test_watchlists_crud(client, auth_headers):
    # 1. Create watchlist
    create_res = client.post("/api/v1/watchlists/", json={
        "name": "Tech Titans",
        "description": "High conviction semiconductor & AI stocks"
    }, headers=auth_headers)
    assert create_res.status_code == 201
    wl_id = create_res.json()["id"]
    assert create_res.json()["name"] == "Tech Titans"

    # 2. Add items to watchlist
    add_nvda = client.post(f"/api/v1/watchlists/{wl_id}/items", json={
        "ticker": "NVDA", "notes": "Leader in GPU acceleration", "target_price": 140.0
    }, headers=auth_headers)
    assert add_nvda.status_code == 201
    assert add_nvda.json()["ticker"] == "NVDA"
    assert add_nvda.json()["current_price"] is not None

    add_tsmc = client.post(f"/api/v1/watchlists/{wl_id}/items", json={
        "ticker": "TSMC", "notes": "Sole foundry for Blackwell"
    }, headers=auth_headers)
    assert add_tsmc.status_code == 201

    # Duplicate check
    dup_res = client.post(f"/api/v1/watchlists/{wl_id}/items", json={
        "ticker": "NVDA"
    }, headers=auth_headers)
    assert dup_res.status_code == 400

    # 3. Retrieve watchlist with enriched quotes
    get_res = client.get(f"/api/v1/watchlists/{wl_id}", headers=auth_headers)
    assert get_res.status_code == 200
    assert len(get_res.json()["items"]) == 2

    # 4. Remove item
    item_id = add_nvda.json()["id"]
    del_item = client.delete(f"/api/v1/watchlists/{wl_id}/items/{item_id}", headers=auth_headers)
    assert del_item.status_code == 204

    after_del = client.get(f"/api/v1/watchlists/{wl_id}", headers=auth_headers)
    assert len(after_del.json()["items"]) == 1

def test_user_profile_preferences(client, auth_headers):
    # 1. Get profile
    prof_res = client.get("/api/v1/auth/profile", headers=auth_headers)
    assert prof_res.status_code == 200
    data = prof_res.json()
    assert "risk_tolerance" in data
    assert "investment_horizon" in data

    # 2. Update profile
    upd_res = client.put("/api/v1/auth/profile", json={
        "risk_tolerance": "AGGRESSIVE",
        "investment_horizon": "LONG_TERM",
        "bio": "Quantitative investor specializing in hardware and AI supply chains."
    }, headers=auth_headers)
    assert upd_res.status_code == 200
    updated = upd_res.json()
    assert updated["risk_tolerance"] == "AGGRESSIVE"
    assert updated["investment_horizon"] == "LONG_TERM"
    assert "Quantitative investor" in updated["bio"]

def test_price_history_and_extended_lookup(client):
    # 1. Seed stock history
    hist_res = client.get("/api/v1/market/history/NVDA?period=30d")
    assert hist_res.status_code == 200
    data = hist_res.json()
    assert data["ticker"] == "NVDA"
    assert len(data["candles"]) == 30
    c0 = data["candles"][0]
    assert "open" in c0 and "close" in c0 and "high" in c0 and "low" in c0

    # 2. Extended symbol lookup beyond 8 seed stocks (e.g. AMZN or GOOGL)
    amzn_quote = client.get("/api/v1/market/quotes/AMZN")
    assert amzn_quote.status_code == 200
    assert amzn_quote.json()["price"] > 0

    # 3. Dynamic lookup for arbitrary ticker
    custom_quote = client.get("/api/v1/market/quotes/QCOM")
    assert custom_quote.status_code == 200
    assert custom_quote.json()["ticker"] == "QCOM"

def test_alert_rules_crud(client, auth_headers):
    # 1. Create alert rule
    rule_res = client.post("/api/v1/alerts/rules", json={
        "ticker": "NVDA",
        "threshold_pct": 0.05,
        "window_minutes": 30.0
    }, headers=auth_headers)
    assert rule_res.status_code == 201
    rule_id = rule_res.json()["id"]

    # 2. List rules
    list_rules = client.get("/api/v1/alerts/rules", headers=auth_headers)
    assert list_rules.status_code == 200
    assert any(r["id"] == rule_id for r in list_rules.json())

    # 3. Update rule
    upd_rule = client.put(f"/api/v1/alerts/rules/{rule_id}", json={
        "threshold_pct": 0.06,
        "is_active": False
    }, headers=auth_headers)
    assert upd_rule.status_code == 200
    assert upd_rule.json()["threshold_pct"] == 0.06
    assert upd_rule.json()["is_active"] is False

    # 4. Delete rule
    del_rule = client.delete(f"/api/v1/alerts/rules/{rule_id}", headers=auth_headers)
    assert del_rule.status_code == 204

def test_journal_archive_toggle(client, auth_headers):
    # Create journal entry
    entry_res = client.post("/api/v1/journal/", json={
        "ticker": "AAPL",
        "thesis_title": "Services Margin Expansion",
        "thesis_content": "Services growth will offset modest iPhone hardware cycles.",
        "target_price": 260.0
    }, headers=auth_headers)
    assert entry_res.status_code == 201
    entry_id = entry_res.json()["id"]
    assert entry_res.json()["is_archived"] is False

    # Toggle archive
    arch_res = client.put(f"/api/v1/journal/{entry_id}/archive", headers=auth_headers)
    assert arch_res.status_code == 200
    assert arch_res.json()["is_archived"] is True

    # Toggle back
    unarch_res = client.put(f"/api/v1/journal/{entry_id}/archive", headers=auth_headers)
    assert unarch_res.status_code == 200
    assert unarch_res.json()["is_archived"] is False

    # Archive again to test query filtering
    client.put(f"/api/v1/journal/{entry_id}/archive", headers=auth_headers)
    
    # Query with is_archived=true
    arch_list = client.get("/api/v1/journal/?is_archived=true", headers=auth_headers)
    assert arch_list.status_code == 200
    assert any(e["id"] == entry_id for e in arch_list.json())

    # Query with is_archived=false
    active_list = client.get("/api/v1/journal/?is_archived=false", headers=auth_headers)
    assert active_list.status_code == 200
    assert not any(e["id"] == entry_id for e in active_list.json())

def test_operational_endpoints_require_authentication(client):
    # Operational endpoints MUST reject unauthenticated requests with 401
    scan_res = client.post("/api/v1/risk-anomalies/anomalies/scan")
    assert scan_res.status_code == 401

    match_res = client.post("/api/v1/trading/match-orders")
    assert match_res.status_code == 401

def test_soft_deleted_portfolio_invariants_and_pending_order_cancellation(client, auth_headers):
    # 1. Create portfolio
    port_res = client.post("/api/v1/portfolios/", json={
        "name": "To Be Deleted Fund",
        "type": "VIRTUAL_TRADING",
        "initial_cash": 10000.0
    }, headers=auth_headers)
    port_id = port_res.json()["id"]

    # 2. Place a pending Limit BUY order (TSLA limit $150, quantity 10 -> $1500 escrow)
    limit_buy = client.post(f"/api/v1/trading/{port_id}/orders", json={
        "ticker": "TSLA",
        "side": "BUY",
        "type": "LIMIT",
        "quantity": 10.0,
        "limit_price": 150.0
    }, headers=auth_headers)
    assert limit_buy.status_code == 201
    order_id = limit_buy.json()["id"]

    # Escrow is locked
    port_data = client.get(f"/api/v1/portfolios/{port_id}", headers=auth_headers).json()
    assert port_data["reserved_cash"] == 1500.0
    assert port_data["virtual_cash_balance"] == 8500.0

    # 3. Soft-delete the portfolio
    del_res = client.delete(f"/api/v1/portfolios/{port_id}", headers=auth_headers)
    assert del_res.status_code == 204

    # 4. Verify that the pending limit order was cancelled and escrow refunded
    orders = client.get(f"/api/v1/trading/{port_id}/orders", headers=auth_headers).json()
    cancelled_order = next((o for o in orders if o["id"] == order_id), None)
    assert cancelled_order is not None
    assert cancelled_order["status"] == "CANCELLED"
    assert "Cancelled due to portfolio deletion" in cancelled_order["error_reason"]

    # Inactive portfolio has cash refunded to virtual_cash_balance
    port_data_after = client.get(f"/api/v1/portfolios/{port_id}", headers=auth_headers).json()
    assert port_data_after["is_active"] is False
    assert port_data_after["reserved_cash"] == 0.0
    assert port_data_after["virtual_cash_balance"] == 10000.0

    # 5. Placing a new order on the inactive portfolio MUST fail
    fail_trade = client.post(f"/api/v1/trading/{port_id}/orders", json={
        "ticker": "NVDA", "side": "BUY", "type": "MARKET", "quantity": 5.0
    }, headers=auth_headers)
    assert fail_trade.status_code == 404

def test_limit_order_matching_logs_audit_events(client, auth_headers):
    # 1. Create portfolio
    port_res = client.post("/api/v1/portfolios/", json={
        "name": "Audit Matching Portfolio",
        "type": "VIRTUAL_TRADING",
        "initial_cash": 10000.0
    }, headers=auth_headers)
    port_id = port_res.json()["id"]

    # 2. Place limit buy for TSLA at $180
    limit_buy = client.post(f"/api/v1/trading/{port_id}/orders", json={
        "ticker": "TSLA",
        "side": "BUY",
        "type": "LIMIT",
        "quantity": 10.0,
        "limit_price": 180.0
    }, headers=auth_headers)
    assert limit_buy.status_code == 201

    # 3. Match orders via operational endpoint with auth
    match_res = client.post("/api/v1/trading/match-orders", headers=auth_headers)
    assert match_res.status_code == 200

    # 4. Check audit logs
    audit_res = client.get("/api/v1/auth/audit-logs", headers=auth_headers)
    assert audit_res.status_code == 200
    actions = [a["action"] for a in audit_res.json()]
    assert "TRADE_ORDER_PLACED" in actions

