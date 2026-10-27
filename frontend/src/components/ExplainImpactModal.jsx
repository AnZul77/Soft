import React, { useState, useEffect } from 'react';
import { 
  X, 
  Sparkles, 
  ShieldAlert, 
  Link2, 
  FileText, 
  ExternalLink,
  TrendingDown,
  TrendingUp,
  Cpu,
  Layers
} from 'lucide-react';
import { api } from '../api';

export default function ExplainImpactModal({ 
  isOpen, 
  onClose, 
  portfolio, 
  ticker, 
  eventDescription, 
  priceChangePct 
}) {
  const [data, setData] = useState(null);
  const [streamedText, setStreamedText] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState("");

  // Keyboard Escape listener
  useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  useEffect(() => {
    if (!isOpen || !portfolio || !ticker) return;

    setData(null);
    setStreamedText("");
    setError("");
    setIsStreaming(true);

    // 1. Fetch structured JSON schema
    api.explainImpact(portfolio.id, ticker, eventDescription, priceChangePct)
      .then((res) => {
        setData(res);
        setIsStreaming(false);
      })
      .catch((err) => {
        setError(err.message || 'Failed to retrieve impact analysis');
        setIsStreaming(false);
      });

    // 2. Stream tokens via SSE
    api.streamExplainImpact(
      portfolio.id,
      ticker,
      eventDescription,
      (chunk) => {
        setStreamedText((prev) => prev + chunk);
      },
      () => {
        setIsStreaming(false);
      },
      (err) => {
        console.warn("SSE fallback:", err);
      }
    );
  }, [isOpen, portfolio, ticker, eventDescription, priceChangePct]);

  if (!isOpen) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="explainImpactTitle"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-black/80 backdrop-blur-md overflow-y-auto animate-in fade-in duration-200"
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div className="relative rounded-2xl bg-[#0f131c] border border-slate-700/80 text-zinc-100 shadow-2xl max-w-2xl w-full overflow-hidden flex flex-col my-auto max-h-[88vh] ring-1 ring-white/10">
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between shrink-0 bg-[#0a0d14]/90">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-cyan-400 flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 id="explainImpactTitle" className="text-sm font-bold text-white tracking-tight">
                  AI Decision Support: Portfolio Impact Analysis
                </h3>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 font-semibold uppercase">
                  RAG Grounded
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                Target: <span className="font-mono font-bold text-indigo-400">{ticker}</span> on portfolio <span className="text-slate-200 font-medium">{portfolio?.name}</span>
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-5 text-xs">
          {error && (
            <div className="p-3.5 rounded-xl bg-rose-950/60 border border-rose-800/80 text-rose-300 flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 shrink-0 text-rose-400" />
              <span>{error}</span>
            </div>
          )}

          {/* Headline & Exposure Grid */}
          {data && (
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div className="p-4 rounded-xl bg-[#141925] border border-slate-800/90 shadow-sm">
                <span className="text-slate-400 text-[10px] uppercase font-bold tracking-wider">Direct Exposure</span>
                <div className="text-2xl font-extrabold font-mono text-white mt-1">
                  {data.portfolio_exposure_pct.toFixed(1)}%
                </div>
                <span className="text-[10px] text-slate-400 font-mono">
                  ${data.portfolio_holding_value.toLocaleString()} ({data.portfolio_holding_shares} shares)
                </span>
              </div>

              <div className="p-4 rounded-xl bg-[#141925] border border-slate-800/90 shadow-sm">
                <span className="text-slate-400 text-[10px] uppercase font-bold tracking-wider">Sentiment Indicator</span>
                <div className={`text-base font-bold font-mono mt-1 flex items-center gap-1.5 ${
                  data.sentiment_impact === 'BEARISH' ? 'text-rose-400' :
                  data.sentiment_impact === 'BULLISH' ? 'text-emerald-400' : 'text-slate-300'
                }`}>
                  {data.sentiment_impact === 'BEARISH' ? <TrendingDown className="w-4 h-4" /> : <TrendingUp className="w-4 h-4" />}
                  {data.sentiment_impact}
                </div>
                <span className="text-[10px] text-slate-400">
                  Grounding Confidence: High
                </span>
              </div>

              <div className="p-4 rounded-xl bg-[#141925] border border-slate-800/90 shadow-sm">
                <span className="text-slate-400 text-[10px] uppercase font-bold tracking-wider">Affected Holdings</span>
                <div className="text-sm font-bold font-mono text-indigo-300 mt-1">
                  {data.direct_holdings_affected.length > 0 ? data.direct_holdings_affected.join(', ') : 'None directly held'}
                </div>
                <span className="text-[10px] text-slate-400">
                  Cross-referenced with ledger
                </span>
              </div>
            </div>
          )}

          {/* Supply Chain Knowledge Graph Contagion Links */}
          {data && data.supply_chain_links && data.supply_chain_links.length > 0 && (
            <div className="p-4 rounded-xl bg-[#141925] border border-slate-800/80 space-y-2">
              <div className="flex items-center gap-1.5 text-slate-300 font-bold uppercase tracking-wider text-[11px]">
                <Link2 className="w-3.5 h-3.5 text-cyan-400" />
                <span>Supply Chain & Graph Relationship Context</span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mt-2">
                {data.supply_chain_links.map((link, idx) => (
                  <div key={idx} className="p-3 rounded-lg bg-[#0e121a] border border-slate-800 font-mono text-[11px]">
                    <div className="flex items-center justify-between font-bold text-white mb-1">
                      <span>{link.source_ticker} ➔ {link.target_ticker}</span>
                      <span className="text-[9px] px-1.5 py-0.5 rounded bg-indigo-950/80 text-indigo-300 border border-indigo-700/60">
                        {link.relationship_type}
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-400 font-sans">{link.description}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Explainable AI Analysis Text (with real-time streaming) */}
          <div className="p-5 rounded-xl bg-[#141925] border border-slate-800/90 relative">
            <div className="flex items-center justify-between mb-3">
              <span className="text-slate-400 font-bold uppercase tracking-wider text-[10px] flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
                Evidence-Grounded RAG Synthesis
              </span>
              {isStreaming && (
                <span className="text-[10px] font-mono text-indigo-400 animate-pulse flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-ping" />
                  Streaming synthesis...
                </span>
              )}
            </div>

            <div className="text-slate-200 leading-relaxed text-xs whitespace-pre-wrap font-sans">
              {streamedText || data?.analysis_text || (
                <div className="text-slate-500 py-6 text-center flex flex-col items-center justify-center gap-2">
                  <Cpu className="w-6 h-6 text-slate-600 animate-pulse" />
                  <span>Querying pgvector embeddings and generating synthesis...</span>
                </div>
              )}
              {isStreaming && <span className="inline-block w-1.5 h-3.5 bg-indigo-400 ml-1 animate-pulse" />}
            </div>
          </div>

          {/* Grounded Evidence Citations */}
          {data && data.evidence_citations && data.evidence_citations.length > 0 && (
            <div className="p-4 rounded-xl bg-[#141925] border border-slate-800/80 space-y-2">
              <div className="flex items-center gap-1.5 text-slate-300 font-bold uppercase tracking-wider text-[11px]">
                <FileText className="w-3.5 h-3.5 text-indigo-400" />
                <span>Grounded Evidence Citations (Source Anchored)</span>
              </div>
              <div className="space-y-2 mt-2">
                {data.evidence_citations.map((c, i) => (
                  <div key={i} className="p-3 rounded-lg bg-[#0e121a] border border-slate-800/80">
                    <div className="flex items-center justify-between text-[11px] font-semibold text-white mb-1">
                      <span>{c.source}: {c.title}</span>
                      <a
                        href={c.url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-indigo-400 hover:text-indigo-300 flex items-center gap-1 transition"
                      >
                        Article <ExternalLink className="w-3 h-3" />
                      </a>
                    </div>
                    <p className="text-[11px] text-slate-400 italic">
                      "{c.snippet}"
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Mandatory Regulatory Disclaimer */}
          <div className="p-3.5 rounded-xl bg-amber-950/20 border border-amber-900/40 text-amber-300/80 text-[10px] flex items-start gap-2.5">
            <ShieldAlert className="w-4 h-4 shrink-0 text-amber-400 mt-0.5" />
            <p className="leading-normal">
              {data?.regulatory_disclaimer || (
                "DISCLAIMER: Non-advisory decision support only. This analysis does not constitute investment advice. Past performance is not indicative of future results."
              )}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
