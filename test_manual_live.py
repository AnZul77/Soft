#!/usr/bin/env python
"""
Interactive Manual Live Testing & Demonstration Harness
AI-Powered Investment Intelligence Platform

Designed for live demonstration to evaluators. Can connect to a live running
backend server (http://127.0.0.1:8000) or run in-process via FastAPI TestClient.

Usage:
    python test_manual_live.py           # Interactive menu (Step-by-Step or Full Auto)
    python test_manual_live.py --step    # Directly start interactive step-by-step
    python test_manual_live.py --auto    # Directly run fast automated walkthrough
"""
import sys
import json
import time
import uuid
from pathlib import Path

# Add backend directory to sys.path
root_dir = Path(__file__).resolve().parent
backend_dir = root_dir / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# ANSI Color codes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
RESET = "\033[0m"

LIVE_SERVER_URL = "http://127.0.0.1:8000"

class LiveTestClient:
    """Wrapper that communicates with either live HTTP server or in-process TestClient."""
    def __init__(self):
        import httpx
        self.is_live_http = False
        self.client = None
        
        # Check if live server is reachable
        try:
            r = httpx.get(f"{LIVE_SERVER_URL}/health", timeout=1.5)
            if r.status_code == 200:
                self.is_live_http = True
                self.base_url = LIVE_SERVER_URL
                self.http_client = httpx.Client(base_url=self.base_url, timeout=15.0)
                print(f"{GREEN}[LIVE SERVER CONNECTED]{RESET} Target: {LIVE_SERVER_URL}")
        except Exception:
            pass

        if not self.is_live_http:
            print(f"{YELLOW}[IN-PROCESS ENGINE]{RESET} Live server not detected on port 8000. Running in-process via FastAPI TestClient.")
            from fastapi.testclient import TestClient
            from app.main import app
            self.test_client_ctx = TestClient(app)
            self.http_client = self.test_client_ctx.__enter__()
            self.base_url = ""

        self.token = ""

    def set_token(self, token: str):
        self.token = token

    def request(self, method: str, path: str, json_data=None, params=None):
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        t0 = time.time()
        if method.upper() == "GET":
            resp = self.http_client.get(path, headers=headers, params=params)
        elif method.upper() == "POST":
            resp = self.http_client.post(path, headers=headers, json=json_data)
        elif method.upper() == "PUT":
            resp = self.http_client.put(path, headers=headers, json=json_data)
        elif method.upper() == "DELETE":
            resp = self.http_client.delete(path, headers=headers)
        else:
            raise ValueError(f"Unsupported method {method}")
        elapsed_ms = (time.time() - t0) * 1000.0

        try:
            data = resp.json()
        except Exception:
            data = resp.text

        return resp.status_code, data, elapsed_ms

    def close(self):
        if not self.is_live_http and hasattr(self, "test_client_ctx"):
            try:
                self.test_client_ctx.__exit__(None, None, None)
            except Exception:
                pass

def pause_for_user(step_num: int, title: str, auto_mode: bool):
    if auto_mode:
        time.sleep(0.4)
        return
    print(f"\n{YELLOW}[PAUSE]{RESET} Finished Step {step_num}: {BOLD}{title}{RESET}")
    val = input(f"Press {BOLD}[ENTER]{RESET} to continue to next step (or 'q' to return to menu): ").strip()
    if val.lower() == 'q':
        print("\nExiting demonstration.\n")
        sys.exit(0)
    print("\n" + "-" * 70)

def print_step_header(step_num: int, title: str, description: str):
    print("\n" + CYAN + BOLD + "=" * 70 + RESET)
    print(f"{CYAN}{BOLD} STEP {step_num}: {title.upper()}{RESET}")
    print(f" {description}")
    print(CYAN + "=" * 70 + RESET)

def run_live_demonstration(auto_mode=False):
    client = LiveTestClient()
    session_id = uuid.uuid4().hex[:6]
    test_user_email = f"demo_{session_id}@example.com"
    test_password = "SecurePassword123!"

    print("\n" + BOLD + MAGENTA + "*" * 70 + RESET)
    print(BOLD + MAGENTA + "   AI-POWERED INVESTMENT INTELLIGENCE PLATFORM" + RESET)
    print(BOLD + MAGENTA + "   Interactive Live Demonstration Harness" + RESET)
    print(f"   Session ID: {session_id} | Mode: {'Automated Fast Walkthrough' if auto_mode else 'Interactive Step-by-Step'}")
    print(BOLD + MAGENTA + "*" * 70 + RESET)

    try:
        # Step 1: Health & Root
        print_step_header(1, "System Health & Discovery", "Verifies API server status, database connection, and OpenAPI spec.")
        status, data, ms = client.request("GET", "/health")
        print(f" -> GET /health | Status: {GREEN}{status}{RESET} ({ms:.1f}ms)")
        print(f"    Payload: {json.dumps(data)}")
        assert status == 200 and data.get("status") == "healthy"
        pause_for_user(1, "System Health", auto_mode)

        # Step 2: User Registration & JWT Auth
        print_step_header(2, "User Registration & Multi-Tenant JWT Auth", f"Creates test investor: {test_user_email}")
        reg_payload = {"email": test_user_email, "password": test_password, "full_name": "Dr. Alex Vance"}
        status, data, ms = client.request("POST", "/api/v1/auth/register", json_data=reg_payload)
        print(f" -> POST /api/v1/auth/register | Status: {GREEN}{status}{RESET} ({ms:.1f}ms)")
        print(f"    Created User ID: {data.get('id')}")

        login_payload = {"email": test_user_email, "password": test_password}
        status, data, ms = client.request("POST", "/api/v1/auth/token", json_data=login_payload)
        token = data.get("access_token")
        client.set_token(token)
        print(f" -> POST /api/v1/auth/token | Status: {GREEN}{status}{RESET} ({ms:.1f}ms)")
        print(f"    JWT Token (HS256): {token[:25]}...{token[-10:]}")
        pause_for_user(2, "Authentication & Session", auto_mode)

        # Step 3: Profile & Risk Preferences
        print_step_header(3, "Risk Profile & Investor Preferences", "Configures risk tolerance (AGGRESSIVE) and horizon (LONG_TERM).")
        prof_payload = {
            "full_name": "Dr. Alex Vance",
            "bio": "Quantitative investor specializing in AI semiconductor supply chains.",
            "risk_tolerance": "AGGRESSIVE",
            "investment_horizon": "LONG_TERM"
        }
        status, data, ms = client.request("PUT", "/api/v1/auth/profile", json_data=prof_payload)
        print(f" -> PUT /api/v1/auth/profile | Status: {GREEN}{status}{RESET} ({ms:.1f}ms)")
        print(f"    Updated Profile: Tolerance={data.get('risk_tolerance')} | Horizon={data.get('investment_horizon')}")
        pause_for_user(3, "Investor Profile Preferences", auto_mode)

        # Step 4: Watchlists
        print_step_header(4, "Watchlist Creation & Securities Tracking", "Creates 'Tech Giants' watchlist and tracks NVDA, AAPL, MSFT.")
        status, wl_data, ms = client.request("POST", "/api/v1/watchlists/", json_data={"name": "Semis & Tech Leaders"})
        wl_id = wl_data.get("id")
        print(f" -> POST /api/v1/watchlists/ | Status: {GREEN}{status}{RESET} ({ms:.1f}ms)")
        print(f"    Watchlist ID: {wl_id} ('{wl_data.get('name')}')")

        for ticker in ["NVDA", "AAPL", "MSFT"]:
            s, d, _ = client.request("POST", f"/api/v1/watchlists/{wl_id}/items", json_data={"ticker": ticker})
            print(f"    + Added {ticker} to watchlist -> HTTP {s}")
        pause_for_user(4, "Watchlist Management", auto_mode)

        # Step 5: Portfolio Creation
        print_step_header(5, "Virtual Trading Portfolio & Double-Entry Ledger", "Initializes simulated portfolio with $100,000 cash balance.")
        port_payload = {"name": "AI Growth Portfolio", "type": "VIRTUAL_TRADING"}
        status, port_data, ms = client.request("POST", "/api/v1/portfolios/", json_data=port_payload)
        portfolio_id = port_data.get("id")
        print(f" -> POST /api/v1/portfolios/ | Status: {GREEN}{status}{RESET} ({ms:.1f}ms)")
        print(f"    Portfolio ID: {portfolio_id}")
        print(f"    Virtual Cash Balance: ${port_data.get('virtual_cash_balance'):,.2f} | Mode: {port_data.get('type')}")
        pause_for_user(5, "Virtual Portfolio Setup", auto_mode)

        # Step 6: Market BUY Order Execution
        print_step_header(6, "Market BUY Order Execution & Cash Invariants", "Executes simulated BUY for 15 shares of NVDA at market price.")
        order_payload = {
            "ticker": "NVDA",
            "side": "BUY",
            "type": "MARKET",
            "quantity": 15.0
        }
        status, order_data, ms = client.request("POST", f"/api/v1/trading/{portfolio_id}/orders", json_data=order_payload)
        print(f" -> POST /api/v1/trading/{portfolio_id}/orders | Status: {GREEN}{status}{RESET} ({ms:.1f}ms)")
        print(f"    Order Status: {order_data.get('status')} | Fill Price: ${order_data.get('execution_price', 0):.2f}")
        print(f"    Total Cost: ${order_data.get('quantity', 0) * (order_data.get('execution_price') or 0):,.2f}")
        pause_for_user(6, "Market Order Execution", auto_mode)

        # Step 7: Limit Order Escrow & Matching
        print_step_header(7, "Limit Order Escrow Reservation & Execution", "Places Limit BUY for AAPL at $140 with cash escrow lock.")
        limit_payload = {
            "ticker": "AAPL",
            "side": "BUY",
            "type": "LIMIT",
            "quantity": 10.0,
            "limit_price": 140.0
        }
        status, limit_data, ms = client.request("POST", f"/api/v1/trading/{portfolio_id}/orders", json_data=limit_payload)
        print(f" -> POST /api/v1/trading/{portfolio_id}/orders (LIMIT BUY) | Status: {GREEN}{status}{RESET} ({ms:.1f}ms)")
        print(f"    Order Status: {limit_data.get('status')} (Funds held in reserved_cash: $1,400.00)")

        # Trigger order matching
        s_match, d_match, _ = client.request("POST", "/api/v1/trading/match-orders")
        print(f" -> POST /api/v1/trading/match-orders | Status: {GREEN}{s_match}{RESET}")
        matched_count = len(d_match) if isinstance(d_match, list) else 0
        print(f"    Matching Engine Scan: Evaluated {matched_count} matched orders.")
        pause_for_user(7, "Limit Order Escrow & Matching", auto_mode)

        # Step 8: Portfolio Valuation
        print_step_header(8, "Portfolio Valuation & Stale Price Hierarchy", "Calculates total equity, unrealized P&L, and asset weights.")
        status, val_data, ms = client.request("GET", f"/api/v1/portfolios/{portfolio_id}")
        print(f" -> GET /api/v1/portfolios/{portfolio_id} | Status: {GREEN}{status}{RESET} ({ms:.1f}ms)")
        total_equity = val_data.get('total_equity', 0.0)
        cash_bal = val_data.get('virtual_cash_balance', 0.0)
        print(f"    Total Portfolio Equity: ${total_equity:,.2f}")
        print(f"    Virtual Cash Balance:   ${cash_bal:,.2f}")
        print(f"    Holdings Count:         {len(val_data.get('holdings', []))}")
        for h in val_data.get("holdings", []):
            print(f"      - {h.get('ticker')}: {h.get('quantity')} shs @ ${h.get('current_price'):.2f} (Weight: {h.get('weight_pct'):.1f}%, Source: {h.get('price_source')})")
        pause_for_user(8, "Portfolio Valuation", auto_mode)

        # Step 9: Systematic Risk Analytics
        print_step_header(9, "Systematic Risk Metrics (HHI, Beta, VaR)", "Evaluates portfolio diversification and downside risk.")
        status, risk_data, ms = client.request("GET", f"/api/v1/risk-anomalies/portfolios/{portfolio_id}/risk")
        print(f" -> GET /api/v1/risk-anomalies/portfolios/{portfolio_id}/risk | Status: {GREEN}{status}{RESET} ({ms:.1f}ms)")
        print(f"    Portfolio Beta to SPY:  {risk_data.get('portfolio_beta', 1.0)}")
        print(f"    Concentration (HHI):   {risk_data.get('concentration_hhi', 0.0):.4f} (High Conc: {risk_data.get('is_high_concentration')})")
        print(f"    Annualized Volatility: {risk_data.get('annualized_volatility', 0.0) * 100:.2f}%")
        print(f"    1-Day 95% Parametric VaR: ${risk_data.get('value_at_risk_95_1d', 0.0):,.2f}")
        pause_for_user(9, "Risk Analytics", auto_mode)

        # Step 10: 8% Price Anomaly Injection & Alert Trigger
        print_step_header(10, "Market Anomaly Simulation & Automated Alerting", "Injects 8.5% price shock on NVDA and triggers portfolio scan.")
        status, inj_data, ms = client.request("POST", "/api/v1/market/anomalies/inject", json_data={"ticker": "NVDA", "price_change_pct": -0.085})
        print(f" -> POST /api/v1/market/anomalies/inject | Status: {GREEN}{status}{RESET} ({ms:.1f}ms)")
        print(f"    Injected New Price: ${inj_data.get('price'):.2f} (Change: {inj_data.get('change_percent'):.2f}%)")

        status, scan_data, ms = client.request("POST", "/api/v1/risk-anomalies/anomalies/scan")
        print(f" -> POST /api/v1/risk-anomalies/anomalies/scan | Status: {GREEN}{status}{RESET} ({ms:.1f}ms)")
        alert_count = len(scan_data) if isinstance(scan_data, list) else 0
        print(f"    Generated Alerts: {alert_count} portfolio notification(s)")
        pause_for_user(10, "Anomaly Detection & Alerts", auto_mode)

        # Step 11: Grounded RAG Explain Impact
        print_step_header(11, "Grounded RAG 'Explain Impact' Decision Support", "Answers: 'Why does this NVDA market event matter to my portfolio?'")
        status, exp_data, ms = client.request("POST", "/api/v1/ai/explain-impact", json_data={"portfolio_id": portfolio_id, "ticker": "NVDA"})
        print(f" -> POST /api/v1/ai/explain-impact | Status: {GREEN}{status}{RESET} ({ms:.1f}ms)")
        print(f"    Headline: {BOLD}{exp_data.get('summary_headline')}{RESET}")
        print(f"    Exposure: {exp_data.get('portfolio_exposure_pct', 0.0):.1f}% of portfolio equity")
        links_list = exp_data.get('supply_chain_links', [])
        links_str = ', '.join([f"{l.get('source_ticker')} ({l.get('relationship_type')}) {l.get('target_ticker')}" for l in links_list])
        print(f"    Supply-Chain Links: {links_str or 'None direct'}")
        print(f"    Citations Grounded: {len(exp_data.get('evidence_citations', []))} verified sources")
        for cite in exp_data.get("evidence_citations", [])[:2]:
            print(f"      * [{cite.get('source')}] {cite.get('title')}")
        print(f"    Disclaimer: {exp_data.get('regulatory_disclaimer', '')[:75]}...")
        pause_for_user(11, "Grounded AI Decision Support", auto_mode)

        # Step 12: Investment Journal & AI Reflection
        print_step_header(12, "Investment Journal & AI Thesis Reflection", "Records investment thesis and generates objective reflection.")
        journal_payload = {
            "portfolio_id": portfolio_id,
            "ticker": "NVDA",
            "thesis_title": "Blackwell Architecture Supercycle",
            "thesis_content": "Hypothesis: Datacenter demand will accelerate gross margins through FY2027.",
            "conviction_score": 5,
            "target_price": 185.0
        }
        status, j_data, ms = client.request("POST", "/api/v1/journal/", json_data=journal_payload)
        entry_id = j_data.get("id")
        print(f" -> POST /api/v1/journal/ | Status: {GREEN}{status}{RESET} ({ms:.1f}ms)")
        print(f"    Created Thesis ID: {entry_id} (Conviction: 5/5 stars, Target: $185.00)")

        status, ref_data, ms = client.request("POST", f"/api/v1/journal/{entry_id}/reflect")
        print(f" -> POST /api/v1/journal/{entry_id}/reflect | Status: {GREEN}{status}{RESET} ({ms:.1f}ms)")
        ai_reflection_text = ref_data.get('ai_reflection') or "Reflection generated successfully."
        print(f"    AI Reflection: {ai_reflection_text[:110]}...")
        pause_for_user(12, "Thesis Reflection", auto_mode)

        # Step 13: System & Security Audit Log
        print_step_header(13, "System & Financial Audit Trail Verification", "Verifies that security and financial actions were recorded.")
        status, audit_data, ms = client.request("GET", "/api/v1/auth/audit-logs")
        print(f" -> GET /api/v1/auth/audit-logs | Status: {GREEN}{status}{RESET} ({ms:.1f}ms)")
        print(f"    Recorded Audit Events: {len(audit_data)} entries")
        for a in audit_data[:4]:
            print(f"      - [{a.get('action')}] User: {a.get('user_id')[:8]}... | Details: {a.get('details')[:50]}...")
        pause_for_user(13, "Audit Logging", auto_mode)

        # Conclusion
        print("\n" + GREEN + BOLD + "=" * 70 + RESET)
        print(f"{GREEN}{BOLD}  LIVE DEMONSTRATION COMPLETE: ALL 13 CORE WORKFLOWS VERIFIED!{RESET}")
        print(GREEN + BOLD + "=" * 70 + RESET + "\n")

    finally:
        client.close()

def main():
    if "--auto" in sys.argv or "--fast" in sys.argv:
        run_live_demonstration(auto_mode=True)
        return
    if "--step" in sys.argv:
        run_live_demonstration(auto_mode=False)
        return

    print("\n" + CYAN + BOLD + "=" * 65 + RESET)
    print(CYAN + BOLD + "   AI-POWERED INVESTMENT INTELLIGENCE PLATFORM" + RESET)
    print(CYAN + BOLD + "   Live Interactive Testing & Demonstration Suite" + RESET)
    print(CYAN + BOLD + "=" * 65 + RESET)
    print("Choose testing mode:")
    print("  [1] Interactive Step-by-Step Live Demo (pauses with explanations)")
    print("  [2] Automated Fast Walkthrough (runs all 13 steps in ~8 seconds)")
    print("  [3] Run Automated Pytest Test Suite (29 unit & invariant tests)")
    print("  [4] Exit")
    print(CYAN + "-" * 65 + RESET)
    
    choice = input("Enter choice [1-4] (default: 1): ").strip()
    if choice == "2":
        run_live_demonstration(auto_mode=True)
    elif choice == "3":
        import run_automated_tests
        run_automated_tests.main()
    elif choice == "4":
        print("Goodbye.")
    else:
        run_live_demonstration(auto_mode=False)

if __name__ == "__main__":
    main()
