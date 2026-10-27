import React from 'react';
import { 
  TrendingUp, 
  Layers, 
  Activity, 
  BookOpen, 
  BarChart3, 
  Plus, 
  LogOut,
  Sparkles,
  Bookmark,
  Bell,
  Bot,
  User,
  ChevronDown,
  ShieldCheck,
  Wallet
} from 'lucide-react';

export default function Navbar({ 
  user, 
  portfolios = [], 
  activePortfolio, 
  onSelectPortfolio, 
  onOpenCreatePortfolio, 
  activeTab, 
  setActiveTab, 
  onLogout,
  onOpenProfile,
  onOpenAIResearch,
  onOpenAlertRules,
  unreadAlertCount = 0
}) {
  const isVirtual = activePortfolio?.type === 'VIRTUAL_TRADING';
  const userInitials = (user?.full_name || user?.email || 'U')
    .split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);

  return (
    <header className="border-b border-[#1c2333] bg-[#090c10]/90 backdrop-blur-xl sticky top-0 z-40 transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 gap-4">
          
          {/* Brand Identity */}
          <div className="flex items-center gap-3 shrink-0">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-cyan-400 flex items-center justify-center shadow-lg shadow-indigo-500/25 ring-1 ring-white/20">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-sm sm:text-base tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
                APEX <span className="font-light text-slate-400">INTELLIGENCE</span>
              </span>
              <span className="hidden sm:inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-mono font-semibold bg-indigo-500/10 border border-indigo-500/30 text-indigo-300">
                v1.0 RAG
              </span>
            </div>
          </div>

          {/* Center Navigation Bar (Segmented Control) */}
          <nav className="hidden lg:flex items-center gap-1 bg-[#121622]/90 p-1 rounded-xl border border-slate-800 shadow-inner">
            <button
              onClick={() => setActiveTab('overview')}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5 ${
                activeTab === 'overview'
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                  : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/50'
              }`}
            >
              <Layers className="w-3.5 h-3.5" />
              Overview
            </button>
            <button
              onClick={() => setActiveTab('trading')}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5 ${
                activeTab === 'trading'
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                  : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/50'
              }`}
            >
              <TrendingUp className="w-3.5 h-3.5" />
              Trade Desk
            </button>
            <button
              onClick={() => setActiveTab('watchlists')}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5 ${
                activeTab === 'watchlists'
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                  : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/50'
              }`}
            >
              <Bookmark className="w-3.5 h-3.5" />
              Watchlists
            </button>
            <button
              onClick={() => setActiveTab('market')}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5 ${
                activeTab === 'market'
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                  : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/50'
              }`}
            >
              <Activity className="w-3.5 h-3.5" />
              Market & Anomaly
            </button>
            <button
              onClick={() => setActiveTab('risk')}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5 ${
                activeTab === 'risk'
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                  : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/50'
              }`}
            >
              <BarChart3 className="w-3.5 h-3.5" />
              Risk Metrics
            </button>
            <button
              onClick={() => setActiveTab('journal')}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5 ${
                activeTab === 'journal'
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                  : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/50'
              }`}
            >
              <BookOpen className="w-3.5 h-3.5" />
              Thesis Journal
            </button>
          </nav>

          {/* Right Control Toolbar */}
          <div className="flex items-center gap-2.5 shrink-0">
            {/* AI Research Copilot Button */}
            {onOpenAIResearch && (
              <button
                onClick={onOpenAIResearch}
                title="Open AI Research Copilot (FR-16)"
                className="px-3 py-1.5 rounded-xl bg-gradient-to-r from-indigo-500/15 to-cyan-500/15 hover:from-indigo-500/25 hover:to-cyan-500/25 border border-indigo-500/40 text-indigo-300 text-xs font-semibold flex items-center gap-1.5 transition-all shadow-sm"
              >
                <Bot className="w-4 h-4 text-cyan-400" />
                <span className="hidden sm:inline">AI Research</span>
              </button>
            )}

            {/* Alert Rules & Notifications */}
            {onOpenAlertRules && (
              <button
                onClick={onOpenAlertRules}
                title="Anomaly Alert Rules (FR-18)"
                className="p-2 text-slate-400 hover:text-amber-400 hover:bg-slate-800/80 rounded-xl transition relative border border-transparent hover:border-slate-700/60"
              >
                <Bell className="w-4 h-4" />
                {unreadAlertCount > 0 && (
                  <span className="absolute top-1 right-1 w-2 h-2 rounded-full bg-amber-400 ring-2 ring-[#090c10]" />
                )}
              </button>
            )}

            {/* Portfolio Selector & Status Pill */}
            {portfolios.length > 0 && (
              <div className="flex items-center gap-1.5 bg-[#121622] border border-slate-800 rounded-xl p-1">
                <div className="flex items-center gap-1.5 pl-2 pr-1">
                  <span className={`w-2 h-2 rounded-full ${isVirtual ? 'bg-emerald-400 shadow-sm shadow-emerald-400/50' : 'bg-cyan-400 shadow-sm shadow-cyan-400/50'}`} />
                  <select
                    value={activePortfolio?.id || ''}
                    onChange={(e) => {
                      const selected = portfolios.find(p => p.id === e.target.value);
                      if (selected) onSelectPortfolio(selected);
                    }}
                    className="bg-transparent text-xs font-semibold text-slate-200 focus:outline-none cursor-pointer max-w-[130px] sm:max-w-[160px] truncate"
                  >
                    {portfolios.map(p => (
                      <option key={p.id} value={p.id} className="bg-[#10141d] text-slate-200">
                        {p.name}
                      </option>
                    ))}
                  </select>
                </div>

                <button
                  onClick={onOpenCreatePortfolio}
                  title="Create New Portfolio"
                  className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
                >
                  <Plus className="w-3.5 h-3.5" />
                </button>
              </div>
            )}

            {/* User Profile Pill & Sign Out */}
            <div className="flex items-center gap-1.5 pl-2 border-l border-slate-800">
              <button
                onClick={onOpenProfile}
                title="Profile & Risk Preferences (FR-02/11/25)"
                className="flex items-center gap-2 text-xs font-medium text-slate-200 hover:text-white bg-[#121622] hover:bg-slate-800/80 border border-slate-800 px-2.5 py-1.5 rounded-xl transition"
              >
                <div className="w-5 h-5 rounded-full bg-indigo-600/80 text-white text-[10px] font-bold flex items-center justify-center">
                  {userInitials}
                </div>
                <span className="hidden xl:inline-block max-w-[100px] truncate">
                  {user?.full_name || user?.email?.split('@')[0]}
                </span>
              </button>

              <button
                onClick={onLogout}
                title="Sign out of platform"
                className="p-2 text-slate-400 hover:text-rose-400 hover:bg-slate-800/80 rounded-xl transition border border-transparent hover:border-slate-700/60"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          </div>

        </div>

        {/* Mobile Navigation Sub-bar */}
        <div className="lg:hidden flex items-center justify-between overflow-x-auto py-2 border-t border-slate-800/80 gap-1 no-scrollbar">
          {[
            { id: 'overview', label: 'Overview', icon: Layers },
            { id: 'trading', label: 'Trade Desk', icon: TrendingUp },
            { id: 'watchlists', label: 'Watchlists', icon: Bookmark },
            { id: 'market', label: 'Market', icon: Activity },
            { id: 'risk', label: 'Risk', icon: BarChart3 },
            { id: 'journal', label: 'Journal', icon: BookOpen },
          ].map(tab => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap flex items-center gap-1.5 transition-all ${
                  isActive
                    ? 'bg-indigo-600 text-white shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                {tab.label}
              </button>
            );
          })}
        </div>
      </div>
    </header>
  );
}
