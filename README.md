# AI-Powered Investment Intelligence Platform (v1.0)

> An institutional-grade decision-support platform engineered to answer: **"Why does this market event matter to *my* portfolio?"** with grounded semantic RAG citations, strict double-entry ledger invariants, automated anomaly detection, and systematic risk analytics.

---

## 1. System Architecture & Multi-Agent Domain Division

The system is architected across functional divisions solving the 7 critical paradoxes identified in the PRD analysis:

| Domain | Responsible Role | Implementation Scope |
| :--- | :--- | :--- |
| **System Orchestration** | **1 Lead Orchestrator** | Database lifecycle (SQLite out-of-the-box + PostgreSQL/pgvector production), configuration management, CORS, Docker Compose containerization. |
| **Auth & Isolation** | **Core Backend 1** | JWT bearer auth, bcrypt password hashing, and strict multi-tenant tenant isolation (`user_id == current_user.id`). |
| **Ledger & Valuation** | **Core Backend 2** | Account mode separation (`MANUAL_TRACKING` vs `VIRTUAL_TRADING`), cash invariants, escrow reservation pattern for limit orders, idempotency header middleware, and valuation fallback engine (`effective_price = quote.price ?? quote.last_close ?? cost_basis`). |
| **Market & Anomalies** | **Core Backend 3** | Consolidated asset watcher queue, quote cache (TTL 60s), 8% 15-minute price anomaly scanner, and in-app notification center. |
| **Vector RAG & Graph** | **ML / AI Intelligence 1** | Text chunking with token overlap, normalized vector embeddings, cosine similarity search, and relational supply-chain knowledge graph (e.g. `TSMC -> SUPPLIER -> NVDA`). |
| **Explainable AI Agent** | **ML / AI Intelligence 2** | "Explain Impact" synthesis engine with prompt injection defense, strict citation anchoring, grounded abstention on empty context, Server-Sent Events (SSE) token streaming, and AI Thesis Reflection. |
| **Modern Financial UI** | **High Quality UI** | Dark-mode interface built with React, Vite, Tailwind CSS, Lucide icons, and modern `<dialog closedby="any">` modals with light-dismiss fallbacks per modern web guidance. |
| **Rigorous Testing** | **Testing Team (3 Suites)** | 29 comprehensive automated tests covering ledger invariants, isolation, risk metrics, anomaly triggers, RAG citations, limit order matching, audit logs, watchlists, profile settings, and full end-to-end user journeys. |

---

## 2. Solutions to Critical PRD Flaws

1. **The Accounting Paradox (Problem 1):** Distinct `MANUAL_TRACKING` (external read-only holding CRUD) and `VIRTUAL_TRADING` (strictly auditable double-entry cash ledger and position mutations via executed orders).
2. **Market Pipeline Feasibility (Problem 2):** Consolidated asset watcher deduplicates held tickers across all user portfolios; interactive mock anomaly injector for instant testing of 8%+ moves.
3. **The Knowledge Graph Trap (Problem 3):** Replaced heavy standalone Neo4j and separate vector DB with PostgreSQL `pgvector` / relational adjacency graph + dense vector index.
4. **Limit Order Escrow (Problem 4):** Funds reserved into `reserved_cash` upon limit order placement; refunded automatically upon cancellation or price improvement.
5. **Regulatory Guardrails & Injections (Problem 5):** Input sanitization blocks prompt overrides; mandatory non-advisory SEC/FINRA disclaimers; explicit abstention (`"Insufficient grounded evidence"`) when context is empty.
6. **Valuation Fallbacks (Problem 6):** Missing prices never become zero; fall back to previous close or cost basis with `is_stale: True` and explicit source badges.
7. **Idempotency Controls (Problem 7):** Client-generated `Idempotency-Key` headers guarantee network retries do not trigger duplicate executions or double debits.

---

## 3. Quick Start Guide

### Backend Setup & Test Execution
```bash
cd backend

# Install dependencies
python -m pip install -r requirements.txt

# Run full test suite (29 tests)
python -m pytest -v

# Run the backend API server (http://localhost:8000)
uvicorn app.main:app --reload --port 8000
```
API Documentation is available at: `http://localhost:8000/docs`

### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start Vite dev server (http://localhost:3000)
npm run dev

# Build for production
npm run build
```

### Full Stack Docker Deployment
```bash
docker-compose up --build
```
- Frontend UI: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
