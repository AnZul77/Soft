import React, { useState } from 'react';
import { 
  DollarSign, 
  TrendingUp, 
  TrendingDown, 
  Lock, 
  Wallet, 
  ArrowUpRight, 
  Sparkles, 
  Plus, 
  Trash2,
  AlertCircle,
  BarChart2,
  Edit3,
  Check,
  X,
  ShieldCheck,
  Clock
} from 'lucide-react';

export default function PortfolioOverview({ 
  valuation, 
  portfolio, 
  onOpenTrade, 
  onExplainHolding, 
  onOpenAddManual, 
  onDeleteManualHolding,
  onViewChart,
  onRenamePortfolio,
  onDeletePortfolio,
  onNavigateTab
}) {
  const [isEditingName, setIsEditingName] = useState(false);
  const [editedName, setEditedName] = useState('');

  if (!portfolio) {
    return (
      <div className="text-center py-16 bg-[#10141d]/80 border border-[#1e2638] rounded-2xl">
        <p className="text-slate-400 text-sm">Please select or create a portfolio to view holdings.</p>
      </div>
    );
  }

  const holdings = valuation?.holdings || [];
  const isVirtual = portfolio.type === 'VIRTUAL_TRADING';
  const totalEquity = valuation?.total_equity || (valuation?.virtual_cash_balance || 0);
  const unrealizedPl = valuation?.total_unrealized_pl || 0;
  const unrealizedPlPct = valuation?.total_unrealized_pl_pct || 0;
  const isPositivePl = unrealizedPl >= 0;

  return (
    <div className="space-y-6">
      {/* Top Banner Stats - Institutional Financial Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Equity */}
        <div className="bg-[#10141d] border border-[#1e2638] hover:border-[#2a364f] rounded-2xl p-5 relative overflow-hidden shadow-sm transition-all group">
          <div className="absolute top-0 inset-x-0 h-[2px] bg-gradient-to-r from-transparent via-indigo-500/40 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold uppercase tracking-wider mb-2">
            <span>Total Equity</span>
            <div className="w-8 h-8 rounded-xl bg-[#141925] border border-slate-800 flex items-center justify-center text-indigo-400">
              <DollarSign className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-extrabold text-white font-mono tracking-tight">
            ${totalEquity.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <div className="text-[11px] text-slate-400 mt-2 flex items-center justify-between font-mono">
            <span>Currency: <strong className="text-slate-200">{portfolio.base_currency}</strong></span>
            <span className="text-[10px] text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded border border-emerald-500/20 font-bold">LIVE VALUED</span>
          </div>
        </div>

        {/* Unrealized P&L */}
        <div className="bg-[#10141d] border border-[#1e2638] hover:border-[#2a364f] rounded-2xl p-5 relative overflow-hidden shadow-sm transition-all group">
          <div className="absolute top-0 inset-x-0 h-[2px] bg-gradient-to-r from-transparent via-indigo-500/40 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold uppercase tracking-wider mb-2">
            <span>Unrealized P&L</span>
            <div className={`w-8 h-8 rounded-xl flex items-center justify-center border ${
              isPositivePl ? 'bg-emerald-950/60 text-emerald-400 border-emerald-800/80' : 'bg-rose-950/60 text-rose-400 border-rose-800/80'
            }`}>
              {isPositivePl ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
            </div>
          </div>
          <div className={`text-2xl font-extrabold font-mono tracking-tight ${
            isPositivePl ? 'text-emerald-400' : 'text-rose-400'
          }`}>
            {isPositivePl ? '+' : ''}${unrealizedPl.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <div className={`text-[11px] font-mono mt-2 font-semibold flex items-center gap-1.5 ${
            isPositivePl ? 'text-emerald-400' : 'text-rose-400'
          }`}>
            <span>{isPositivePl ? '+' : ''}{unrealizedPlPct.toFixed(2)}% net return</span>
          </div>
        </div>

        {/* Available Cash */}
        <div className="bg-[#10141d] border border-[#1e2638] hover:border-[#2a364f] rounded-2xl p-5 relative overflow-hidden shadow-sm transition-all group">
          <div className="absolute top-0 inset-x-0 h-[2px] bg-gradient-to-r from-transparent via-indigo-500/40 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold uppercase tracking-wider mb-2">
            <span>{isVirtual ? 'Buying Power' : 'Untracked Balance'}</span>
            <div className="w-8 h-8 rounded-xl bg-[#141925] border border-slate-800 flex items-center justify-center text-cyan-400">
              <Wallet className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-extrabold text-white font-mono tracking-tight">
            ${(valuation?.virtual_cash_balance || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <div className="text-[11px] text-slate-400 mt-2 flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
            <span>{isVirtual ? 'Double-Entry Ledger Verified' : 'Manual Portfolio Mode'}</span>
          </div>
        </div>

        {/* Escrow Reserved Cash */}
        <div className="bg-[#10141d] border border-[#1e2638] hover:border-[#2a364f] rounded-2xl p-5 relative overflow-hidden shadow-sm transition-all group">
          <div className="absolute top-0 inset-x-0 h-[2px] bg-gradient-to-r from-transparent via-indigo-500/40 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold uppercase tracking-wider mb-2">
            <span>Escrow Reserved</span>
            <div className="w-8 h-8 rounded-xl bg-[#141925] border border-slate-800 flex items-center justify-center text-amber-400">
              <Lock className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-extrabold text-amber-400 font-mono tracking-tight">
            ${(valuation?.reserved_cash || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <div className="text-[11px] text-slate-400 mt-2 flex items-center gap-1.5">
            <Clock className="w-3.5 h-3.5 text-amber-500/80" />
            <span>Committed to Pending Limit Buys</span>
          </div>
        </div>
      </div>

      {/* Holdings Section */}
      <div className="bg-[#10141d] border border-[#1e2638] rounded-2xl overflow-hidden shadow-sm">
        <div className="px-6 py-4 border-b border-[#1e2638] flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-[#0c1017]/50">
          <div>
            {isEditingName ? (
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  value={editedName}
                  onChange={(e) => setEditedName(e.target.value)}
                  className="bg-[#141925] border border-slate-700 rounded-lg px-2.5 py-1 text-xs text-white font-bold focus:outline-none focus:ring-1 focus:ring-indigo-500"
                  autoFocus
                />
                <button
                  onClick={async () => {
                    if (editedName.trim() && onRenamePortfolio) {
                      await onRenamePortfolio(portfolio.id, editedName.trim());
                    }
                    setIsEditingName(false);
                  }}
                  title="Save Name"
                  className="p-1 rounded bg-indigo-600 hover:bg-indigo-500 text-white transition"
                >
                  <Check className="w-3.5 h-3.5" />
                </button>
                <button
                  onClick={() => setIsEditingName(false)}
                  title="Cancel"
                  className="p-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-400 transition"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <h2 className="text-sm font-bold text-white uppercase tracking-wider">
                  {portfolio.name} — Asset Breakdown
                </h2>
                {onRenamePortfolio && (
                  <button
                    onClick={() => {
                      setEditedName(portfolio.name);
                      setIsEditingName(true);
                    }}
                    title="Rename Portfolio"
                    className="p-1 rounded text-slate-400 hover:text-white hover:bg-slate-800 transition"
                  >
                    <Edit3 className="w-3.5 h-3.5" />
                  </button>
                )}
                {onDeletePortfolio && (
                  <button
                    onClick={() => {
                      if (confirm(`Are you sure you want to delete portfolio "${portfolio.name}"? Historical orders and cash transactions will remain safely archived.`)) {
                        onDeletePortfolio(portfolio.id);
                      }
                    }}
                    title="Soft Delete Portfolio"
                    className="p-1 rounded text-slate-500 hover:text-rose-400 hover:bg-slate-800 transition"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>
            )}
            <p className="text-xs text-slate-400 mt-0.5">Real-time market valuation with fallback validation</p>
          </div>

          <div className="flex items-center gap-2">
            {isVirtual ? (
              <button
                onClick={onOpenTrade}
                className="px-3.5 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md shadow-indigo-600/25 transition flex items-center gap-1.5"
              >
                <ArrowUpRight className="w-3.5 h-3.5" />
                New Trade Order
              </button>
            ) : (
              <button
                onClick={onOpenAddManual}
                className="px-3.5 py-1.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold shadow-md shadow-cyan-600/25 transition flex items-center gap-1.5"
              >
                <Plus className="w-3.5 h-3.5" />
                Add External Holding
              </button>
            )}
          </div>
        </div>

        {holdings.length === 0 ? (
          <div className="py-16 px-6 text-center">
            <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center mx-auto text-indigo-400 mb-3 shadow-inner">
              <Sparkles className="w-6 h-6" />
            </div>
            <h3 className="text-sm font-bold text-white tracking-tight">Portfolio Ready for Allocation</h3>
            <p className="text-xs text-slate-400 max-w-md mx-auto mt-1 leading-relaxed">
              {isVirtual 
                ? "This simulated trading account has $100,000.00 cash available. Execute a market or limit order to start tracking asset performance." 
                : "Manually add external holdings with cost bases to track asset valuation and market volatility."}
            </p>
            <div className="mt-5 flex items-center justify-center gap-3">
              {isVirtual ? (
                <button
                  onClick={onOpenTrade}
                  className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs shadow-md shadow-indigo-600/30 transition flex items-center gap-1.5"
                >
                  <ArrowUpRight className="w-4 h-4" />
                  Execute First Trade
                </button>
              ) : (
                <button
                  onClick={onOpenAddManual}
                  className="px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-xs shadow-md shadow-cyan-600/30 transition flex items-center gap-1.5"
                >
                  <Plus className="w-4 h-4" />
                  Add First Holding
                </button>
              )}
            </div>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="border-b border-[#1e2638] bg-[#090c10]/60 text-slate-400 font-semibold uppercase tracking-wider text-[11px]">
                  <th className="py-3.5 px-6">Ticker</th>
                  <th className="py-3.5 px-4">Portfolio Weight</th>
                  <th className="py-3.5 px-4">Shares</th>
                  <th className="py-3.5 px-4">Cost Basis</th>
                  <th className="py-3.5 px-4">Current Price</th>
                  <th className="py-3.5 px-4">Market Value</th>
                  <th className="py-3.5 px-4">Unrealized P&L</th>
                  <th className="py-3.5 px-6 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1e2638]/70 font-mono">
                {holdings.map((h) => {
                  const isGain = h.unrealized_pl >= 0;
                  return (
                    <tr key={h.holding_id} className="hover:bg-[#141925]/70 transition-colors">
                      <td className="py-3.5 px-6 font-bold text-white flex items-center gap-2 font-mono">
                        <span className="text-sm font-extrabold">{h.ticker}</span>
                        {h.is_stale && (
                          <span className="text-[9px] px-1.5 py-0.5 rounded bg-amber-950/70 text-amber-400 border border-amber-800" title="Using cached or cost basis fallback price">
                            STALE
                          </span>
                        )}
                        <span className="text-[9px] font-sans px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700/60">
                          {h.price_source}
                        </span>
                      </td>

                      <td className="py-3.5 px-4">
                        <div className="flex items-center gap-2">
                          <span className="w-10 text-slate-300 font-semibold">{h.weight_pct.toFixed(1)}%</span>
                          <div className="w-16 h-1.5 bg-slate-800 rounded-full overflow-hidden hidden sm:block">
                            <div 
                              className="h-full bg-gradient-to-r from-indigo-500 to-cyan-400 rounded-full" 
                              style={{ width: `${Math.min(100, h.weight_pct)}%` }}
                            />
                          </div>
                        </div>
                      </td>

                      <td className="py-3.5 px-4 text-slate-200">{h.quantity}</td>
                      <td className="py-3.5 px-4 text-slate-300">${h.cost_basis.toFixed(2)}</td>
                      <td className="py-3.5 px-4 font-semibold text-white">${h.current_price.toFixed(2)}</td>
                      <td className="py-3.5 px-4 text-slate-200">${h.market_value.toLocaleString(undefined, { minimumFractionDigits: 2 })}</td>
                      
                      <td className={`py-3.5 px-4 font-semibold ${isGain ? 'text-emerald-400' : 'text-rose-400'}`}>
                        {isGain ? '+' : ''}${h.unrealized_pl.toFixed(2)} ({isGain ? '+' : ''}{h.unrealized_pl_pct.toFixed(2)}%)
                      </td>

                      <td className="py-3.5 px-6 text-right">
                        <div className="flex items-center justify-end gap-2 font-sans">
                          {onViewChart && (
                            <button
                              onClick={() => onViewChart(h.ticker)}
                              title="View Interactive Price Chart"
                              className="px-2.5 py-1 rounded-lg bg-[#141925] hover:bg-slate-800 border border-slate-700/80 text-slate-200 text-[11px] font-medium transition flex items-center gap-1 shadow-sm"
                            >
                              <BarChart2 className="w-3 h-3 text-cyan-400" />
                              Chart
                            </button>
                          )}

                          <button
                            onClick={() => onExplainHolding(h.ticker)}
                            title="Explain Impact with AI RAG"
                            className="px-2.5 py-1 rounded-lg bg-indigo-500/10 hover:bg-indigo-500/20 border border-indigo-500/30 text-indigo-300 text-[11px] font-semibold transition flex items-center gap-1 shadow-sm"
                          >
                            <Sparkles className="w-3 h-3 text-indigo-400" />
                            Explain AI
                          </button>

                          {!isVirtual && (
                            <button
                              onClick={() => onDeleteManualHolding(h.holding_id)}
                              title="Delete position"
                              className="p-1 rounded text-slate-400 hover:text-rose-400 hover:bg-slate-800 transition"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
