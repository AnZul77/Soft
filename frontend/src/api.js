const rawApiUrl = import.meta.env?.VITE_API_URL || "";
const cleanUrl = rawApiUrl.replace(/\/+$/, '');
const API_BASE = cleanUrl 
  ? (cleanUrl.endsWith('/api/v1') ? cleanUrl : `${cleanUrl}/api/v1`)
  : "/api/v1";

let authToken = localStorage.getItem("apex_token") || "";

export const setAuthToken = (token) => {
  authToken = token;
  if (token) {
    localStorage.setItem("apex_token", token);
  } else {
    localStorage.removeItem("apex_token");
  }
};

export const getAuthToken = () => authToken;

const request = async (endpoint, options = {}) => {
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {})
  };

  if (authToken) {
    headers["Authorization"] = `Bearer ${authToken}`;
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers
  });

  if (!response.ok) {
    let errorDetail = "An unexpected error occurred";
    try {
      const errJson = await response.json();
      errorDetail = errJson.detail || JSON.stringify(errJson);
    } catch {
      errorDetail = await response.text();
    }
    throw new Error(errorDetail);
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
};

export const api = {
  // Auth
  register: (email, password, full_name) =>
    request("/auth/register", { method: "POST", body: JSON.stringify({ email, password, full_name }) }),
  login: (email, password) =>
    request("/auth/login-json", { method: "POST", body: JSON.stringify({ email, password }) }),
  getMe: () => request("/auth/me"),

  getProfile: () => request("/auth/profile"),
  updateProfile: (profileData) =>
    request("/auth/profile", { method: "PUT", body: JSON.stringify(profileData) }),
  getAuditLogs: (limit = 50) => request(`/auth/audit-logs?limit=${limit}`),

  // Portfolios
  getPortfolios: () => request("/portfolios/"),
  getPortfolio: (id) => request(`/portfolios/${id}`),
  createPortfolio: (name, type = "VIRTUAL_TRADING", initial_cash = 100000) =>
    request("/portfolios/", { method: "POST", body: JSON.stringify({ name, type, initial_cash }) }),
  updatePortfolio: (id, data) =>
    request(`/portfolios/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  deletePortfolio: (id) => request(`/portfolios/${id}`, { method: "DELETE" }),
  getValuation: (id) => request(`/portfolios/${id}/valuation`),
  addManualHolding: (portfolioId, ticker, quantity, cost_basis) =>
    request(`/portfolios/${portfolioId}/holdings`, {
      method: "POST",
      body: JSON.stringify({ ticker, quantity, cost_basis })
    }),
  deleteManualHolding: (portfolioId, holdingId) =>
    request(`/portfolios/${portfolioId}/holdings/${holdingId}`, { method: "DELETE" }),

  // Trading
  placeOrder: (portfolioId, orderData, idempotencyKey) => {
    const headers = {};
    if (idempotencyKey) {
      headers["Idempotency-Key"] = idempotencyKey;
    }
    return request(`/trading/${portfolioId}/orders`, {
      method: "POST",
      headers,
      body: JSON.stringify(orderData)
    });
  },
  getOrders: (portfolioId) => request(`/trading/${portfolioId}/orders`),
  cancelOrder: (portfolioId, orderId) =>
    request(`/trading/${portfolioId}/orders/${orderId}/cancel`, { method: "POST" }),
  getTransactions: (portfolioId) => request(`/trading/${portfolioId}/transactions`),

  // Market
  getQuotes: () => request("/market/quotes"),
  getSingleQuote: (ticker) => request(`/market/quotes/${ticker}`),
  getPriceHistory: (ticker, period = "30d") =>
    request(`/market/history/${ticker}?period=${period}`),
  injectAnomaly: (ticker, price_change_pct, headline, content) =>
    request("/market/anomalies/inject", {
      method: "POST",
      body: JSON.stringify({ ticker, price_change_pct, headline, content })
    }),
  getNews: () => request("/market/news"),

  // Watchlists (FR-07)
  getWatchlists: () => request("/watchlists/"),
  getWatchlist: (id) => request(`/watchlists/${id}`),
  createWatchlist: (name, description) =>
    request("/watchlists/", { method: "POST", body: JSON.stringify({ name, description }) }),
  updateWatchlist: (id, data) =>
    request(`/watchlists/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  deleteWatchlist: (id) => request(`/watchlists/${id}`, { method: "DELETE" }),
  addWatchlistItem: (watchlistId, ticker, notes, target_price) =>
    request(`/watchlists/${watchlistId}/items`, {
      method: "POST",
      body: JSON.stringify({ ticker, notes, target_price })
    }),
  removeWatchlistItem: (watchlistId, itemId) =>
    request(`/watchlists/${watchlistId}/items/${itemId}`, { method: "DELETE" }),

  // Risk & Anomalies
  getPortfolioRisk: (portfolioId) => request(`/risk-anomalies/portfolios/${portfolioId}/risk`),
  runAnomalyScan: () => request("/risk-anomalies/anomalies/scan", { method: "POST" }),
  getAlerts: () => request("/risk-anomalies/alerts"),
  markAlertRead: (alertId) => request(`/risk-anomalies/alerts/${alertId}/read`, { method: "PUT" }),

  // Alert Rules (FR-18)
  getAlertRules: () => request("/alerts/rules"),
  createAlertRule: (ruleData) =>
    request("/alerts/rules", { method: "POST", body: JSON.stringify(ruleData) }),
  updateAlertRule: (ruleId, ruleData) =>
    request(`/alerts/rules/${ruleId}`, { method: "PUT", body: JSON.stringify(ruleData) }),
  deleteAlertRule: (ruleId) => request(`/alerts/rules/${ruleId}`, { method: "DELETE" }),

  // AI & RAG
  explainImpact: (portfolioId, ticker, event_description, price_change_pct) =>
    request("/ai/explain-impact", {
      method: "POST",
      body: JSON.stringify({
        portfolio_id: portfolioId,
        ticker,
        event_description,
        price_change_pct
      })
    }),

  // SSE stream explain impact
  streamExplainImpact: (portfolioId, ticker, event_description, onChunk, onDone, onError) => {
    const params = new URLSearchParams({
      portfolio_id: portfolioId,
      ticker,
      event_description: event_description || ""
    });
    const url = `${API_BASE}/ai/explain-impact/stream?${params.toString()}`;

    const headers = {};
    if (authToken) headers["Authorization"] = `Bearer ${authToken}`;

    fetch(url, { headers })
      .then(async (res) => {
        if (!res.ok) throw new Error("Streaming error: " + (await res.text()));
        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n\n");
          buffer = lines.pop() || "";

          for (const block of lines) {
            if (block.includes("event: done") || block.includes("[COMPLETED]")) {
              onDone();
              return;
            }
            if (block.startsWith("data:")) {
              const text = block.replace("data:", "").trimStart();
              onChunk(text);
            }
          }
        }
        onDone();
      })
      .catch((err) => {
        if (onError) onError(err);
      });
  },

  researchQuery: (query, ticker, limit = 5) =>
    request("/ai/research", { method: "POST", body: JSON.stringify({ query, ticker, limit }) }),

  // Journal (FR-22)
  getJournalEntries: (is_archived) => {
    const q = is_archived !== undefined ? `?is_archived=${is_archived}` : '';
    return request(`/journal/${q}`);
  },
  createJournalEntry: (entryData) =>
    request("/journal/", { method: "POST", body: JSON.stringify(entryData) }),
  updateJournalEntry: (id, entryData) =>
    request(`/journal/${id}`, { method: "PUT", body: JSON.stringify(entryData) }),
  archiveJournalEntry: (id) => request(`/journal/${id}/archive`, { method: "PUT" }),
  deleteJournalEntry: (id) => request(`/journal/${id}`, { method: "DELETE" }),
  reflectOnThesis: (entryId) =>
    request(`/journal/${entryId}/reflect`, { method: "POST" })
};
