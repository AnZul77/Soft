import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import PortfolioOverview from './components/PortfolioOverview';
import TradeOrderModal from './components/TradeOrderModal';
import MarketWatch from './components/MarketWatch';
import AnomalyAlertsFeed from './components/AnomalyAlertsFeed';
import ExplainImpactModal from './components/ExplainImpactModal';
import RiskAnalyticsCard from './components/RiskAnalyticsCard';
import InvestmentJournal from './components/InvestmentJournal';
import { api, setAuthToken, getAuthToken } from './api';
import { 
  Sparkles, 
  ArrowRight, 
  ShieldCheck, 
  TrendingUp, 
  RefreshCw, 
  Plus, 
  X,
  Lock,
  Wallet
} from 'lucide-react';

export default function App() {
  const [user, setUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(true);
  const [authMode, setAuthMode] = useState('login'); // 'login' or 'register'
  const [email, setEmail] = useState('investor@intelligence.ai');
  const [password, setPassword] = useState('Password123!');
  const [fullName, setFullName] = useState('Alpha Investor');
  const [authError, setAuthError] = useState('');

  // Platform state
  const [portfolios, setPortfolios] = useState([]);
  const [activePortfolio, setActivePortfolio] = useState(null);
  const [valuation, setValuation] = useState(null);
  const [quotes, setQuotes] = useState([]);
  const [news, setNews] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [orders, setOrders] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [activeTab, setActiveTab] = useState('overview');

  // Modals
  const [isTradeModalOpen, setIsTradeModalOpen] = useState(false);
  const [tradeDefaultTicker, setTradeDefaultTicker] = useState('NVDA');
  const [isExplainModalOpen, setIsExplainModalOpen] = useState(false);
  const [explainParams, setExplainParams] = useState({ ticker: 'TSMC', event: '', priceChangePct: 0 });
  const [isCreatePortOpen, setIsCreatePortOpen] = useState(false);
  const [newPortName, setNewPortName] = useState('');
  const [newPortType, setNewPortType] = useState('VIRTUAL_TRADING');
  const [isAddManualOpen, setIsAddManualOpen] = useState(false);
  const [manualTicker, setManualTicker] = useState('AAPL');
  const [manualQty, setManualQty] = useState('50');
  const [manualCost, setManualCost] = useState('180');

  // Initial Auth Check
  useEffect(() => {
    const token = getAuthToken();
    if (token) {
      api.getMe()
        .then(setUser)
        .catch(() => {
          setAuthToken('');
          setUser(null);
        })
        .finally(() => setAuthLoading(false));
    } else {
      setAuthLoading(false);
    }
  }, []);

  // Load user data once logged in
  const refreshAllData = async () => {
    if (!user) return;
    try {
      const [portList, quoteList, newsList, alertList] = await Promise.all([
        api.getPortfolios(),
        api.getQuotes(),
        api.getNews(),
        api.getAlerts()
      ]);

      setPortfolios(portList);
      setQuotes(quoteList);
      setNews(newsList);
      setAlerts(alertList);

      // Select active portfolio if none selected or if list updated
      let current = activePortfolio;
      if (!current && portList.length > 0) {
        current = portList[0];
        setActivePortfolio(current);
      } else if (current) {
        const found = portList.find(p => p.id === current.id);
        if (found) {
          setActivePortfolio(found);
          current = found;
        } else if (portList.length > 0) {
          current = portList[0];
          setActivePortfolio(current);
        }
      }

      if (current) {
        const [val, ords, txs] = await Promise.all([
          api.getValuation(current.id),
          api.getOrders(current.id),
          api.getTransactions(current.id)
        ]);
        setValuation(val);
        setOrders(ords);
        setTransactions(txs);
      } else if (portList.length === 0) {
        // Auto-seed a demo portfolio for convenience
        const initial = await api.createPortfolio("Alpha Flagship Fund", "VIRTUAL_TRADING", 100000);
        setPortfolios([initial]);
        setActivePortfolio(initial);
        const val = await api.getValuation(initial.id);
        setValuation(val);
      }
    } catch (err) {
      console.error("Data refresh error:", err);
    }
  };

  useEffect(() => {
    if (user) {
      refreshAllData();
      const interval = setInterval(refreshAllData, 15000);
      return () => clearInterval(interval);
    }
  }, [user]);

  useEffect(() => {
    if (activePortfolio) {
      api.getValuation(activePortfolio.id).then(setValuation).catch(console.error);
      api.getOrders(activePortfolio.id).then(setOrders).catch(console.error);
      api.getTransactions(activePortfolio.id).then(setTransactions).catch(console.error);
    }
  }, [activePortfolio?.id]);

  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    setAuthError('');
    try {
      if (authMode === 'register') {
        await api.register(email, password, fullName);
      }
      const data = await api.login(email, password);
      setAuthToken(data.access_token);
      setUser(data.user);
    } catch (err) {
      setAuthError(err.message);
    }
  };

  const handleLogout = () => {
    setAuthToken('');
    setUser(null);
    setPortfolios([]);
    setActivePortfolio(null);
  };

  const handleCreatePortfolio = async (e) => {
    e.preventDefault();
    if (!newPortName) return;
    try {
      const p = await api.createPortfolio(newPortName, newPortType, newPortType === 'VIRTUAL_TRADING' ? 100000 : 0);
      setNewPortName('');
      setIsCreatePortOpen(false);
      await refreshAllData();
      setActivePortfolio(p);
    } catch (err) {
      alert("Error creating portfolio: " + err.message);
    }
  };

  const handleAddManualHolding = async (e) => {
    e.preventDefault();
    if (!activePortfolio) return;
    try {
      await api.addManualHolding(
        activePortfolio.id,
        manualTicker.toUpperCase(),
        parseFloat(manualQty),
        parseFloat(manualCost)
      );
      setIsAddManualOpen(false);
      refreshAllData();
    } catch (err) {
      alert("Error adding holding: " + err.message);
    }
  };

  const handleDeleteManualHolding = async (holdingId) => {
    if (!activePortfolio) return;
    if (!confirm("Are you sure you want to remove this holding?")) return;
    try {
      await api.deleteManualHolding(activePortfolio.id, holdingId);
      refreshAllData();
    } catch (err) {
      alert("Error deleting holding: " + err.message);
    }
  };

  const openExplainForTicker = (ticker, eventDesc = '', priceChangePct = 0) => {
    setExplainParams({
      ticker,
      event: eventDesc || `${ticker} market volatility inquiry`,
      priceChangePct
    });
    setIsExplainModalOpen(true);
  };

  const openTradeForTicker = (ticker) => {
    setTradeDefaultTicker(ticker);
    setIsTradeModalOpen(true);
  };

  if (authLoading) {
    return (
      <div className="min-h-screen bg-zinc-950 flex items-center justify-center text-zinc-400 font-mono text-xs">
        Loading Apex Intelligence System...
      </div>
    );
  }

  // Auth Screen
  if (!user) {
    return (
      <div className="min-h-screen bg-zinc-950 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
        <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-indigo-600 to-cyan-400 mx-auto flex items-center justify-center shadow-lg shadow-indigo-500/25 mb-4">
            <Sparkles className="w-6 h-6 text-white" />
          </div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight">
            Apex Intelligence Platform
          </h1>
          <p className="mt-2 text-xs text-zinc-400">
            Decision-support, simulated trading, and grounded supply-chain RAG for investors.
          </p>
        </div>

        <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md px-4">
          <div className="bg-zinc-900 border border-zinc-800 py-8 px-6 shadow-2xl rounded-2xl sm:px-10">
            {authError && (
              <div className="mb-4 p-3 rounded-xl bg-rose-950/70 border border-rose-800 text-rose-300 text-xs">
                {authError}
              </div>
            )}

            <form className="space-y-4" onSubmit={handleLoginSubmit}>
              {authMode === 'register' && (
                <div>
                  <label className="block text-xs font-medium text-zinc-300">Full Name</label>
                  <input
                    type="text"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    required
                    className="mt-1 block w-full rounded-xl bg-zinc-950 border border-zinc-800 px-3 py-2 text-xs text-white focus:outline-none focus:ring-1 focus:ring-indigo-500"
                  />
                </div>
              )}

              <div>
                <label className="block text-xs font-medium text-zinc-300">Email Address</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="mt-1 block w-full rounded-xl bg-zinc-950 border border-zinc-800 px-3 py-2 text-xs text-white focus:outline-none focus:ring-1 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-zinc-300">Password</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="mt-1 block w-full rounded-xl bg-zinc-950 border border-zinc-800 px-3 py-2 text-xs text-white focus:outline-none focus:ring-1 focus:ring-indigo-500"
                />
              </div>

              <button
                type="submit"
                className="w-full mt-2 py-2.5 px-4 rounded-xl font-bold text-xs bg-indigo-600 hover:bg-indigo-500 text-white shadow-md shadow-indigo-600/30 transition flex items-center justify-center gap-1.5"
              >
                {authMode === 'login' ? 'Sign In' : 'Create Account'}
                <ArrowRight className="w-4 h-4" />
              </button>
            </form>

            <div className="mt-6 pt-4 border-t border-zinc-800 text-center">
              <button
                type="button"
                onClick={() => setAuthMode(authMode === 'login' ? 'register' : 'login')}
                className="text-xs text-indigo-400 hover:text-indigo-300 font-medium"
              >
                {authMode === 'login' 
                  ? "Don't have an account? Sign up" 
                  : "Already registered? Sign in"}
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 flex flex-col">
      {/* Navbar */}
      <Navbar
        user={user}
        portfolios={portfolios}
        activePortfolio={activePortfolio}
        onSelectPortfolio={setActivePortfolio}
        onOpenCreatePortfolio={() => setIsCreatePortOpen(true)}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onLogout={handleLogout}
      />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Tab Content */}
        {activeTab === 'overview' && (
          <div className="space-y-8">
            <PortfolioOverview
              valuation={valuation}
              portfolio={activePortfolio}
              onOpenTrade={() => setIsTradeModalOpen(true)}
              onExplainHolding={(ticker) => openExplainForTicker(ticker)}
              onOpenAddManual={() => setIsAddManualOpen(true)}
              onDeleteManualHolding={handleDeleteManualHolding}
            />

            {/* Quick Anomaly Alerts preview */}
            <AnomalyAlertsFeed
              alerts={alerts}
              onMarkRead={async (id) => {
                await api.markAlertRead(id);
                refreshAllData();
              }}
              onExplainAlert={(a) => openExplainForTicker(a.ticker, a.message, a.price_change_pct)}
            />
          </div>
        )}

        {activeTab === 'trading' && (
          <div className="space-y-8">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-base font-bold text-white tracking-tight">Simulated Trading & Cash Ledger</h2>
                <p className="text-xs text-zinc-400 mt-0.5">
                  Double-entry cash invariant ledger and limit order escrow management
                </p>
              </div>

              {activePortfolio?.type === 'VIRTUAL_TRADING' && (
                <button
                  onClick={() => setIsTradeModalOpen(true)}
                  className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs shadow-md shadow-indigo-600/30 transition flex items-center gap-1.5"
                >
                  <Plus className="w-4 h-4" />
                  Place Order
                </button>
              )}
            </div>

            {/* Orders History Table */}
            <div className="bg-zinc-900/60 border border-zinc-800 rounded-2xl overflow-hidden shadow-sm">
              <div className="px-6 py-4 border-b border-zinc-800">
                <h3 className="text-sm font-bold text-white uppercase tracking-wider">Order Execution Book</h3>
              </div>
              {orders.length === 0 ? (
                <div className="text-center py-10 text-xs text-zinc-500">
                  No trade orders submitted yet.
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-left border-collapse text-xs font-mono">
                    <thead>
                      <tr className="border-b border-zinc-800 bg-zinc-950/40 text-zinc-400">
                        <th className="py-3 px-6">Order ID</th>
                        <th className="py-3 px-4">Side</th>
                        <th className="py-3 px-4">Type</th>
                        <th className="py-3 px-4">Ticker</th>
                        <th className="py-3 px-4">Quantity</th>
                        <th className="py-3 px-4">Price</th>
                        <th className="py-3 px-4">Status</th>
                        <th className="py-3 px-4">Time</th>
                        <th className="py-3 px-6 text-right">Action</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-zinc-800/60">
                      {orders.map((o) => (
                        <tr key={o.id} className="hover:bg-zinc-800/30">
                          <td className="py-3 px-6 text-zinc-400">{o.id.slice(0, 8)}...</td>
                          <td className={`py-3 px-4 font-bold ${o.side === 'BUY' ? 'text-emerald-400' : 'text-rose-400'}`}>
                            {o.side}
                          </td>
                          <td className="py-3 px-4 text-zinc-300">{o.type}</td>
                          <td className="py-3 px-4 font-bold text-white">{o.ticker}</td>
                          <td className="py-3 px-4 text-zinc-200">{o.quantity}</td>
                          <td className="py-3 px-4 text-zinc-200">
                            {o.execution_price ? `$${o.execution_price.toFixed(2)}` : (o.limit_price ? `$${o.limit_price.toFixed(2)}` : '—')}
                          </td>
                          <td className="py-3 px-4">
                            <span className={`text-[10px] px-2 py-0.5 rounded font-bold ${
                              o.status === 'FILLED' ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' :
                              o.status === 'PENDING' ? 'bg-amber-950 text-amber-400 border border-amber-800' :
                              'bg-zinc-800 text-zinc-400'
                            }`}>
                              {o.status}
                            </span>
                          </td>
                          <td className="py-3 px-4 text-zinc-500 text-[11px]">
                            {new Date(o.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </td>
                          <td className="py-3 px-6 text-right">
                            {o.status === 'PENDING' && (
                              <button
                                onClick={async () => {
                                  await api.cancelOrder(activePortfolio.id, o.id);
                                  refreshAllData();
                                }}
                                className="px-2 py-1 rounded bg-rose-950 text-rose-300 border border-rose-800 hover:bg-rose-900 text-[11px] font-sans"
                              >
                                Cancel Order
                              </button>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>

            {/* Cash Transactions Double-Entry Ledger */}
            <div className="bg-zinc-900/60 border border-zinc-800 rounded-2xl overflow-hidden shadow-sm">
              <div className="px-6 py-4 border-b border-zinc-800">
                <h3 className="text-sm font-bold text-white uppercase tracking-wider">Cash Transactions Ledger (Audit Trail)</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse text-xs font-mono">
                  <thead>
                    <tr className="border-b border-zinc-800 bg-zinc-950/40 text-zinc-400">
                      <th className="py-3 px-6">Timestamp</th>
                      <th className="py-3 px-4">Transaction Type</th>
                      <th className="py-3 px-4">Amount</th>
                      <th className="py-3 px-4">Balance After</th>
                      <th className="py-3 px-6">Description</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-zinc-800/60">
                    {transactions.map((tx) => {
                      const isCredit = tx.amount >= 0;
                      return (
                        <tr key={tx.id} className="hover:bg-zinc-800/30">
                          <td className="py-3 px-6 text-zinc-400 text-[11px]">
                            {new Date(tx.created_at).toLocaleString()}
                          </td>
                          <td className="py-3 px-4">
                            <span className="text-[10px] px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-300">
                              {tx.transaction_type}
                            </span>
                          </td>
                          <td className={`py-3 px-4 font-bold ${isCredit ? 'text-emerald-400' : 'text-rose-400'}`}>
                            {isCredit ? '+' : ''}${Math.abs(tx.amount).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                          </td>
                          <td className="py-3 px-4 text-white font-semibold">
                            ${tx.balance_after.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                          </td>
                          <td className="py-3 px-6 text-zinc-400 font-sans text-xs">
                            {tx.description}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'market' && (
          <MarketWatch
            quotes={quotes}
            news={news}
            onAnomalyInjected={refreshAllData}
            onExplainTicker={(ticker) => openExplainForTicker(ticker)}
            onTradeTicker={openTradeForTicker}
          />
        )}

        {activeTab === 'risk' && (
          <RiskAnalyticsCard portfolio={activePortfolio} />
        )}

        {activeTab === 'journal' && (
          <InvestmentJournal portfolio={activePortfolio} quotes={quotes} />
        )}
      </main>

      {/* Trade Order Modal */}
      <TradeOrderModal
        isOpen={isTradeModalOpen}
        onClose={() => setIsTradeModalOpen(false)}
        portfolio={activePortfolio}
        quotes={quotes}
        defaultTicker={tradeDefaultTicker}
        onOrderSuccess={refreshAllData}
      />

      {/* Explain Impact AI Modal */}
      <ExplainImpactModal
        isOpen={isExplainModalOpen}
        onClose={() => setIsExplainModalOpen(false)}
        portfolio={activePortfolio}
        ticker={explainParams.ticker}
        eventDescription={explainParams.event}
        priceChangePct={explainParams.priceChangePct}
      />

      {/* Create Portfolio Modal */}
      {isCreatePortOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 max-w-sm w-full space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">Create New Portfolio</h3>
              <button onClick={() => setIsCreatePortOpen(false)} className="text-zinc-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreatePortfolio} className="space-y-3">
              <div>
                <label className="block text-[11px] text-zinc-400 mb-1">Portfolio Name</label>
                <input
                  type="text"
                  placeholder="e.g. AI Momentum Fund"
                  value={newPortName}
                  onChange={(e) => setNewPortName(e.target.value)}
                  required
                  className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:ring-1 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label className="block text-[11px] text-zinc-400 mb-1">Account Mode</label>
                <select
                  value={newPortType}
                  onChange={(e) => setNewPortType(e.target.value)}
                  className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:ring-1 focus:ring-indigo-500"
                >
                  <option value="VIRTUAL_TRADING">Simulated Paper Trading ($100k balance)</option>
                  <option value="MANUAL_TRACKING">External Watch Portfolio (Manual CRUD)</option>
                </select>
              </div>

              <button
                type="submit"
                className="w-full py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs shadow-md transition"
              >
                Create Portfolio
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Add Manual Holding Modal */}
      {isAddManualOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 max-w-sm w-full space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">Add External Holding</h3>
              <button onClick={() => setIsAddManualOpen(false)} className="text-zinc-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleAddManualHolding} className="space-y-3">
              <div>
                <label className="block text-[11px] text-zinc-400 mb-1">Asset Ticker</label>
                <input
                  type="text"
                  placeholder="AAPL"
                  value={manualTicker}
                  onChange={(e) => setManualTicker(e.target.value)}
                  required
                  className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-3 py-2 text-xs font-mono font-bold text-white focus:outline-none focus:ring-1 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label className="block text-[11px] text-zinc-400 mb-1">Shares Quantity</label>
                <input
                  type="number"
                  step="any"
                  value={manualQty}
                  onChange={(e) => setManualQty(e.target.value)}
                  required
                  className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-3 py-2 text-xs font-mono text-white focus:outline-none focus:ring-1 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label className="block text-[11px] text-zinc-400 mb-1">Cost Basis Per Share ($)</label>
                <input
                  type="number"
                  step="any"
                  value={manualCost}
                  onChange={(e) => setManualCost(e.target.value)}
                  required
                  className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-3 py-2 text-xs font-mono text-white focus:outline-none focus:ring-1 focus:ring-indigo-500"
                />
              </div>

              <button
                type="submit"
                className="w-full py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs shadow-md transition"
              >
                Add Position
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
