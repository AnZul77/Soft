import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { Bell, X, Plus, Trash2, Check, AlertTriangle, ShieldCheck } from 'lucide-react';

export default function AlertRuleModal({ isOpen, onClose }) {
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [ticker, setTicker] = useState('');
  const [thresholdPct, setThresholdPct] = useState('8');
  const [windowMinutes, setWindowMinutes] = useState('15');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (isOpen) {
      fetchRules();
    }
  }, [isOpen]);

  const fetchRules = async () => {
    setLoading(true);
    try {
      const data = await api.getAlertRules();
      setRules(data);
    } catch (err) {
      setError(err.message || 'Failed to fetch alert rules');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateRule = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    try {
      await api.createAlertRule({
        ticker: ticker.trim().toUpperCase() || null,
        threshold_pct: parseFloat(thresholdPct) / 100.0,
        window_minutes: parseFloat(windowMinutes)
      });
      setTicker('');
      setThresholdPct('8');
      fetchRules();
    } catch (err) {
      setError(err.message || 'Failed to create alert rule');
    } finally {
      setSaving(false);
    }
  };

  const handleToggleRule = async (rule) => {
    try {
      await api.updateAlertRule(rule.id, { is_active: !rule.is_active });
      fetchRules();
    } catch (err) {
      setError(err.message || 'Failed to update alert rule');
    }
  };

  const handleDeleteRule = async (ruleId) => {
    try {
      await api.deleteAlertRule(ruleId);
      fetchRules();
    } catch (err) {
      setError(err.message || 'Failed to delete alert rule');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
      <div className="bg-zinc-900 border border-zinc-800 rounded-2xl w-full max-w-2xl overflow-hidden shadow-2xl flex flex-col max-h-[85vh]">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-zinc-800 bg-zinc-950/60">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-amber-950 border border-amber-700/60 flex items-center justify-center text-amber-400">
              <Bell className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-bold text-white text-base">Anomaly Alert Rules</h3>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-950 border border-amber-700 text-amber-300 font-bold uppercase">
                  FR-18
                </span>
              </div>
              <p className="text-xs text-zinc-400">Configure thresholds for automated volatility and supply chain anomaly detection</p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-1.5 text-zinc-400 hover:text-white hover:bg-zinc-800 rounded-lg transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto flex-1 space-y-6">
          {error && (
            <div className="p-3 bg-rose-950/60 border border-rose-800 text-rose-300 text-xs rounded-xl">
              {error}
            </div>
          )}

          {/* Add Rule Form */}
          <form onSubmit={handleCreateRule} className="bg-zinc-950/70 border border-zinc-800 p-4 rounded-xl space-y-3">
            <h4 className="text-xs font-bold text-zinc-300 uppercase tracking-wider flex items-center gap-1.5">
              <Plus className="w-3.5 h-3.5 text-indigo-400" />
              Add Custom Rule
            </h4>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div>
                <label className="block text-[11px] text-zinc-400 mb-1">Ticker (Blank = All Holdings)</label>
                <input
                  type="text"
                  placeholder="e.g. NVDA or all"
                  value={ticker}
                  onChange={(e) => setTicker(e.target.value.toUpperCase())}
                  className="w-full bg-zinc-900 border border-zinc-800 rounded-xl px-3 py-2 text-xs font-mono text-white placeholder-zinc-600 focus:outline-none focus:ring-1 focus:ring-indigo-500 uppercase"
                />
              </div>

              <div>
                <label className="block text-[11px] text-zinc-400 mb-1">Trigger Move (%)</label>
                <select
                  value={thresholdPct}
                  onChange={(e) => setThresholdPct(e.target.value)}
                  className="w-full bg-zinc-900 border border-zinc-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:ring-1 focus:ring-indigo-500 font-mono"
                >
                  <option value="4">4% intraday move</option>
                  <option value="5">5% intraday move</option>
                  <option value="8">8% standard anomaly</option>
                  <option value="10">10% sharp shock</option>
                  <option value="15">15% extreme event</option>
                </select>
              </div>

              <div>
                <label className="block text-[11px] text-zinc-400 mb-1">Time Window (Min)</label>
                <select
                  value={windowMinutes}
                  onChange={(e) => setWindowMinutes(e.target.value)}
                  className="w-full bg-zinc-900 border border-zinc-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:ring-1 focus:ring-indigo-500 font-mono"
                >
                  <option value="15">15 Minutes</option>
                  <option value="30">30 Minutes</option>
                  <option value="60">60 Minutes</option>
                </select>
              </div>
            </div>

            <div className="flex justify-end pt-1">
              <button
                type="submit"
                disabled={saving}
                className="px-4 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-bold text-xs shadow-md shadow-indigo-600/30 transition"
              >
                {saving ? 'Adding...' : 'Create Rule'}
              </button>
            </div>
          </form>

          {/* Rules List */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold text-zinc-400 uppercase tracking-wider">
              Active Trigger Rules ({rules.length})
            </h4>

            {loading ? (
              <div className="py-8 text-center text-xs text-zinc-500">Loading configured rules...</div>
            ) : rules.length === 0 ? (
              <div className="py-8 text-center text-xs text-zinc-500 bg-zinc-950/40 border border-zinc-800/60 rounded-xl">
                No custom alert rules configured. The system will use the default 8% consolidated portfolio scanner.
              </div>
            ) : (
              <div className="border border-zinc-800 rounded-xl overflow-hidden divide-y divide-zinc-800/60 font-mono">
                {rules.map((r) => (
                  <div key={r.id} className="flex items-center justify-between p-3.5 bg-zinc-950/40 hover:bg-zinc-800/30 transition">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-zinc-900 border border-zinc-800 flex items-center justify-center font-bold text-xs text-white">
                        {r.ticker || 'ALL'}
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-xs text-white">
                            {r.ticker ? `Ticker: ${r.ticker}` : 'All Portfolio Holdings'}
                          </span>
                          <span className="text-[10px] text-zinc-400 font-sans">
                            Threshold: {(r.threshold_pct * 100).toFixed(0)}% move in {r.window_minutes}m
                          </span>
                        </div>
                        <span className="text-[10px] text-zinc-500 font-sans">
                          Created {new Date(r.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 font-sans">
                      <button
                        onClick={() => handleToggleRule(r)}
                        className={`px-2.5 py-1 rounded-lg text-xs font-semibold transition ${
                          r.is_active
                            ? 'bg-emerald-950 border border-emerald-800 text-emerald-400'
                            : 'bg-zinc-800 border border-zinc-700 text-zinc-400'
                        }`}
                      >
                        {r.is_active ? 'Active' : 'Muted'}
                      </button>
                      <button
                        onClick={() => handleDeleteRule(r.id)}
                        className="p-1.5 text-zinc-500 hover:text-rose-400 hover:bg-zinc-800 rounded-lg transition"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
