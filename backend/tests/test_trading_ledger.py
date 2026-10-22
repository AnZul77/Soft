import pytest

@pytest.fixture
def auth_headers(client):
    client.post("/api/v1/auth/register", json={"email": "trader@example.com", "password": "pass"})
    res = client.post("/api/v1/auth/login-json", json={"email": "trader@example.com", "password": "pass"})
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_market_buy_and_sell_with_cash_invariants(client, auth_headers):
    # 1. Create Virtual Trading Portfolio
    port_res = client.post("/api/v1/portfolios/", json={
        "name": "Trading Ledger Alpha",
        "type": "VIRTUAL_TRADING",
        "initial_cash": 100000.0
    }, headers=auth_headers)
    assert port_res.status_code == 201
    port_id = port_res.json()["id"]

    # 2. Check initial cash
    val_res = client.get(f"/api/v1/portfolios/{port_id}/valuation", headers=auth_headers)
    assert val_res.status_code == 200
    assert val_res.json()["virtual_cash_balance"] == 100000.0

    # 3. Market BUY 100 shares of NVDA
    # Assume NVDA is ~$128.50, so total cost ~$12,850
    order_res = client.post(f"/api/v1/trading/{port_id}/orders", json={
        "ticker": "NVDA",
        "side": "BUY",
        "type": "MARKET",
        "quantity": 100.0
    }, headers=auth_headers)
    assert order_res.status_code == 201
    order_data = order_res.json()
    assert order_data["status"] == "FILLED"
    exec_price = order_data["execution_price"]
    assert exec_price > 0

    # Verify cash deducted and holding created
    val_res2 = client.get(f"/api/v1/portfolios/{port_id}/valuation", headers=auth_headers)
    val_data2 = val_res2.json()
    expected_cash = round(100000.0 - (100.0 * exec_price), 2)
    assert val_data2["virtual_cash_balance"] == expected_cash
    assert len(val_data2["holdings"]) == 1
    assert val_data2["holdings"][0]["ticker"] == "NVDA"
    assert val_data2["holdings"][0]["quantity"] == 100.0

    # 4. Check Cash Transactions ledger
    tx_res = client.get(f"/api/v1/trading/{port_id}/transactions", headers=auth_headers)
    assert tx_res.status_code == 200
    txs = tx_res.json()
    # At least INITIAL_DEPOSIT and BUY_ORDER
    types = [t["transaction_type"] for t in txs]
    assert "INITIAL_DEPOSIT" in types
    assert "BUY_ORDER" in types

    # 5. INVARIANT: Attempt to BUY more than available cash -> Must fail
    huge_order = client.post(f"/api/v1/trading/{port_id}/orders", json={
        "ticker": "NVDA",
        "side": "BUY",
        "type": "MARKET",
        "quantity": 50000.0 # Would cost > $6M
    }, headers=auth_headers)
    assert huge_order.status_code == 400
    assert "Insufficient cash" in huge_order.json()["detail"]

    # 6. Market SELL 40 shares of NVDA
    sell_res = client.post(f"/api/v1/trading/{port_id}/orders", json={
        "ticker": "NVDA",
        "side": "SELL",
        "type": "MARKET",
        "quantity": 40.0
    }, headers=auth_headers)
    assert sell_res.status_code == 201
    assert sell_res.json()["status"] == "FILLED"

    # Verify holding reduced to 60 shares
    val_res3 = client.get(f"/api/v1/portfolios/{port_id}/valuation", headers=auth_headers)
    assert val_res3.json()["holdings"][0]["quantity"] == 60.0

    # 7. INVARIANT: Attempt to SELL more shares than held -> Must fail
    oversell = client.post(f"/api/v1/trading/{port_id}/orders", json={
        "ticker": "NVDA",
        "side": "SELL",
        "type": "MARKET",
        "quantity": 100.0 # Only 60 held
    }, headers=auth_headers)
    assert oversell.status_code == 400
    assert "Insufficient shares" in oversell.json()["detail"]

def test_limit_order_escrow_reservation_and_cancellation(client, auth_headers):
    port_res = client.post("/api/v1/portfolios/", json={
        "name": "Limit Escrow Portfolio",
        "type": "VIRTUAL_TRADING",
        "initial_cash": 10000.0
    }, headers=auth_headers)
    port_id = port_res.json()["id"]

    # Place a Limit BUY below market price (e.g. TSLA limit at $150 while TSLA is ~$215)
    limit_res = client.post(f"/api/v1/trading/{port_id}/orders", json={
        "ticker": "TSLA",
        "side": "BUY",
        "type": "LIMIT",
        "quantity": 10.0,
        "limit_price": 150.0 # Escrow required = $1,500
    }, headers=auth_headers)
    assert limit_res.status_code == 201
    order_data = limit_res.json()
    assert order_data["status"] == "PENDING"
    order_id = order_data["id"]

    # Check that $1,500 was moved from virtual_cash to reserved_cash
    port_view = client.get(f"/api/v1/portfolios/{port_id}", headers=auth_headers).json()
    assert port_view["virtual_cash_balance"] == 8500.0
    assert port_view["reserved_cash"] == 1500.0

    # Cancel the limit order
    cancel_res = client.post(f"/api/v1/trading/{port_id}/orders/{order_id}/cancel", headers=auth_headers)
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "CANCELLED"

    # Verify escrow was refunded back to virtual_cash
    port_view2 = client.get(f"/api/v1/portfolios/{port_id}", headers=auth_headers).json()
    assert port_view2["virtual_cash_balance"] == 10000.0
    assert port_view2["reserved_cash"] == 0.0

def test_order_idempotency_key_prevents_duplicate_executions(client, auth_headers):
    port_res = client.post("/api/v1/portfolios/", json={
        "name": "Idempotent Portfolio",
        "type": "VIRTUAL_TRADING",
        "initial_cash": 50000.0
    }, headers=auth_headers)
    port_id = port_res.json()["id"]

    headers_with_key = {
        **auth_headers,
        "Idempotency-Key": "test-uuid-idempotency-key-001"
    }

    # First request
    res1 = client.post(f"/api/v1/trading/{port_id}/orders", json={
        "ticker": "AAPL",
        "side": "BUY",
        "type": "MARKET",
        "quantity": 10.0
    }, headers=headers_with_key)
    assert res1.status_code == 201
    order1 = res1.json()

    # Second identical request with same idempotency key (simulating retry or network duplicate)
    res2 = client.post(f"/api/v1/trading/{port_id}/orders", json={
        "ticker": "AAPL",
        "side": "BUY",
        "type": "MARKET",
        "quantity": 10.0
    }, headers=headers_with_key)
    assert res2.status_code == 201
    order2 = res2.json()

    # Must return the SAME order ID and not place a second trade
    assert order1["id"] == order2["id"]

    # Verify holding quantity is only 10, not 20
    val_res = client.get(f"/api/v1/portfolios/{port_id}/valuation", headers=auth_headers)
    assert val_res.json()["holdings"][0]["quantity"] == 10.0

def test_manual_portfolio_vs_virtual_trading_separation(client, auth_headers):
    # 1. Create Virtual Trading portfolio -> manual holding insertion must fail
    v_port = client.post("/api/v1/portfolios/", json={
        "name": "Strict Virtual Portfolio",
        "type": "VIRTUAL_TRADING"
    }, headers=auth_headers).json()

    fail_manual = client.post(f"/api/v1/portfolios/{v_port['id']}/holdings", json={
        "ticker": "AAPL",
        "quantity": 50.0,
        "cost_basis": 150.0
    }, headers=auth_headers)
    assert fail_manual.status_code == 400
    assert "only permitted on MANUAL_TRACKING" in fail_manual.json()["detail"]

    # 2. Create Manual Tracking portfolio -> manual holding insertion succeeds
    m_port = client.post("/api/v1/portfolios/", json={
        "name": "External Watch Portfolio",
        "type": "MANUAL_TRACKING"
    }, headers=auth_headers).json()

    success_manual = client.post(f"/api/v1/portfolios/{m_port['id']}/holdings", json={
        "ticker": "AAPL",
        "quantity": 50.0,
        "cost_basis": 150.0
    }, headers=auth_headers)
    assert success_manual.status_code == 201
    assert success_manual.json()["ticker"] == "AAPL"

    # Virtual trade order on MANUAL_TRACKING must be rejected
    fail_trade = client.post(f"/api/v1/trading/{m_port['id']}/orders", json={
        "ticker": "AAPL",
        "side": "BUY",
        "type": "MARKET",
        "quantity": 10.0
    }, headers=auth_headers)
    assert fail_trade.status_code == 400
    assert "only permitted on VIRTUAL_TRADING" in fail_trade.json()["detail"]

def test_limit_order_matching_on_price_move_and_improvement_refund(client, auth_headers):
    # 1. Create Portfolio
    port_res = client.post("/api/v1/portfolios/", json={
        "name": "Limit Match Strategy",
        "type": "VIRTUAL_TRADING",
        "initial_cash": 10000.0
    }, headers=auth_headers)
    port_id = port_res.json()["id"]

    # 2. Place Limit BUY for TSLA at $180 (current TSLA is ~$215)
    limit_buy = client.post(f"/api/v1/trading/{port_id}/orders", json={
        "ticker": "TSLA",
        "side": "BUY",
        "type": "LIMIT",
        "quantity": 10.0,
        "limit_price": 180.0
    }, headers=auth_headers)
    assert limit_buy.status_code == 201
    order_id = limit_buy.json()["id"]
    assert limit_buy.json()["status"] == "PENDING"

    # Escrow is locked: 10 * 180 = $1,800
    port_val = client.get(f"/api/v1/portfolios/{port_id}", headers=auth_headers).json()
    assert port_val["reserved_cash"] == 1800.0
    assert port_val["virtual_cash_balance"] == 8200.0

    # 3. Simulate sudden price drop: TSLA drops to $170 via Anomaly Injector
    inj = client.post("/api/v1/market/anomalies/inject", json={
        "ticker": "TSLA",
        "price_change_pct": -0.21, # Drop below $180 to ~$170
        "headline": "TSLA Intraday Flash Crash"
    })
    assert inj.status_code == 200
    new_price = inj.json()["price"]
    assert new_price <= 180.0

    # The order should have been automatically matched and filled!
    orders_res = client.get(f"/api/v1/trading/{port_id}/orders", headers=auth_headers)
    orders = orders_res.json()
    filled_order = next((o for o in orders if o["id"] == order_id), None)
    assert filled_order is not None
    assert filled_order["status"] == "FILLED"
    assert filled_order["execution_price"] == new_price

    # Verify price improvement refund:
    # Reserved cash was $1,800. Actual cost was 10 * new_price.
    # Refund = 1800 - (10 * new_price) added back to virtual_cash_balance!
    port_after = client.get(f"/api/v1/portfolios/{port_id}", headers=auth_headers).json()
    assert port_after["reserved_cash"] == 0.0
    expected_cash = round(8200.0 + (1800.0 - (10.0 * new_price)), 2)
    assert abs(port_after["virtual_cash_balance"] - expected_cash) < 0.01

    # Verify holdings position created
    val_after = client.get(f"/api/v1/portfolios/{port_id}/valuation", headers=auth_headers).json()
    tsla_h = next((h for h in val_after["holdings"] if h["ticker"] == "TSLA"), None)
    assert tsla_h is not None
    assert tsla_h["quantity"] == 10.0

def test_limit_sell_matching_and_share_commitment_invariants(client, auth_headers):
    # 1. Create Portfolio and buy 20 shares of NVDA
    port_res = client.post("/api/v1/portfolios/", json={
        "name": "Limit Sell Strategy",
        "type": "VIRTUAL_TRADING",
        "initial_cash": 10000.0
    }, headers=auth_headers)
    port_id = port_res.json()["id"]

    client.post(f"/api/v1/trading/{port_id}/orders", json={
        "ticker": "NVDA", "side": "BUY", "type": "MARKET", "quantity": 20.0
    }, headers=auth_headers)

    # 2. Place Limit SELL for 15 shares of NVDA at $190 (current price is ~$128.50)
    limit_sell1 = client.post(f"/api/v1/trading/{port_id}/orders", json={
        "ticker": "NVDA",
        "side": "SELL",
        "type": "LIMIT",
        "quantity": 15.0,
        "limit_price": 190.0
    }, headers=auth_headers)
    assert limit_sell1.status_code == 201
    assert limit_sell1.json()["status"] == "PENDING"
    order_id = limit_sell1.json()["id"]

    # 3. SHARE COMMITMENT INVARIANT: Try to place another limit sell for 10 shares
    # (Only 20 held, 15 already committed in pending limit sell -> only 5 available!)
    oversell_limit = client.post(f"/api/v1/trading/{port_id}/orders", json={
        "ticker": "NVDA",
        "side": "SELL",
        "type": "LIMIT",
        "quantity": 10.0,
        "limit_price": 195.0
    }, headers=auth_headers)
    assert oversell_limit.status_code == 400
    assert "Insufficient available shares" in oversell_limit.json()["detail"]

    # 4. Simulate NVDA price surge to $200 via Anomaly Injector
    inj = client.post("/api/v1/market/anomalies/inject", json={
        "ticker": "NVDA",
        "price_change_pct": 0.55, # Surge above $190
        "headline": "NVDA Unprecedented Datacenter Acceleration Surge"
    })
    assert inj.status_code == 200
    surge_price = inj.json()["price"]
    assert surge_price >= 190.0

    # 5. Order should automatically fill!
    orders_res = client.get(f"/api/v1/trading/{port_id}/orders", headers=auth_headers)
    filled_order = next((o for o in orders_res.json() if o["id"] == order_id), None)
    assert filled_order is not None
    assert filled_order["status"] == "FILLED"
    assert filled_order["execution_price"] == surge_price

    # 6. Verify holding reduced to 5 shares (20 - 15)
    val = client.get(f"/api/v1/portfolios/{port_id}/valuation", headers=auth_headers).json()
    nvda_h = next((h for h in val["holdings"] if h["ticker"] == "NVDA"), None)
    assert nvda_h is not None
    assert nvda_h["quantity"] == 5.0

