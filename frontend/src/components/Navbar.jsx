import React from 'react';
import { 
  TrendingUp, 
  ShieldCheck, 
  Layers, 
  Activity, 
  BookOpen, 
  BarChart3, 
  PlusCircle, 
  LogOut,
  Sparkles
} from 'lucide-react';

export default function Navbar({ 
  user, 
  portfolios, 
  activePortfolio, 
  onSelectPortfolio, 
  onOpenCreatePortfolio, 
  activeTab, 
  setActiveTab, 
  onLogout 
}) {
  return (
    <header className="border-b border-zinc-800 bg-zinc-950/80 backdrop-blur-md sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand */}
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-cyan-400 flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <span className="font-extrabold text-base tracking-tight bg-gradient-to-r from-white via-zinc-200 to-zinc-400 bg-clip-text text-transparent">
                APEX INTELLIGENCE
              </span>
              <span className="ml-2 text-[10px] font-mono uppercase px-1.5 py-0.5 rounded bg-indigo-950/60 border border-indigo-700/50 text-indigo-300">
                v1.0 RAG
              </span>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center gap-1 bg-zinc-900/60 p-1 rounded-xl border border-zinc-800/80">
            <button
              onClick={() => setActiveTab('overview')}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5 ${
                activeTab === 'overview'
                  ? 'bg-zinc-800 text-white shadow-sm'
                  : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/40'
              }`}
            >
              <Layers className="w-3.5 h-3.5" />
              Overview
            </button>
            <button
              onClick={() => setActiveTab('trading')}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5 ${
                activeTab === 'trading'
                  ? 'bg-zinc-800 text-white shadow-sm'
                  : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/40'
              }`}
            >
              <TrendingUp className="w-3.5 h-3.5" />
              Trade Desk
            </button>
            <button
              onClick={() => setActiveTab('market')}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5 ${
                activeTab === 'market'
                  ? 'bg-zinc-800 text-white shadow-sm'
                  : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/40'
              }`}
            >
              <Activity className="w-3.5 h-3.5" />
              Market & Anomalies
            </button>
            <button
              onClick={() => setActiveTab('risk')}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5 ${
                activeTab === 'risk'
                  ? 'bg-zinc-800 text-white shadow-sm'
                  : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/40'
              }`}
            >
              <BarChart3 className="w-3.5 h-3.5" />
              Risk Metrics
            </button>
            <button
              onClick={() => setActiveTab('journal')}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5 ${
                activeTab === 'journal'
                  ? 'bg-zinc-800 text-white shadow-sm'
                  : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/40'
              }`}
            >
              <BookOpen className="w-3.5 h-3.5" />
              Thesis Journal
            </button>
          </nav>

          {/* Right Controls */}
          <div className="flex items-center gap-3">
            {/* Portfolio Selector */}
            {portfolios.length > 0 && (
              <div className="flex items-center gap-2">
                <select
                  value={activePortfolio?.id || ''}
                  onChange={(e) => {
                    const selected = portfolios.find(p => p.id === e.target.value);
                    if (selected) onSelectPortfolio(selected);
                  }}
                  className="bg-zinc-900 border border-zinc-700/80 text-xs font-medium rounded-lg px-2.5 py-1.5 text-zinc-200 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                >
                  {portfolios.map(p => (
                    <option key={p.id} value={p.id}>
                      {p.name} ({p.type === 'VIRTUAL_TRADING' ? 'Paper' : 'Watch'})
                    </option>
                  ))}
                </select>

                {activePortfolio && (
                  <span className={`text-[10px] font-mono px-2 py-0.5 rounded-full uppercase border font-semibold ${
                    activePortfolio.type === 'VIRTUAL_TRADING'
                      ? 'bg-emerald-950/60 border-emerald-700 text-emerald-400'
                      : 'bg-blue-950/60 border-blue-700 text-blue-400'
                  }`}>
                    {activePortfolio.type === 'VIRTUAL_TRADING' ? 'Simulated Ledger' : 'External Watch'}
                  </span>
                )}
              </div>
            )}

            <button
              onClick={onOpenCreatePortfolio}
              title="Create Portfolio"
              className="p-1.5 text-zinc-400 hover:text-white hover:bg-zinc-800 rounded-lg transition"
            >
              <PlusCircle className="w-4 h-4" />
            </button>

            {/* User Profile & Logout */}
            <div className="flex items-center gap-2 pl-2 border-l border-zinc-800">
              <span className="text-xs text-zinc-400 hidden sm:inline-block">
                {user?.full_name || user?.email}
              </span>
              <button
                onClick={onLogout}
                title="Sign out"
                className="p-1.5 text-zinc-400 hover:text-rose-400 hover:bg-zinc-800 rounded-lg transition"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
