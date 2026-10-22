import React, { useState } from 'react';
import { 
  Activity, 
  TrendingUp, 
  TrendingDown, 
  Zap, 
  Sparkles, 
  Radio, 
  ExternalLink,
  Flame
} from 'lucide-react';
import { api } from '../api';

export default function MarketWatch({ 
  quotes, 
  news, 
  onAnomalyInjected, 
  onExplainTicker, 
  onTradeTicker 
}) {
  const [injectTicker, setInjectTicker] = useState("TSMC");
  const [injectPct, setInjectPct] = useState("-0.085");
  const [injectHeadline, setInjectHeadline] = useState("Tainan Substation Disruption Causes 8.5% Plunge");
  const [isInjecting, setIsInjecting] = useState(false);
  const [injectMsg, setInjectMsg] = useState("");

  const handleInject = async (e) => {
    e.preventDefault();
    setIsInjecting(true);
    setInjectMsg("");

    try {
      const pct = parseFloat(injectPct);
      await api.injectAnomaly(
        injectTicker,
        pct,
        injectHeadline,
        `Intraday market disruption on ${injectTicker}: unexpected technical failure causing production suspension.`
      );
      // Run anomaly scan to generate notifications
      await api.runAnomalyScan();
      setInjectMsg(`Successfully injected ${(pct * 100).toFixed(1)}% anomaly on ${injectTicker}! Alerts generated.`);
      setIsInjecting(false);
      onAnomalyInjected();
    } catch (err) {
      setInjectMsg(`Injection failed: ${err.message}`);
      setIsInjecting(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Top Banner: Anomaly Simulator & Testing Sandbox */}
      <div className="bg-gradient-to-r from-indigo-950/60 via-zinc-900 to-zinc-900/80 border border-indigo-800/40 rounded-2xl p-6 relative overflow-hidden shadow-lg shadow-indigo-950/20">
        <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
          <div className="max-w-xl">
            <div className="flex items-center gap-2 text-indigo-400 text-xs font-bold uppercase tracking-wider mb-2">
              <Zap className="w-4 h-4 text-indigo-400 animate-pulse" />
              <span>Real-Time Anomaly Testing Sandbox</span>
            </div>
            <h2 className="text-lg font-bold text-white tracking-tight">
              Test Market Anomaly Pipeline & Decision Support
            </h2>
            <p className="text-xs text-zinc-400 mt-1">
              Simulate an 8%+ sudden price move or supply-chain shock to test automated portfolio exposure detection, 
              background alert routing, and RAG-grounded impact explanation.
            </p>
          </div>

          <form onSubmit={handleInject} className="flex flex-wrap items-center gap-3 w-full lg:w-auto">
            <select
              value={injectTicker}
              onChange={(e) => {
                setInjectTicker(e.target.value);
                setInjectHeadline(`${e.target.value} Incurs Sudden Volatility Following Regulatory Report`);
              }}
              className="bg-zinc-950 border border-zinc-800 rounded-xl px-3 py-2 text-xs font-mono font-bold text-white focus:outline-none focus:ring-1 focus:ring-indigo-500"
            >
              {quotes.map(q => (
                <option key={q.ticker} value={q.ticker}>{q.ticker}</option>
              ))}
            </select>

            <select
              value={injectPct}
              onChange={(e) => setInjectPct(e.target.value)}
              className="bg-zinc-950 border border-zinc-800 rounded-xl px-3 py-2 text-xs font-mono font-bold text-white focus:outline-none focus:ring-1 focus:ring-indigo-500"
            >
              <option value="-0.085">-8.5% Flash Drop</option>
              <option value="-0.120">-12.0% Severe Plunge</option>
              <option value="0.095">+9.5% Sudden Surge</option>
              <option value="0.150">+15.0% Mega Spike</option>
            </select>

            <button
              type="submit"
              disabled={isInjecting}
              className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs shadow-md shadow-indigo-600/30 transition flex items-center gap-1.5 shrink-0"
            >
              <Flame className="w-3.5 h-3.5 text-amber-300" />
              {isInjecting ? 'Simulating...' : 'Inject Anomaly'}
            </button>
          </form>
        </div>

        {injectMsg && (
          <div className="mt-4 p-2.5 rounded-lg bg-indigo-950/80 border border-indigo-700/50 text-indigo-300 text-xs font-mono">
            {injectMsg}
          </div>
        )}
      </div>

      {/* Live Market Tickers Grid */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">Consolidated Watcher Quotes</h3>
            <p className="text-xs text-zinc-400 mt-0.5">Automated queue deduplicating held tickers across active accounts</p>
          </div>
          <div className="flex items-center gap-1.5 text-xs text-emerald-400 font-mono">
            <Radio className="w-3.5 h-3.5 animate-pulse" />
            <span>Feed Active (TTL 60s)</span>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
          {quotes.map((q) => {
            const isUp = q.change >= 0;
            return (
              <div
                key={q.ticker}
                className="bg-zinc-900/60 border border-zinc-800/80 hover:border-zinc-700 rounded-2xl p-4 transition shadow-sm relative overflow-hidden group"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <span className="font-extrabold text-base text-white font-mono tracking-tight">{q.ticker}</span>
                    <span className="ml-2 text-[10px] px-1.5 py-0.2 rounded bg-zinc-800 text-zinc-400 font-sans">
                      {q.source}
                    </span>
                  </div>

                  <div className={`flex items-center gap-0.5 text-xs font-mono font-bold ${
                    isUp ? 'text-emerald-400' : 'text-rose-400'
                  }`}>
                    {isUp ? <TrendingUp className="w-3.5 h-3.5" /> : <TrendingDown className="w-3.5 h-3.5" />}
                    <span>{isUp ? '+' : ''}{q.change_percent.toFixed(2)}%</span>
                  </div>
                </div>

                <div className="mt-3">
                  <div className="text-2xl font-bold font-mono text-white">
                    ${q.price.toFixed(2)}
                  </div>
                  <div className="text-[11px] text-zinc-400 font-mono mt-0.5">
                    Prev: ${q.previous_close?.toFixed(2) || '—'}
                  </div>
                </div>

                {/* Actions on hover */}
                <div className="mt-4 pt-3 border-t border-zinc-800/60 flex items-center justify-between gap-2">
                  <button
                    onClick={() => onExplainTicker(q.ticker)}
                    className="flex-1 py-1 px-2 rounded-lg bg-indigo-950/60 hover:bg-indigo-900/80 border border-indigo-700/50 text-indigo-300 text-[11px] font-semibold transition flex items-center justify-center gap-1"
                  >
                    <Sparkles className="w-3 h-3 text-indigo-400" />
                    Explain
                  </button>
                  <button
                    onClick={() => onTradeTicker(q.ticker)}
                    className="flex-1 py-1 px-2 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-[11px] font-semibold transition"
                  >
                    Trade
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Financial News Wire */}
      <div className="bg-zinc-900/60 border border-zinc-800 rounded-2xl overflow-hidden shadow-sm">
        <div className="px-6 py-4 border-b border-zinc-800 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">Financial News Feed & Vector Store</h3>
            <p className="text-xs text-zinc-400 mt-0.5">Chunked and embedded for hybrid semantic RAG retrieval</p>
          </div>
        </div>

        <div className="divide-y divide-zinc-800/60">
          {news.map((item) => (
            <div key={item.id} className="p-5 hover:bg-zinc-800/20 transition">
              <div className="flex items-center gap-2 mb-1.5">
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-zinc-800 text-zinc-300 font-medium">
                  {item.source}
                </span>
                <span className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold ${
                  item.sentiment_label === 'BULLISH'
                    ? 'bg-emerald-950/80 text-emerald-400 border border-emerald-800'
                    : item.sentiment_label === 'BEARISH'
                    ? 'bg-rose-950/80 text-rose-400 border border-rose-800'
                    : 'bg-zinc-800 text-zinc-400'
                }`}>
                  {item.sentiment_label}
                </span>
                <span className="text-[11px] text-zinc-500 font-mono">
                  {new Date(item.published_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>

              <h4 className="text-sm font-bold text-white hover:text-indigo-300 transition">
                {item.title}
              </h4>
              <p className="text-xs text-zinc-400 mt-1 line-clamp-2">
                {item.content_raw}
              </p>

              <div className="flex items-center justify-between mt-3 text-xs">
                <div className="flex items-center gap-1.5">
                  <span className="text-[11px] text-zinc-500">Related Assets:</span>
                  {(item.ticker_tags || "").split(",").map(t => (
                    <span key={t} className="text-[10px] font-mono font-bold px-1.5 py-0.5 bg-zinc-800 text-zinc-300 rounded">
                      {t.trim()}
                    </span>
                  ))}
                </div>

                <a 
                  href={item.url} 
                  target="_blank" 
                  rel="noreferrer"
                  className="text-indigo-400 hover:text-indigo-300 text-[11px] flex items-center gap-1"
                >
                  Source Link <ExternalLink className="w-3 h-3" />
                </a>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
