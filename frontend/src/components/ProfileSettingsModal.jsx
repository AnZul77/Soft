import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { X, User, ShieldCheck, Clock, FileText, Check, AlertCircle, Shield } from 'lucide-react';

export default function ProfileSettingsModal({ isOpen, onClose, onProfileUpdated }) {
  const [activeSubTab, setActiveSubTab] = useState('profile'); // 'profile' or 'audit'
  const [profile, setProfile] = useState(null);
  const [fullName, setFullName] = useState('');
  const [riskTolerance, setRiskTolerance] = useState('MODERATE');
  const [investmentHorizon, setInvestmentHorizon] = useState('MEDIUM_TERM');
  const [bio, setBio] = useState('');
  const [auditLogs, setAuditLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    if (isOpen) {
      loadProfileAndLogs();
    } else {
      setSuccessMsg('');
      setErrorMsg('');
    }
  }, [isOpen]);

  const loadProfileAndLogs = async () => {
    setLoading(true);
    try {
      const [profData, logsData] = await Promise.all([
        api.getProfile(),
        api.getAuditLogs(50)
      ]);
      setProfile(profData);
      setFullName(profData.full_name || '');
      setRiskTolerance(profData.risk_tolerance || 'MODERATE');
      setInvestmentHorizon(profData.investment_horizon || 'MEDIUM_TERM');
      setBio(profData.bio || '');
      setAuditLogs(logsData || []);
    } catch (err) {
      setErrorMsg(err.message || 'Failed to load profile');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveProfile = async (e) => {
    e.preventDefault();
    setSaving(true);
    setSuccessMsg('');
    setErrorMsg('');
    try {
      const updated = await api.updateProfile({
        full_name: fullName.trim(),
        risk_tolerance: riskTolerance,
        investment_horizon: investmentHorizon,
        bio: bio.trim()
      });
      setProfile(updated);
      setSuccessMsg('Profile and risk preferences saved successfully!');
      if (onProfileUpdated) onProfileUpdated(updated);
      // Reload audit logs to show the profile update action
      const logs = await api.getAuditLogs(50);
      setAuditLogs(logs);
    } catch (err) {
      setErrorMsg(err.message || 'Failed to update profile');
    } finally {
      setSaving(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
      <div className="bg-zinc-900 border border-zinc-800 rounded-2xl w-full max-w-2xl overflow-hidden shadow-2xl flex flex-col max-h-[85vh]">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-zinc-800 bg-zinc-950/60">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-950 border border-indigo-700/60 flex items-center justify-center text-indigo-400">
              <User className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-white text-base">User Profile & Risk Settings</h3>
              <p className="text-xs text-zinc-400">Manage risk tolerance, investment horizon, and system audit log</p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-1.5 text-zinc-400 hover:text-white hover:bg-zinc-800 rounded-lg transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab Switcher */}
        <div className="flex border-b border-zinc-800 bg-zinc-950/40 px-6 gap-6 text-xs">
          <button
            onClick={() => setActiveSubTab('profile')}
            className={`py-3 font-semibold border-b-2 transition ${
              activeSubTab === 'profile'
                ? 'border-indigo-500 text-white'
                : 'border-transparent text-zinc-400 hover:text-zinc-200'
            }`}
          >
            Risk Preferences & Bio
          </button>
          <button
            onClick={() => setActiveSubTab('audit')}
            className={`py-3 font-semibold border-b-2 transition flex items-center gap-1.5 ${
              activeSubTab === 'audit'
                ? 'border-indigo-500 text-white'
                : 'border-transparent text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <Shield className="w-3.5 h-3.5" />
            System Audit Trail (FR-25)
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto flex-1 space-y-4">
          {successMsg && (
            <div className="p-3 bg-emerald-950/60 border border-emerald-800 text-emerald-300 text-xs rounded-xl flex items-center gap-2">
              <Check className="w-4 h-4 flex-shrink-0" />
              <span>{successMsg}</span>
            </div>
          )}

          {errorMsg && (
            <div className="p-3 bg-rose-950/60 border border-rose-800 text-rose-300 text-xs rounded-xl flex items-center gap-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}

          {activeSubTab === 'profile' && (
            <form onSubmit={handleSaveProfile} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-zinc-300 mb-1">Account Email</label>
                <input
                  type="text"
                  value={profile?.email || ''}
                  disabled
                  className="w-full bg-zinc-950/50 border border-zinc-800/80 rounded-xl px-3 py-2 text-xs text-zinc-500 font-mono cursor-not-allowed"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-zinc-300 mb-1">Full Name</label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:ring-1 focus:ring-indigo-500"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-zinc-300 mb-1">
                    Risk Tolerance (FR-02)
                  </label>
                  <select
                    value={riskTolerance}
                    onChange={(e) => setRiskTolerance(e.target.value)}
                    className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:ring-1 focus:ring-indigo-500"
                  >
                    <option value="CONSERVATIVE">Conservative (Capital preservation, low volatility)</option>
                    <option value="MODERATE">Moderate (Balanced risk / market return)</option>
                    <option value="AGGRESSIVE">Aggressive (High growth, tech / cyclical focus)</option>
                    <option value="SPECULATIVE">Speculative (Max volatility, early-stage catalysts)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-medium text-zinc-300 mb-1">
                    Investment Horizon (FR-11)
                  </label>
                  <select
                    value={investmentHorizon}
                    onChange={(e) => setInvestmentHorizon(e.target.value)}
                    className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:ring-1 focus:ring-indigo-500"
                  >
                    <option value="SHORT_TERM">Short Term (&lt; 1 Year)</option>
                    <option value="MEDIUM_TERM">Medium Term (1 - 3 Years)</option>
                    <option value="LONG_TERM">Long Term (3 - 7 Years)</option>
                    <option value="MULTI_DECADE">Multi-Decade (&gt; 7 Years)</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-zinc-300 mb-1">
                  Investment Bio & Methodology
                </label>
                <textarea
                  rows="3"
                  value={bio}
                  onChange={(e) => setBio(e.target.value)}
                  placeholder="Describe your strategy, sector interests, or mandate guidelines..."
                  className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:ring-1 focus:ring-indigo-500"
                />
              </div>

              <div className="flex justify-end pt-2">
                <button
                  type="submit"
                  disabled={saving}
                  className="px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-bold text-xs shadow-md shadow-indigo-600/30 transition flex items-center gap-1.5"
                >
                  <Check className="w-4 h-4" />
                  {saving ? 'Saving...' : 'Save Preferences'}
                </button>
              </div>
            </form>
          )}

          {activeSubTab === 'audit' && (
            <div className="space-y-3">
              <div className="flex items-center justify-between text-xs text-zinc-400">
                <p>Immutable audit trail of security, order execution, and portfolio events.</p>
                <span className="font-mono">{auditLogs.length} Records</span>
              </div>

              {auditLogs.length === 0 ? (
                <div className="text-center py-10 text-xs text-zinc-500">
                  No audit log entries recorded yet.
                </div>
              ) : (
                <div className="border border-zinc-800 rounded-xl overflow-hidden">
                  <table className="w-full text-left text-xs font-mono">
                    <thead className="bg-zinc-950/60 border-b border-zinc-800 text-zinc-400 text-[11px]">
                      <tr>
                        <th className="py-2.5 px-4">Timestamp</th>
                        <th className="py-2.5 px-3">Action</th>
                        <th className="py-2.5 px-3">Resource</th>
                        <th className="py-2.5 px-4">Details</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-zinc-800/60">
                      {auditLogs.map((log) => (
                        <tr key={log.id} className="hover:bg-zinc-800/30">
                          <td className="py-2.5 px-4 text-zinc-400 text-[11px] whitespace-nowrap">
                            {new Date(log.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                          </td>
                          <td className="py-2.5 px-3">
                            <span className="text-[10px] px-1.5 py-0.5 rounded font-bold bg-indigo-950 border border-indigo-800 text-indigo-300">
                              {log.action}
                            </span>
                          </td>
                          <td className="py-2.5 px-3 text-zinc-400 text-[11px]">
                            {log.resource_type || '—'}
                          </td>
                          <td className="py-2.5 px-4 text-zinc-300 font-sans text-xs">
                            {log.details || '—'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
