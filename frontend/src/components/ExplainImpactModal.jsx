import React, { useState, useEffect, useRef } from 'react';
import { 
  X, 
  Sparkles, 
  ShieldAlert, 
  Layers, 
  Link2, 
  FileText, 
  ExternalLink,
  Info
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
  const dialogRef = useRef(null);
  const [data, setData] = useState(null);
  const [streamedText, setStreamedText] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState("");

  // Sync with native <dialog>
  useEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) return;

    if (isOpen) {
      if (!dialog.open) dialog.showModal();
    } else {
      if (dialog.open) dialog.close();
    }
  }, [isOpen]);

  // Modern Web Guidance: Fallback for browsers without native `closedby` attribute support
  useEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) return;

    const handleBackdropClick = (event) => {
      if (event.target !== dialog) return;
      const rect = dialog.getBoundingClientRect();
      const isContent = (
        rect.top <= event.clientY &&
        event.clientY <= rect.top + rect.height &&
        rect.left <= event.clientX &&
        event.clientX <= rect.left + rect.width
      );
      if (!isContent) {
        onClose();
      }
    };

    if (!('closedBy' in HTMLDialogElement.prototype)) {
      dialog.addEventListener('click', handleBackdropClick);
      return () => dialog.removeEventListener('click', handleBackdropClick);
    }
  }, [onClose]);

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
        setError(err.message);
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

  return (
    <dialog
      ref={dialogRef}
      closedby="any"
      onClose={onClose}
      aria-labelledby="explainImpactTitle"
      className="m-auto rounded-2xl bg-zinc-900 border border-zinc-800 text-zinc-100 shadow-2xl max-w-2xl w-full overflow-hidden p-0 max-h-[90vh] flex flex-col"
    >
      {/* Modal Header */}
      <div className="p-6 border-b border-zinc-800 flex items-center justify-between shrink-0 bg-zinc-950/60">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-cyan-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 id="explainImpactTitle" className="text-base font-bold text-white tracking-tight">
              AI Decision Support: Portfolio Impact Analysis
            </h3>
            <p className="text-xs text-zinc-400 mt-0.5">
              Target: <span className="font-mono font-bold text-indigo-400">{ticker}</span> on portfolio <span className="text-zinc-300 font-semibold">{portfolio?.name}</span>
            </p>
          </div>
        </div>

        <button
          onClick={onClose}
          className="p-1.5 rounded-lg text-zinc-400 hover:text-white hover:bg-zinc-800 transition"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Modal Body */}
      <div className="p-6 overflow-y-auto space-y-6 text-xs">
        {error && (
          <div className="p-3.5 rounded-xl bg-rose-950/60 border border-rose-800 text-rose-300">
            {error}
          </div>
        )}

        {/* Headline & Exposure Grid */}
        {data && (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="p-4 rounded-xl bg-zinc-950/80 border border-zinc-800">
              <span className="text-zinc-500 text-[10px] uppercase font-bold tracking-wider">Direct Exposure</span>
              <div className="text-xl font-bold font-mono text-white mt-1">
                {data.portfolio_exposure_pct.toFixed(1)}%
              </div>
              <span className="text-[10px] text-zinc-400 font-mono">
                ${data.portfolio_holding_value.toLocaleString()} ({data.portfolio_holding_shares} shares)
              </span>
            </div>

            <div className="p-4 rounded-xl bg-zinc-950/80 border border-zinc-800">
              <span className="text-zinc-500 text-[10px] uppercase font-bold tracking-wider">Sentiment Assessment</span>
              <div className={`text-base font-bold font-mono mt-1 ${
                data.sentiment_impact === 'BEARISH' ? 'text-rose-400' :
                data.sentiment_impact === 'BULLISH' ? 'text-emerald-400' : 'text-zinc-300'
              }`}>
                {data.sentiment_impact}
              </div>
              <span className="text-[10px] text-zinc-400">
                Grounding Confidence: High
              </span>
            </div>

            <div className="p-4 rounded-xl bg-zinc-950/80 border border-zinc-800">
              <span className="text-zinc-500 text-[10px] uppercase font-bold tracking-wider">Affected Holdings</span>
              <div className="text-sm font-bold font-mono text-indigo-300 mt-1">
                {data.direct_holdings_affected.length > 0 ? data.direct_holdings_affected.join(', ') : 'None directly held'}
              </div>
              <span className="text-[10px] text-zinc-400">
                Cross-referenced with ledger
              </span>
            </div>
          </div>
        )}

        {/* Supply Chain Knowledge Graph Contagion Links */}
        {data && data.supply_chain_links.length > 0 && (
          <div className="p-4 rounded-xl bg-zinc-950/60 border border-zinc-800 space-y-2">
            <div className="flex items-center gap-1.5 text-zinc-300 font-bold uppercase tracking-wider text-[11px]">
              <Link2 className="w-3.5 h-3.5 text-cyan-400" />
              <span>Supply Chain & Competitor Graph Links</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mt-2">
              {data.supply_chain_links.map((link, idx) => (
                <div key={idx} className="p-2.5 rounded-lg bg-zinc-900 border border-zinc-800/80 font-mono text-[11px]">
                  <div className="flex items-center justify-between font-bold text-white mb-1">
                    <span>{link.source_ticker} ➔ {link.target_ticker}</span>
                    <span className="text-[9px] px-1.5 py-0.2 rounded bg-indigo-950 text-indigo-300 border border-indigo-800">
                      {link.relationship_type}
                    </span>
                  </div>
                  <p className="text-[11px] text-zinc-400 font-sans">{link.description}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Explainable AI Analysis Text (with real-time streaming) */}
        <div className="p-5 rounded-xl bg-zinc-950 border border-zinc-800/90 relative">
          <div className="flex items-center justify-between mb-3">
            <span className="text-zinc-400 font-bold uppercase tracking-wider text-[10px] flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
              Evidence-Grounded RAG Synthesis
            </span>
            {isStreaming && (
              <span className="text-[10px] font-mono text-indigo-400 animate-pulse">
                Streaming tokens...
              </span>
            )}
          </div>

          <div className="text-zinc-200 leading-relaxed text-xs whitespace-pre-wrap font-sans">
            {streamedText || data?.analysis_text || (
              <div className="text-zinc-500 py-4 text-center">
                Querying pgvector embeddings and generating synthesis...
              </div>
            )}
            {isStreaming && <span className="inline-block w-1.5 h-3.5 bg-indigo-400 ml-1 animate-pulse" />}
          </div>
        </div>

        {/* Grounded Evidence Citations */}
        {data && data.evidence_citations.length > 0 && (
          <div className="p-4 rounded-xl bg-zinc-950/60 border border-zinc-800 space-y-2">
            <div className="flex items-center gap-1.5 text-zinc-300 font-bold uppercase tracking-wider text-[11px]">
              <FileText className="w-3.5 h-3.5 text-indigo-400" />
              <span>Grounded Evidence Citations (Source Anchored)</span>
            </div>
            <div className="space-y-2 mt-2">
              {data.evidence_citations.map((c, i) => (
                <div key={i} className="p-3 rounded-lg bg-zinc-900/80 border border-zinc-800">
                  <div className="flex items-center justify-between text-[11px] font-semibold text-white mb-1">
                    <span>{c.source}: {c.title}</span>
                    <a
                      href={c.url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
                    >
                      Article <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>
                  <p className="text-[11px] text-zinc-400 italic">
                    "{c.snippet}"
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Mandatory Regulatory Disclaimer */}
        <div className="p-3.5 rounded-xl bg-zinc-950 border border-amber-900/40 text-amber-300/80 text-[10px] flex items-start gap-2.5">
          <ShieldAlert className="w-4 h-4 shrink-0 text-amber-400 mt-0.5" />
          <p className="leading-normal">
            {data?.regulatory_disclaimer || (
              "DISCLAIMER: Non-advisory decision support only. This analysis does not constitute investment advice. Past performance is not indicative of future results."
            )}
          </p>
        </div>
      </div>
    </dialog>
  );
}
