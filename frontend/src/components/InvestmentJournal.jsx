import React, { useState, useEffect } from 'react';
import { 
  BookOpen, 
  Plus, 
  Sparkles, 
  Trash2, 
  Target, 
  Calendar, 
  Star,
  CheckCircle2
} from 'lucide-react';
import { api } from '../api';

export default function InvestmentJournal({ portfolio, quotes }) {
  const [entries, setEntries] = useState([]);
  const [ticker, setTicker] = useState("NVDA");
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [rationale, setRationale] = useState("");
  const [targetPrice, setTargetPrice] = useState("");
  const [confidence, setConfidence] = useState(4);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [reflectingId, setReflectingId] = useState(null);

  const loadEntries = () => {
    api.getJournalEntries()
      .then(setEntries)
      .catch(console.error);
  };

  useEffect(() => {
    loadEntries();
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!title || !content) return;

    setIsSubmitting(true);
    try {
      await api.createJournalEntry({
        portfolio_id: portfolio?.id,
        ticker: ticker.toUpperCase(),
        thesis_title: title,
        thesis_content: content,
        rationale,
        target_price: targetPrice ? parseFloat(targetPrice) : null,
        confidence_rating: confidence
      });
      setTitle("");
      setContent("");
      setRationale("");
      setTargetPrice("");
      setIsSubmitting(false);
      loadEntries();
    } catch (err) {
      alert("Failed to create entry: " + err.message);
      setIsSubmitting(false);
    }
  };

  const handleReflect = async (entryId) => {
    setReflectingId(entryId);
    try {
      await api.reflectOnThesis(entryId);
      loadEntries();
      setReflectingId(null);
    } catch (err) {
      alert("Reflection failed: " + err.message);
      setReflectingId(null);
    }
  };

  const handleDelete = async (entryId) => {
    if (!confirm("Are you sure you want to delete this thesis entry?")) return;
    try {
      await api.deleteJournalEntry(entryId);
      loadEntries();
    } catch (err) {
      alert("Delete failed: " + err.message);
    }
  };

  return (
    <div className="space-y-8">
      {/* Log Thesis Form */}
      <div className="bg-zinc-900/60 border border-zinc-800 rounded-2xl p-6 shadow-sm">
        <div className="flex items-center gap-2 mb-4">
          <BookOpen className="w-4 h-4 text-indigo-400" />
          <h2 className="text-sm font-bold text-white uppercase tracking-wider">Record Investment Thesis</h2>
        </div>

        <form onSubmit={handleCreate} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-[11px] font-medium text-zinc-400 mb-1">Asset Ticker</label>
              <select
                value={ticker}
                onChange={(e) => setTicker(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-3 py-2 text-xs font-mono font-bold text-white focus:outline-none focus:ring-1 focus:ring-indigo-500"
              >
                {quotes.map(q => (
                  <option key={q.ticker} value={q.ticker}>{q.ticker}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-[11px] font-medium text-zinc-400 mb-1">Thesis Headline</label>
              <input
                type="text"
                placeholder="e.g. AI Hyperscaler Capex Supercycle"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
                className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:ring-1 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="block text-[11px] font-medium text-zinc-400 mb-1">Target Price ($)</label>
              <input
                type="number"
                step="any"
                placeholder="e.g. 175.00"
                value={targetPrice}
                onChange={(e) => setTargetPrice(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-3 py-2 text-xs font-mono text-white focus:outline-none focus:ring-1 focus:ring-indigo-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-[11px] font-medium text-zinc-400 mb-1">Core Hypothesis & Assumptions</label>
            <textarea
              rows="2"
              placeholder="Detail your operational and market assumptions (e.g. margin expansion, market share gains)..."
              value={content}
              onChange={(e) => setContent(e.target.value)}
              required
              className="w-full bg-zinc-950 border border-zinc-800 rounded-xl p-3 text-xs text-white focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>

          <div className="flex items-center justify-between pt-2">
            <div className="flex items-center gap-1.5">
              <span className="text-[11px] text-zinc-400 mr-2">Conviction:</span>
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  type="button"
                  key={star}
                  onClick={() => setConfidence(star)}
                  className={`p-1 rounded hover:scale-110 transition ${
                    confidence >= star ? 'text-amber-400' : 'text-zinc-600'
                  }`}
                >
                  <Star className="w-4 h-4 fill-current" />
                </button>
              ))}
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs shadow-md shadow-indigo-600/30 transition flex items-center gap-1.5"
            >
              <Plus className="w-4 h-4" />
              Save Thesis
            </button>
          </div>
        </form>
      </div>

      {/* Journal Entries List */}
      <div className="space-y-4">
        <h3 className="text-sm font-bold text-white uppercase tracking-wider">Recorded Theses & Reflection Log</h3>

        {entries.length === 0 ? (
          <div className="text-center py-12 bg-zinc-900/40 border border-zinc-800 rounded-2xl">
            <p className="text-zinc-400 text-xs">No thesis entries logged yet. Record your investment hypotheses above.</p>
          </div>
        ) : (
          entries.map((entry) => (
            <div 
              key={entry.id} 
              className="bg-zinc-900/60 border border-zinc-800 rounded-2xl p-5 shadow-sm space-y-4"
            >
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-base text-white font-mono">{entry.ticker}</span>
                    <span className="text-xs font-semibold text-zinc-300">{entry.thesis_title}</span>
                  </div>
                  <div className="flex items-center gap-3 text-[11px] text-zinc-500 font-mono mt-1">
                    <span>Logged: {new Date(entry.created_at).toLocaleDateString()}</span>
                    {entry.target_price && (
                      <span className="text-emerald-400 font-semibold">Target: ${entry.target_price.toFixed(2)}</span>
                    )}
                    <span>Conviction: {entry.confidence_rating}/5</span>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleReflect(entry.id)}
                    disabled={reflectingId === entry.id}
                    className="px-3 py-1.5 rounded-lg bg-indigo-950/80 hover:bg-indigo-900 border border-indigo-700/60 text-indigo-300 text-xs font-semibold transition flex items-center gap-1.5"
                  >
                    <Sparkles className={`w-3.5 h-3.5 text-indigo-400 ${reflectingId === entry.id ? 'animate-spin' : ''}`} />
                    {reflectingId === entry.id ? 'Reflecting...' : 'AI Thesis Reflection'}
                  </button>
                  <button
                    onClick={() => handleDelete(entry.id)}
                    className="p-1.5 text-zinc-500 hover:text-rose-400 hover:bg-zinc-800 rounded-lg transition"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>

              <p className="text-xs text-zinc-300 whitespace-pre-wrap">
                {entry.thesis_content}
              </p>

              {/* AI Reflection Result */}
              {entry.ai_reflection && (
                <div className="p-4 rounded-xl bg-zinc-950 border border-indigo-900/50 space-y-2">
                  <div className="flex items-center gap-1.5 text-indigo-300 font-bold uppercase tracking-wider text-[10px]">
                    <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
                    <span>AI Thesis Reflection & Grounding</span>
                  </div>
                  <div className="text-xs text-zinc-300 leading-relaxed whitespace-pre-wrap">
                    {entry.ai_reflection}
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
