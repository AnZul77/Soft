import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { 
  Eye, 
  Plus, 
  Trash2, 
  TrendingUp, 
  TrendingDown, 
  BarChart2, 
  Sparkles, 
  DollarSign, 
  FolderPlus, 
  Edit3, 
  Check, 
  X,
  Target
} from 'lucide-react';

export default function WatchlistsTab({ onTrade, onExplain, onViewChart, onTradeTicker, onExplainTicker }) {
  const handleTrade = onTrade || onTradeTicker;
  const handleExplain = onExplain || onExplainTicker;
  const [watchlists, setWatchlists] = useState([]);
  const [activeWatchlistId, setActiveWatchlistId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Add Item form state
  const [newTicker, setNewTicker] = useState('');
  const [newNotes, setNewNotes] = useState('');
  const [newTargetPrice, setNewTargetPrice] = useState('');
  const [isAddingItem, setIsAddingItem] = useState(false);

  // Create Watchlist state
  const [isCreatingWl, setIsCreatingWl] = useState(false);
  const [newWlName, setNewWlName] = useState('');
  const [newWlDesc, setNewWlDesc] = useState('');

  // Rename state
  const [isRenaming, setIsRenaming] = useState(false);
  const [renamedName, setRenamedName] = useState('');

  useEffect(() => {
    fetchWatchlists();
  }, []);

  const fetchWatchlists = async () => {
    setLoading(true);
    setError('');
    try {
      const list = await api.getWatchlists();
      setWatchlists(list);
      if (list.length > 0 && !activeWatchlistId) {
        setActiveWatchlistId(list[0].id);
      } else if (list.length > 0 && !list.find(w => w.id === activeWatchlistId)) {
        setActiveWatchlistId(list[0].id);
      }
    } catch (err) {
      setError(err.message || 'Failed to load watchlists');
    } finally {
      setLoading(false);
    }
  };

  const activeWatchlist = watchlists.find(w => w.id === activeWatchlistId);

  const handleCreateWatchlist = async (e) => {
    e.preventDefault();
    if (!newWlName.trim()) return;
    try {
      const created = await api.createWatchlist(newWlName.trim(), newWlDesc.trim());
      setNewWlName('');
      setNewWlDesc('');
      setIsCreatingWl(false);
      await fetchWatchlists();
      setActiveWatchlistId(created.id);
    } catch (err) {
      setError(err.message || 'Failed to create watchlist');
    }
  };

  const handleRenameWatchlist = async () => {
    if (!renamedName.trim() || !activeWatchlistId) return;
    try {
      await api.updateWatchlist(activeWatchlistId, { name: renamedName.trim() });
      setIsRenaming(false);
      fetchWatchlists();
    } catch (err) {
      setError(err.message || 'Failed to rename watchlist');
    }
  };

  const handleDeleteWatchlist = async (id) => {
    if (!window.confirm('Are you sure you want to delete this watchlist?')) return;
    try {
      await api.deleteWatchlist(id);
      fetchWatchlists();
    } catch (err) {
      setError(err.message || 'Failed to delete watchlist');
    }
  };

  const handleAddItem = async (e) => {
    e.preventDefault();
    if (!newTicker.trim() || !activeWatchlistId) return;
    try {
      await api.addWatchlistItem(
        activeWatchlistId,
        newTicker.trim().toUpperCase(),
        newNotes.trim(),
        newTargetPrice ? parseFloat(newTargetPrice) : null
      );
      setNewTicker('');
      setNewNotes('');
      setNewTargetPrice('');
      setIsAddingItem(false);
      fetchWatchlists();
    } catch (err) {
      setError(err.message || 'Failed to add security');
    }
  };

  const handleRemoveItem = async (itemId) => {
    if (!activeWatchlistId) return;
    try {
      await api.removeWatchlistItem(activeWatchlistId, itemId);
      fetchWatchlists();
    } catch (err) {
      setError(err.message || 'Failed to remove security');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header & Watchlist Selector */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
            <Eye className="w-5 h-5 text-indigo-400" />
            Watchlists & Asset Radar
          </h2>
          <p className="text-xs text-zinc-400 mt-0.5">
            Monitor target securities, track price targets, and launch one-click research or simulated trades
          </p>
        </div>

        <div className="flex items-center gap-2">
          {watchlists.length > 0 && (
            <div className="flex items-center gap-2">
              {isRenaming ? (
                <div className="flex items-center gap-1.5">
                  <input
                    type="text"
                    value={renamedName}
                    onChange={(e) => setRenamedName(e.target.value)}
                    className="bg-zinc-950 border border-indigo-500 rounded-lg px-2.5 py-1 text-xs text-white focus:outline-none"
                    autoFocus
                  />
                  <button
                    onClick={handleRenameWatchlist}
                    className="p-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg transition"
                    title="Save name"
                  >
                    <Check className="w-3.5 h-3.5" />
                  </button>
                  <button
                    onClick={() => setIsRenaming(false)}
                    className="p-1.5 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 rounded-lg transition"
                    title="Cancel"
                  >
                    <X className="w-3.5 h-3.5" />
                  </button>
                </div>
              ) : (
                <div className="flex items-center gap-1.5 bg-zinc-900 border border-zinc-800 rounded-xl px-2 py-1">
                  <select
                    value={activeWatchlistId || ''}
                    onChange={(e) => setActiveWatchlistId(e.target.value)}
                    className="bg-transparent text-xs font-semibold text-white focus:outline-none cursor-pointer pr-4"
                  >
                    {watchlists.map(w => (
                      <option key={w.id} value={w.id} className="bg-zinc-900 text-white">
                        {w.name} ({w.items?.length || 0})
                      </option>
                    ))}
                  </select>
                  <button
                    onClick={() => {
                      setRenamedName(activeWatchlist?.name || '');
                      setIsRenaming(true);
                    }}
                    title="Rename Watchlist"
                    className="p-1 text-zinc-400 hover:text-white rounded"
                  >
                    <Edit3 className="w-3.5 h-3.5" />
                  </button>
                  <button
                    onClick={() => handleDeleteWatchlist(activeWatchlistId)}
                    title="Delete Watchlist"
                    className="p-1 text-zinc-400 hover:text-rose-400 rounded"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              )}
            </div>
          )}

          <button
            onClick={() => setIsCreatingWl(true)}
            className="px-3 py-1.5 rounded-xl bg-zinc-900 border border-zinc-700 hover:border-zinc-500 text-zinc-200 hover:text-white text-xs font-semibold transition flex items-center gap-1.5"
          >
            <FolderPlus className="w-3.5 h-3.5 text-indigo-400" />
            New List
          </button>
        </div>
      </div>

      {error && (
        <div className="p-3 bg-rose-950/60 border border-rose-800 text-rose-300 text-xs rounded-xl flex items-center justify-between">
          <span>{error}</span>
          <button onClick={() => setError('')} className="p-1 hover:text-white">
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      )}

      {/* Create Watchlist Modal / Inline Panel */}
      {isCreatingWl && (
        <form onSubmit={handleCreateWatchlist} className="p-4 bg-zinc-900/90 border border-indigo-700/50 rounded-2xl space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold uppercase tracking-wider text-indigo-300">Create New Watchlist</h3>
            <button type="button" onClick={() => setIsCreatingWl(false)} className="text-zinc-400 hover:text-white">
              <X className="w-4 h-4" />
            </button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div>
              <label className="block text-[11px] text-zinc-400 mb-1">Watchlist Name *</label>
              <input
                type="text"
                placeholder="e.g. Semiconductor Foundry Focus"
                value={newWlName}
                onChange={(e) => setNewWlName(e.target.value)}
                required
                className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:ring-1 focus:ring-indigo-500"
              />
            </div>
            <div>
              <label className="block text-[11px] text-zinc-400 mb-1">Description (Optional)</label>
              <input
                type="text"
                placeholder="Strategy or focus notes"
                value={newWlDesc}
                onChange={(e) => setNewWlDesc(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:ring-1 focus:ring-indigo-500"
              />
            </div>
          </div>
          <div className="flex justify-end gap-2 pt-1">
            <button
              type="button"
              onClick={() => setIsCreatingWl(false)}
              className="px-3 py-1.5 rounded-xl text-xs text-zinc-400 hover:text-white transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs shadow-md shadow-indigo-600/30 transition"
            >
              Create List
            </button>
          </div>
        </form>
      )}

      {/* Main Watchlist View */}
      {watchlists.length === 0 ? (
        <div className="text-center py-16 bg-zinc-900/40 border border-dashed border-zinc-800 rounded-2xl">
          <Eye className="w-10 h-10 text-zinc-600 mx-auto mb-3" />
          <h3 className="text-sm font-bold text-zinc-300">No Watchlists Created Yet</h3>
          <p className="text-xs text-zinc-500 max-w-sm mx-auto mt-1 mb-4">
            Create your first watchlist to track tickers, monitor price gaps, and assess supply-chain catalysts.
          </p>
          <button
            onClick={() => setIsCreatingWl(true)}
            className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs transition"
          >
            Create Watchlist
          </button>
        </div>
      ) : (
        <div className="bg-zinc-900/60 border border-zinc-800 rounded-2xl overflow-hidden shadow-sm">
          {/* Watchlist Sub-header */}
          <div className="flex flex-wrap items-center justify-between px-6 py-4 border-b border-zinc-800 bg-zinc-950/40 gap-4">
            <div>
              <h3 className="text-sm font-bold text-white tracking-tight">{activeWatchlist?.name}</h3>
              {activeWatchlist?.description && (
                <p className="text-xs text-zinc-400 mt-0.5">{activeWatchlist.description}</p>
              )}
            </div>

            <button
              onClick={() => setIsAddingItem(!isAddingItem)}
              className="px-3 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs shadow-md shadow-indigo-600/30 transition flex items-center gap-1.5"
            >
              <Plus className="w-3.5 h-3.5" />
              Add Security
            </button>
          </div>

          {/* Add Security Form */}
          {isAddingItem && (
            <form onSubmit={handleAddItem} className="p-4 border-b border-zinc-800 bg-zinc-950/70 space-y-3">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div>
                  <label className="block text-[11px] text-zinc-400 mb-1">Ticker Symbol *</label>
                  <input
                    type="text"
                    placeholder="e.g. NVDA, TSMC, AAPL"
                    value={newTicker}
                    onChange={(e) => setNewTicker(e.target.value.toUpperCase())}
                    required
                    className="w-full bg-zinc-900 border border-zinc-800 rounded-xl px-3 py-2 text-xs font-mono text-white focus:outline-none focus:ring-1 focus:ring-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-[11px] text-zinc-400 mb-1">Target Price ($)</label>
                  <input
                    type="number"
                    step="0.01"
                    placeholder="Optional target"
                    value={newTargetPrice}
                    onChange={(e) => setNewTargetPrice(e.target.value)}
                    className="w-full bg-zinc-900 border border-zinc-800 rounded-xl px-3 py-2 text-xs font-mono text-white focus:outline-none focus:ring-1 focus:ring-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-[11px] text-zinc-400 mb-1">Thesis / Quick Notes</label>
                  <input
                    type="text"
                    placeholder="Rationale for watching"
                    value={newNotes}
                    onChange={(e) => setNewNotes(e.target.value)}
                    className="w-full bg-zinc-900 border border-zinc-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:ring-1 focus:ring-indigo-500"
                  />
                </div>
              </div>
              <div className="flex justify-end gap-2 pt-1">
                <button
                  type="button"
                  onClick={() => setIsAddingItem(false)}
                  className="px-3 py-1.5 rounded-xl text-xs text-zinc-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs"
                >
                  Add to Watchlist
                </button>
              </div>
            </form>
          )}

          {/* Securities Table */}
          {activeWatchlist?.items?.length === 0 ? (
            <div className="text-center py-12 text-xs text-zinc-500">
              No securities added to this watchlist yet. Click "Add Security" to begin tracking.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="border-b border-zinc-800 bg-zinc-950/40 text-zinc-400 uppercase text-[11px] font-mono">
                    <th className="py-3 px-6">Ticker</th>
                    <th className="py-3 px-4">Live Quote</th>
                    <th className="py-3 px-4">24h Change</th>
                    <th className="py-3 px-4">Target Price</th>
                    <th className="py-3 px-4">Target Gap</th>
                    <th className="py-3 px-4">Notes</th>
                    <th className="py-3 px-6 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-zinc-800/60 font-mono">
                  {activeWatchlist?.items?.map((item) => {
                    const price = item.current_price;
                    const changePct = item.change_percent || 0.0;
                    const isPositive = changePct >= 0;
                    const targetGap = item.target_price && price 
                      ? ((item.target_price - price) / price) * 100 
                      : null;

                    return (
                      <tr key={item.id} className="hover:bg-zinc-800/30 transition">
                        <td className="py-3 px-6">
                          <button
                            onClick={() => onViewChart && onViewChart(item.ticker)}
                            className="font-bold text-white hover:text-indigo-400 flex items-center gap-1.5 group"
                          >
                            <span>{item.ticker}</span>
                            <BarChart2 className="w-3.5 h-3.5 text-zinc-500 group-hover:text-indigo-400 transition" />
                          </button>
                        </td>
                        <td className="py-3 px-4 text-white font-semibold">
                          {price ? `$${price.toFixed(2)}` : '—'}
                        </td>
                        <td className={`py-3 px-4 font-bold flex items-center gap-1 ${isPositive ? 'text-emerald-400' : 'text-rose-400'}`}>
                          {isPositive ? <TrendingUp className="w-3.5 h-3.5" /> : <TrendingDown className="w-3.5 h-3.5" />}
                          {isPositive ? '+' : ''}{changePct.toFixed(2)}%
                        </td>
                        <td className="py-3 px-4 text-zinc-300">
                          {item.target_price ? `$${item.target_price.toFixed(2)}` : '—'}
                        </td>
                        <td className="py-3 px-4">
                          {targetGap !== null ? (
                            <span className={`text-[10px] px-1.5 py-0.5 rounded font-bold ${
                              targetGap > 0 
                                ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' 
                                : 'bg-rose-950 text-rose-400 border border-rose-800'
                            }`}>
                              {targetGap > 0 ? '+' : ''}{targetGap.toFixed(1)}%
                            </span>
                          ) : (
                            <span className="text-zinc-600">—</span>
                          )}
                        </td>
                        <td className="py-3 px-4 text-zinc-400 font-sans text-xs max-w-xs truncate">
                          {item.notes || '—'}
                        </td>
                        <td className="py-3 px-6 text-right">
                          <div className="flex items-center justify-end gap-1.5 font-sans">
                            <button
                              onClick={() => onViewChart && onViewChart(item.ticker)}
                              title="View Interactive Chart"
                              className="p-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-300 transition"
                            >
                              <BarChart2 className="w-3.5 h-3.5" />
                            </button>
                            <button
                              onClick={() => handleExplain && handleExplain(item.ticker)}
                              title="AI Impact Analysis"
                              className="p-1.5 rounded-lg bg-indigo-950/80 hover:bg-indigo-900 border border-indigo-700/60 text-indigo-300 transition"
                            >
                              <Sparkles className="w-3.5 h-3.5" />
                            </button>
                            <button
                              onClick={() => handleTrade && handleTrade(item.ticker)}
                              title="Place Simulated Trade"
                              className="p-1.5 rounded-lg bg-emerald-950/80 hover:bg-emerald-900 border border-emerald-700/60 text-emerald-300 transition"
                            >
                              <DollarSign className="w-3.5 h-3.5" />
                            </button>
                            <button
                              onClick={() => handleRemoveItem(item.id)}
                              title="Remove from Watchlist"
                              className="p-1.5 rounded-lg text-zinc-500 hover:text-rose-400 hover:bg-zinc-800 transition"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>
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
      )}
    </div>
  );
}
