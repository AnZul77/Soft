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
  X
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
  onDeletePortfolio
}) {
  const [isEditingName, setIsEditingName] = useState(false);
  const [editedName, setEditedName] = useState('');
  if (!portfolio) {
    return (
      <div className="text-center py-16 bg-zinc-900/40 border border-zinc-800 rounded-2xl">
        <p className="text-zinc-400 text-sm">Please select or create a portfolio to view holdings.</p>
      </div>
    );
  }

  const holdings = valuation?.holdings || [];
  const isVirtual = portfolio.type === 'VIRTUAL_TRADING';
  const totalEquity = valuation?.total_equity || 0;
  const unrealizedPl = valuation?.total_unrealized_pl || 0;
  const unrealizedPlPct = valuation?.total_unrealized_pl_pct || 0;
  const isPositivePl = unrealizedPl >= 0;

  return (
    <div className="space-y-6">
      {/* Top Banner Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Equity */}
        <div className="bg-zinc-900/70 border border-zinc-800/80 rounded-2xl p-5 relative overflow-hidden shadow-sm backdrop-blur-sm">
          <div className="flex items-center justify-between text-zinc-400 text-xs font-medium mb-2">
            <span>Total Equity</span>
            <div className="w-7 h-7 rounded-lg bg-zinc-800 flex items-center justify-center text-zinc-300">
              <DollarSign className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-extrabold text-white font-mono tracking-tight">
            ${totalEquity.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <div className="text-[11px] text-zinc-400 mt-2 flex items-center gap-1 font-mono">
            Currency: <span className="text-zinc-200 font-semibold">{portfolio.base_currency}</span>
          </div>
        </div>

        {/* Unrealized P&L */}
        <div className="bg-zinc-900/70 border border-zinc-800/80 rounded-2xl p-5 relative overflow-hidden shadow-sm backdrop-blur-sm">
          <div className="flex items-center justify-between text-zinc-400 text-xs font-medium mb-2">
            <span>Unrealized P&L</span>
            <div className={`w-7 h-7 rounded-lg flex items-center justify-center ${
              isPositivePl ? 'bg-emerald-950/80 text-emerald-400' : 'bg-rose-950/80 text-rose-400'
            }`}>
              {isPositivePl ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
            </div>
          </div>
          <div className={`text-2xl font-extrabold font-mono tracking-tight ${
            isPositivePl ? 'text-emerald-400' : 'text-rose-400'
          }`}>
            {isPositivePl ? '+' : ''}${unrealizedPl.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <div className={`text-[11px] font-mono mt-2 font-semibold ${
            isPositivePl ? 'text-emerald-400' : 'text-rose-400'
          }`}>
            {isPositivePl ? '+' : ''}{unrealizedPlPct.toFixed(2)}% overall return
          </div>
        </div>

        {/* Available Cash */}
        <div className="bg-zinc-900/70 border border-zinc-800/80 rounded-2xl p-5 relative overflow-hidden shadow-sm backdrop-blur-sm">
          <div className="flex items-center justify-between text-zinc-400 text-xs font-medium mb-2">
            <span>{isVirtual ? 'Available Cash' : 'Untracked Balance'}</span>
            <div className="w-7 h-7 rounded-lg bg-zinc-800 flex items-center justify-center text-zinc-300">
              <Wallet className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-extrabold text-white font-mono tracking-tight">
            ${(valuation?.virtual_cash_balance || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <div className="text-[11px] text-zinc-400 mt-2">
            {isVirtual ? 'Strict Double-Entry Ledger' : 'Manual Portfolio Mode'}
          </div>
        </div>

        {/* Escrow Reserved Cash */}
        <div className="bg-zinc-900/70 border border-zinc-800/80 rounded-2xl p-5 relative overflow-hidden shadow-sm backdrop-blur-sm">
          <div className="flex items-center justify-between text-zinc-400 text-xs font-medium mb-2">
            <span>Escrow Reserved</span>
            <div className="w-7 h-7 rounded-lg bg-zinc-800 flex items-center justify-center text-zinc-300">
              <Lock className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-extrabold text-amber-400 font-mono tracking-tight">
            ${(valuation?.reserved_cash || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <div className="text-[11px] text-zinc-400 mt-2">
            Locked for Pending Limit Buys
          </div>
        </div>
      </div>

      {/* Holdings Section */}
      <div className="bg-zinc-900/60 border border-zinc-800 rounded-2xl overflow-hidden shadow-sm">
        <div className="px-6 py-4 border-b border-zinc-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            {isEditingName ? (
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  value={editedName}
                  onChange={(e) => setEditedName(e.target.value)}
                  className="bg-zinc-950 border border-zinc-700 rounded-lg px-2.5 py-1 text-xs text-white font-bold focus:outline-none focus:ring-1 focus:ring-indigo-500"
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
                  className="p-1 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-400 transition"
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
                    className="p-1 rounded text-zinc-400 hover:text-white hover:bg-zinc-800 transition"
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
                    className="p-1 rounded text-zinc-500 hover:text-rose-400 hover:bg-zinc-800 transition"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>
            )}
            <p className="text-xs text-zinc-400 mt-0.5">Real-time market valuation with fallback validation</p>
          </div>

          <div className="flex items-center gap-2">
            {isVirtual ? (
              <button
                onClick={onOpenTrade}
                className="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md shadow-indigo-600/20 transition flex items-center gap-1.5"
              >
                <ArrowUpRight className="w-3.5 h-3.5" />
                New Trade Order
              </button>
            ) : (
              <button
                onClick={onOpenAddManual}
                className="px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-md shadow-blue-600/20 transition flex items-center gap-1.5"
              >
                <Plus className="w-3.5 h-3.5" />
                Add External Holding
              </button>
            )}
          </div>
        </div>

        {holdings.length === 0 ? (
          <div className="text-center py-12 px-4">
            <div className="w-12 h-12 rounded-2xl bg-zinc-800 flex items-center justify-center mx-auto text-zinc-500 mb-3">
              <AlertCircle className="w-6 h-6" />
            </div>
            <h3 className="text-sm font-semibold text-zinc-300">No active holdings in this portfolio</h3>
            <p className="text-xs text-zinc-500 max-w-sm mx-auto mt-1">
              {isVirtual 
                ? "Execute a virtual trade order via the Trade Desk to populate your portfolio." 
                : "Manually add external holdings with cost bases to track asset valuation."}
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="border-b border-zinc-800 bg-zinc-950/40 text-zinc-400 font-medium">
                  <th className="py-3 px-6">Ticker</th>
                  <th className="py-3 px-4">Weight</th>
                  <th className="py-3 px-4">Shares</th>
                  <th className="py-3 px-4">Cost Basis</th>
                  <th className="py-3 px-4">Current Price</th>
                  <th className="py-3 px-4">Market Value</th>
                  <th className="py-3 px-4">Unrealized P&L</th>
                  <th className="py-3 px-6 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-800/60 font-mono">
                {holdings.map((h) => {
                  const isGain = h.unrealized_pl >= 0;
                  return (
                    <tr key={h.holding_id} className="hover:bg-zinc-800/30 transition-colors">
                      <td className="py-3.5 px-6 font-bold text-white flex items-center gap-2">
                        <span>{h.ticker}</span>
                        {h.is_stale && (
                          <span className="text-[9px] px-1.5 py-0.2 rounded bg-amber-950/70 text-amber-400 border border-amber-800" title="Using cached or cost basis fallback price">
                            STALE
                          </span>
                        )}
                        <span className="text-[9px] font-sans px-1.5 py-0.2 rounded bg-zinc-800 text-zinc-400">
                          {h.price_source}
                        </span>
                      </td>

                      <td className="py-3.5 px-4">
                        <div className="flex items-center gap-2">
                          <span className="w-10 text-zinc-300">{h.weight_pct.toFixed(1)}%</span>
                          <div className="w-16 h-1.5 bg-zinc-800 rounded-full overflow-hidden hidden sm:block">
                            <div 
                              className="h-full bg-indigo-500 rounded-full" 
                              style={{ width: `${Math.min(100, h.weight_pct)}%` }}
                            />
                          </div>
                        </div>
                      </td>

                      <td className="py-3.5 px-4 text-zinc-200">{h.quantity}</td>
                      <td className="py-3.5 px-4 text-zinc-300">${h.cost_basis.toFixed(2)}</td>
                      <td className="py-3.5 px-4 font-semibold text-white">${h.current_price.toFixed(2)}</td>
                      <td className="py-3.5 px-4 text-zinc-200">${h.market_value.toLocaleString(undefined, { minimumFractionDigits: 2 })}</td>
                      
                      <td className={`py-3.5 px-4 font-semibold ${isGain ? 'text-emerald-400' : 'text-rose-400'}`}>
                        {isGain ? '+' : ''}${h.unrealized_pl.toFixed(2)} ({isGain ? '+' : ''}{h.unrealized_pl_pct.toFixed(2)}%)
                      </td>

                      <td className="py-3.5 px-6 text-right">
                        <div className="flex items-center justify-end gap-2 font-sans">
                          {onViewChart && (
                            <button
                              onClick={() => onViewChart(h.ticker)}
                              title="View Interactive Price Chart"
                              className="px-2.5 py-1 rounded-md bg-zinc-800/80 hover:bg-zinc-700 border border-zinc-700/60 text-zinc-300 text-[11px] font-medium transition flex items-center gap-1"
                            >
                              <BarChart2 className="w-3 h-3 text-cyan-400" />
                              Chart
                            </button>
                          )}

                          <button
                            onClick={() => onExplainHolding(h.ticker)}
                            title="Explain Impact with AI"
                            className="px-2.5 py-1 rounded-md bg-indigo-950/60 hover:bg-indigo-900 border border-indigo-700/60 text-indigo-300 text-[11px] font-medium transition flex items-center gap-1"
                          >
                            <Sparkles className="w-3 h-3 text-indigo-400" />
                            Explain AI
                          </button>

                          {!isVirtual && (
                            <button
                              onClick={() => onDeleteManualHolding(h.holding_id)}
                              title="Delete position"
                              className="p-1 rounded text-zinc-400 hover:text-rose-400 hover:bg-zinc-800 transition"
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
