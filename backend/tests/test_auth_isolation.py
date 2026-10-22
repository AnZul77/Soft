import pytest

def test_user_registration_and_login(client):
    # Register User
    res = client.post("/api/v1/auth/register", json={
        "email": "user_a@example.com",
        "password": "Password123!",
        "full_name": "User Alpha"
    })
    assert res.status_code == 201
    data = res.json()
    assert data["email"] == "user_a@example.com"
    assert "id" in data

    # Login with JSON
    login_res = client.post("/api/v1/auth/login-json", json={
        "email": "user_a@example.com",
        "password": "Password123!"
    })
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

    # Access /me with token
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "user_a@example.com"

def test_duplicate_user_registration_fails(client):
    res1 = client.post("/api/v1/auth/register", json={
        "email": "duplicate@example.com",
        "password": "Password123!"
    })
    assert res1.status_code == 201

    res2 = client.post("/api/v1/auth/register", json={
        "email": "duplicate@example.com",
        "password": "Password123!"
    })
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"]

def test_strict_multi_tenant_portfolio_isolation(client):
    # Register User A
    client.post("/api/v1/auth/register", json={"email": "alice@example.com", "password": "pass"})
    res_a = client.post("/api/v1/auth/login-json", json={"email": "alice@example.com", "password": "pass"})
    token_a = res_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Register User B
    client.post("/api/v1/auth/register", json={"email": "bob@example.com", "password": "pass"})
    res_b = client.post("/api/v1/auth/login-json", json={"email": "bob@example.com", "password": "pass"})
    token_b = res_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Alice creates a portfolio
    port_res = client.post("/api/v1/portfolios/", json={
        "name": "Alice Private Fund",
        "type": "VIRTUAL_TRADING",
        "initial_cash": 50000.0
    }, headers=headers_a)
    assert port_res.status_code == 201
    alice_portfolio_id = port_res.json()["id"]

    # Bob tries to view Alice's portfolio -> Must return 404
    bob_view = client.get(f"/api/v1/portfolios/{alice_portfolio_id}", headers=headers_b)
    assert bob_view.status_code == 404

    # Bob tries to delete Alice's portfolio -> Must return 404
    bob_del = client.delete(f"/api/v1/portfolios/{alice_portfolio_id}", headers=headers_b)
    assert bob_del.status_code == 404

    # Bob's portfolio list should NOT contain Alice's portfolio
    bob_list = client.get("/api/v1/portfolios/", headers=headers_b)
    assert bob_list.status_code == 200
    assert len(bob_list.json()) == 0

    # Alice places an order
    alice_order = client.post(f"/api/v1/trading/{alice_portfolio_id}/orders", json={
        "ticker": "NVDA", "side": "BUY", "type": "MARKET", "quantity": 10.0
    }, headers=headers_a)
    assert alice_order.status_code == 201
    order_id = alice_order.json()["id"]

    # Bob tries to access Alice's trading orders -> Must return 404
    bob_orders = client.get(f"/api/v1/trading/{alice_portfolio_id}/orders", headers=headers_b)
    assert bob_orders.status_code == 404

    # Bob tries to access Alice's cash transactions -> Must return 404
    bob_txs = client.get(f"/api/v1/trading/{alice_portfolio_id}/transactions", headers=headers_b)
    assert bob_txs.status_code == 404

    # Bob tries to cancel Alice's order -> Must return 404
    bob_cancel = client.post(f"/api/v1/trading/{alice_portfolio_id}/orders/{order_id}/cancel", headers=headers_b)
    assert bob_cancel.status_code == 404

    # Bob tries to attach a journal entry to Alice's portfolio -> Must return 404
    bob_journal = client.post("/api/v1/journal/", json={
        "portfolio_id": alice_portfolio_id,
        "ticker": "NVDA",
        "thesis_title": "Bob spying on Alice",
        "thesis_content": "Unauthorized link attempt"
    }, headers=headers_b)
    assert bob_journal.status_code == 404

    # Bob tries to request AI Explain Impact on Alice's portfolio -> Must return 404
    bob_explain = client.post("/api/v1/ai/explain-impact", json={
        "portfolio_id": alice_portfolio_id,
        "ticker": "NVDA",
        "event_description": "Probe event"
    }, headers=headers_b)
    assert bob_explain.status_code == 404

def test_unauthenticated_request_rejected(client):
    res = client.get("/api/v1/portfolios/")
    assert res.status_code == 401
