import React, { useState, useEffect } from 'react';
import { 
  BarChart3, 
  ShieldCheck, 
  AlertTriangle, 
  Activity, 
  TrendingUp, 
  Percent,
  RefreshCw
} from 'lucide-react';
import { api } from '../api';

export default function RiskAnalyticsCard({ portfolio }) {
  const [risk, setRisk] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchRisk = () => {
    if (!portfolio) return;
    setLoading(true);
    setError('');
    api.getPortfolioRisk(portfolio.id)
      .then((data) => {
        setRisk(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchRisk();
  }, [portfolio?.id]);

  if (!portfolio) return null;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-base font-bold text-white tracking-tight">Portfolio Risk & Exposure Diagnostics</h2>
          <p className="text-xs text-zinc-400 mt-0.5">
            Statistical calculations: Concentration (HHI), Systematic Beta, Volatility, and Parametric 95% VaR
          </p>
        </div>
        <button
          onClick={fetchRisk}
          disabled={loading}
          className="px-3 py-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-300 text-xs font-medium transition flex items-center gap-1.5"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          Recalculate
        </button>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-950/60 border border-rose-800 text-rose-300 text-xs">
          {error}
        </div>
      )}

      {/* Grid of Risk Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Concentration HHI */}
        <div className="bg-zinc-900/60 border border-zinc-800 rounded-2xl p-5 shadow-sm">
          <div className="flex items-center justify-between text-zinc-400 text-xs mb-2">
            <span>Concentration (HHI)</span>
            <span className={`text-[10px] font-mono px-1.5 py-0.2 rounded font-bold ${
              risk?.is_high_concentration
                ? 'bg-rose-950 text-rose-400 border border-rose-800'
                : 'bg-emerald-950 text-emerald-400 border border-emerald-800'
            }`}>
              {risk?.is_high_concentration ? 'HIGH CONCENTRATION' : 'BALANCED'}
            </span>
          </div>

          <div className="text-2xl font-bold font-mono text-white">
            {risk ? risk.concentration_hhi.toFixed(4) : '—'}
          </div>

          <div className="mt-3 text-xs text-zinc-400">
            Top 3 Holdings: <span className="font-semibold text-zinc-200">{risk ? risk.top_3_concentration_pct.toFixed(1) : 0}%</span>
          </div>
          <p className="text-[11px] text-zinc-500 mt-1">
            Scores &gt; 0.25 indicate elevated single-stock dependency.
          </p>
        </div>

        {/* Portfolio Beta */}
        <div className="bg-zinc-900/60 border border-zinc-800 rounded-2xl p-5 shadow-sm">
          <div className="flex items-center justify-between text-zinc-400 text-xs mb-2">
            <span>Systematic Beta</span>
            <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-zinc-800 text-zinc-300">
              Benchmark: SPY
            </span>
          </div>

          <div className="text-2xl font-bold font-mono text-white">
            {risk ? risk.portfolio_beta.toFixed(2) : '—'}
          </div>

          <div className="mt-3 text-xs text-zinc-400">
            {risk?.portfolio_beta > 1.0 ? 'More volatile than market' : 'Defensive / Cash protected'}
          </div>
          <p className="text-[11px] text-zinc-500 mt-1">
            Beta &gt; 1.0 amplifies S&P 500 swings; Beta &lt; 1.0 dampens shocks.
          </p>
        </div>

        {/* Annualized Volatility */}
        <div className="bg-zinc-900/60 border border-zinc-800 rounded-2xl p-5 shadow-sm">
          <div className="flex items-center justify-between text-zinc-400 text-xs mb-2">
            <span>Realized Volatility</span>
            <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-zinc-800 text-zinc-300">
              Annualized
            </span>
          </div>

          <div className="text-2xl font-bold font-mono text-indigo-400">
            {risk ? `${risk.annualized_volatility.toFixed(1)}%` : '—'}
          </div>

          <div className="mt-3 text-xs text-zinc-400">
            Weighted 30-day standard deviation
          </div>
          <p className="text-[11px] text-zinc-500 mt-1">
            Normal market range: 15%–25%. Tech-heavy portfolios range 30%–45%.
          </p>
        </div>

        {/* Value at Risk (VaR 95% 1-day) */}
        <div className="bg-zinc-900/60 border border-zinc-800 rounded-2xl p-5 shadow-sm">
          <div className="flex items-center justify-between text-zinc-400 text-xs mb-2">
            <span>Value at Risk (95% 1-Day)</span>
            <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-rose-950 text-rose-300 border border-rose-800">
              95% Confidence
            </span>
          </div>

          <div className="text-2xl font-bold font-mono text-rose-400">
            ${risk ? risk.value_at_risk_95_1d.toLocaleString(undefined, { minimumFractionDigits: 2 }) : '—'}
          </div>

          <div className="mt-3 text-xs text-zinc-400">
            Maximum expected 1-day loss in 19 out of 20 market sessions.
          </div>
          <p className="text-[11px] text-zinc-500 mt-1">
            Parametric formula: 1.645 × daily volatility × total equity.
          </p>
        </div>
      </div>
    </div>
  );
}
