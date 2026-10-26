import React, { useState } from 'react';
import { api } from '../api';
import { Sparkles, X, Search, BookOpen, ExternalLink, ShieldCheck, Activity } from 'lucide-react';

const SUGGESTED_QUERIES = [
  "Assess TSMC packaging supply chain bottlenecks and GPU delivery impact",
  "How does NVIDIA Blackwell rack-scale architecture affect datacenter power constraints?",
  "Evaluate semiconductor wafer pricing resilience amid export control changes",
  "Apple Services margin expansion versus hardware upgrade cycle trends"
];

export default function AIResearchModal({ isOpen, onClose, defaultTicker = '', onTrade }) {
  const [query, setQuery] = useState('');
  const [ticker, setTicker] = useState(defaultTicker);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const handleSearch = async (searchQuery = query) => {
    if (!searchQuery.trim()) return;
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const res = await api.researchQuery(searchQuery.trim(), ticker.trim().toUpperCase() || undefined, 5);
      setResult(res);
    } catch (err) {
      setError(err.message || 'Failed to complete semantic research query');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectSuggested = (q) => {
    setQuery(q);
    handleSearch(q);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
      <div className="bg-zinc-900 border border-zinc-800 rounded-2xl w-full max-w-3xl overflow-hidden shadow-2xl flex flex-col max-h-[85vh]">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-zinc-800 bg-zinc-950/60">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-cyan-400 flex items-center justify-center text-white shadow-lg shadow-indigo-500/20">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-bold text-white text-base">AI Semantic Research Assistant</h3>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-950 border border-indigo-700 text-indigo-300 font-bold uppercase">
                  FR-16 RAG
                </span>
              </div>
              <p className="text-xs text-zinc-400">Grounded evidence synthesis cross-referencing news, filings, and supply chain graphs</p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-1.5 text-zinc-400 hover:text-white hover:bg-zinc-800 rounded-lg transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Search Bar */}
        <div className="p-6 border-b border-zinc-800/80 bg-zinc-950/40 space-y-3">
          <form 
            onSubmit={(e) => {
              e.preventDefault();
              handleSearch();
            }} 
            className="flex gap-2"
          >
            <div className="relative flex-1">
              <Search className="w-4 h-4 text-zinc-500 absolute left-3.5 top-3" />
              <input
                type="text"
                placeholder="Ask any market or company research question (e.g. supply chain bottleneck, margin trends)..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="w-full bg-zinc-900 border border-zinc-800 rounded-xl pl-10 pr-4 py-2.5 text-xs text-white placeholder-zinc-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 font-sans"
              />
            </div>
            <input
              type="text"
              placeholder="Ticker (optional)"
              value={ticker}
              onChange={(e) => setTicker(e.target.value.toUpperCase())}
              className="w-32 bg-zinc-900 border border-zinc-800 rounded-xl px-3 py-2.5 text-xs font-mono text-white placeholder-zinc-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 uppercase text-center"
            />
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-bold text-xs shadow-md shadow-indigo-600/30 transition flex items-center gap-1.5 flex-shrink-0"
            >
              {loading ? (
                <>
                  <Activity className="w-4 h-4 animate-spin" />
                  Synthesizing...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  Synthesize
                </>
              )}
            </button>
          </form>

          {/* Suggested Prompts */}
          <div className="flex flex-wrap items-center gap-1.5 pt-1">
            <span className="text-[10px] text-zinc-500 uppercase font-mono font-bold mr-1">Prompts:</span>
            {SUGGESTED_QUERIES.map((sq, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => handleSelectSuggested(sq)}
                className="text-[11px] bg-zinc-900 hover:bg-zinc-800 text-zinc-300 hover:text-white px-2.5 py-1 rounded-lg border border-zinc-800 transition truncate max-w-xs text-left"
              >
                {sq}
              </button>
            ))}
          </div>
        </div>

        {/* Results Area */}
        <div className="p-6 overflow-y-auto flex-1 space-y-6">
          {error && (
            <div className="p-3 bg-rose-950/60 border border-rose-800 text-rose-300 text-xs rounded-xl">
              {error}
            </div>
          )}

          {loading && (
            <div className="py-16 text-center space-y-3">
              <div className="w-10 h-10 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto" />
              <p className="text-xs text-zinc-400">
                Retrieving embedding vectors, cross-referencing knowledge graph, and synthesizing citations...
              </p>
            </div>
          )}

          {!loading && !result && !error && (
            <div className="py-16 text-center space-y-3">
              <BookOpen className="w-10 h-10 text-zinc-600 mx-auto" />
              <h4 className="text-sm font-bold text-zinc-400">Enter a query to begin grounded semantic research</h4>
              <p className="text-xs text-zinc-500 max-w-md mx-auto">
                Queries are grounded using cosine similarity over news articles and company relationship nodes, preventing hallucinations.
              </p>
            </div>
          )}

          {!loading && result && (
            <div className="space-y-6 animate-fade-in">
              {/* Answer Card */}
              <div className="bg-zinc-950/70 border border-zinc-800/90 rounded-2xl p-5 space-y-3">
                <div className="flex items-center justify-between border-b border-zinc-800/80 pb-3">
                  <div className="flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-indigo-400" />
                    <h4 className="text-xs font-bold text-white uppercase tracking-wider">
                      Synthesized Intelligence Brief
                    </h4>
                  </div>
                  {result.abstention && (
                    <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-amber-950 border border-amber-800 text-amber-400 uppercase">
                      Abstention (No Grounded Context)
                    </span>
                  )}
                </div>

                <div className="text-xs text-zinc-200 leading-relaxed space-y-3 whitespace-pre-line font-sans">
                  {result.answer}
                </div>

                <div className="pt-3 border-t border-zinc-800/60 flex items-center justify-between text-[11px] text-zinc-500">
                  <span className="flex items-center gap-1.5">
                    <ShieldCheck className="w-3.5 h-3.5 text-indigo-400" />
                    SEC Grounding: Strictly factual & citation-backed
                  </span>
                  {result.ticker && onTrade && (
                    <button
                      onClick={() => {
                        onClose();
                        onTrade(result.ticker);
                      }}
                      className="text-xs text-indigo-400 hover:text-indigo-300 font-bold"
                    >
                      Trade {result.ticker} &rarr;
                    </button>
                  )}
                </div>
              </div>

              {/* Citations List */}
              {result.citations && result.citations.length > 0 && (
                <div className="space-y-3">
                  <h4 className="text-xs font-bold text-zinc-400 uppercase tracking-wider flex items-center gap-1.5">
                    <BookOpen className="w-3.5 h-3.5" />
                    Grounded Evidence Sources ({result.citations.length})
                  </h4>

                  <div className="grid grid-cols-1 gap-2.5">
                    {result.citations.map((c, idx) => (
                      <div key={idx} className="bg-zinc-950/40 border border-zinc-800/60 rounded-xl p-3 text-xs space-y-1 hover:border-zinc-700 transition">
                        <div className="flex items-center justify-between">
                          <span className="text-[10px] font-mono font-bold text-indigo-400 uppercase px-1.5 py-0.5 rounded bg-indigo-950/50 border border-indigo-900">
                            {c.source}
                          </span>
                          <span className="text-[10px] text-zinc-500 font-mono">
                            Score: {(c.similarity_score * 100).toFixed(1)}%
                          </span>
                        </div>
                        <h5 className="font-bold text-white text-xs">{c.title}</h5>
                        <p className="text-zinc-400 text-xs italic">"{c.snippet}"</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
