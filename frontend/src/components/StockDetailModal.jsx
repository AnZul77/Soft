import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { X, TrendingUp, TrendingDown, Calendar, DollarSign, BarChart2, Activity } from 'lucide-react';

export default function StockDetailModal({ isOpen, onClose, ticker, onTrade, onTradeTicker }) {
  const handleTrade = onTrade || onTradeTicker;
  const [period, setPeriod] = useState('30d');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [hoveredCandle, setHoveredCandle] = useState(null);

  useEffect(() => {
    if (isOpen && ticker) {
      fetchHistory(ticker, period);
    } else {
      setData(null);
      setHoveredCandle(null);
    }
  }, [isOpen, ticker, period]);

  const fetchHistory = async (sym, per) => {
    setLoading(true);
    setError('');
    try {
      const res = await api.getPriceHistory(sym, per);
      setData(res);
      if (res.candles && res.candles.length > 0) {
        setHoveredCandle(res.candles[res.candles.length - 1]);
      }
    } catch (err) {
      setError(err.message || 'Failed to fetch price history');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen || !ticker) return null;

  const candles = data?.candles || [];
  const prices = candles.map(c => c.close);
  const minPrice = prices.length > 0 ? Math.min(...prices) : 0;
  const maxPrice = prices.length > 0 ? Math.max(...prices) : 100;
  const priceRange = maxPrice - minPrice || 1;

  // Chart coordinates
  const svgWidth = 600;
  const svgHeight = 220;
  const paddingX = 20;
  const paddingY = 25;
  const usableWidth = svgWidth - paddingX * 2;
  const usableHeight = svgHeight - paddingY * 2;

  const points = candles.map((c, i) => {
    const x = paddingX + (i / (candles.length - 1 || 1)) * usableWidth;
    const y = svgHeight - paddingY - ((c.close - minPrice) / priceRange) * usableHeight;
    return { x, y, candle: c };
  });

  const pathD = points.length > 0 
    ? `M ${points[0].x} ${points[0].y} ` + points.slice(1).map(p => `L ${p.x} ${p.y}`).join(' ')
    : '';

  const areaD = points.length > 0
    ? `${pathD} L ${points[points.length - 1].x} ${svgHeight - paddingY} L ${points[0].x} ${svgHeight - paddingY} Z`
    : '';

  const isPositive = candles.length > 1 && candles[candles.length - 1].close >= candles[0].close;
  const strokeColor = isPositive ? '#10b981' : '#f43f5e';
  const fillColor = isPositive ? 'rgba(16, 185, 129, 0.15)' : 'rgba(244, 63, 94, 0.15)';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
      <div className="bg-zinc-900 border border-zinc-800 rounded-2xl w-full max-w-2xl overflow-hidden shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-zinc-800 bg-zinc-950/50">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-950/80 border border-indigo-700/60 flex items-center justify-center text-indigo-400 font-black text-sm">
              {ticker}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-bold text-white text-base tracking-tight">
                  {data?.company_name || ticker}
                </h3>
                <span className="text-xs font-mono text-zinc-400 uppercase">({ticker})</span>
              </div>
              <p className="text-xs text-zinc-400 flex items-center gap-2 mt-0.5">
                <span className="font-mono text-white font-semibold">
                  ${data?.current_price?.toFixed(2) || '—'}
                </span>
                <span className="text-[11px] text-zinc-500">• Intraday Live Tick</span>
              </p>
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
        <div className="p-6 space-y-5">
          {/* Controls: Period filters & Hover stats */}
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-1 bg-zinc-950 p-1 rounded-xl border border-zinc-800">
              {['7d', '30d', '90d', '1y'].map((p) => (
                <button
                  key={p}
                  onClick={() => setPeriod(p)}
                  className={`px-3 py-1 rounded-lg text-xs font-mono font-medium transition ${
                    period === p
                      ? 'bg-indigo-600 text-white shadow-sm'
                      : 'text-zinc-400 hover:text-white hover:bg-zinc-800/60'
                  }`}
                >
                  {p.toUpperCase()}
                </button>
              ))}
            </div>

            {hoveredCandle && (
              <div className="flex items-center gap-4 text-xs font-mono bg-zinc-950/60 px-3 py-1.5 rounded-xl border border-zinc-800/80">
                <span className="text-zinc-400">
                  {new Date(hoveredCandle.timestamp).toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' })}
                </span>
                <span className="text-zinc-300">
                  O: <span className="text-white">${hoveredCandle.open?.toFixed(2)}</span>
                </span>
                <span className="text-zinc-300">
                  H: <span className="text-emerald-400">${hoveredCandle.high?.toFixed(2)}</span>
                </span>
                <span className="text-zinc-300">
                  L: <span className="text-rose-400">${hoveredCandle.low?.toFixed(2)}</span>
                </span>
                <span className="text-zinc-300 font-bold">
                  C: <span className="text-indigo-400">${hoveredCandle.close?.toFixed(2)}</span>
                </span>
              </div>
            )}
          </div>

          {/* Interactive SVG Chart */}
          <div className="relative bg-zinc-950/80 border border-zinc-800/80 rounded-xl p-3 overflow-hidden">
            {loading ? (
              <div className="h-[220px] flex items-center justify-center text-xs text-zinc-500 gap-2">
                <Activity className="w-4 h-4 animate-spin text-indigo-400" />
                Loading price history series...
              </div>
            ) : error ? (
              <div className="h-[220px] flex items-center justify-center text-xs text-rose-400">
                {error}
              </div>
            ) : candles.length === 0 ? (
              <div className="h-[220px] flex items-center justify-center text-xs text-zinc-500">
                No historical candles available.
              </div>
            ) : (
              <svg 
                viewBox={`0 0 ${svgWidth} ${svgHeight}`} 
                className="w-full h-[220px] overflow-visible"
              >
                {/* Horizontal gridlines */}
                {[0.25, 0.5, 0.75].map((ratio) => {
                  const y = paddingY + usableHeight * ratio;
                  const priceAtY = maxPrice - ratio * priceRange;
                  return (
                    <g key={ratio}>
                      <line 
                        x1={paddingX} 
                        y1={y} 
                        x2={svgWidth - paddingX} 
                        y2={y} 
                        stroke="#27272a" 
                        strokeDasharray="4 4" 
                      />
                      <text 
                        x={svgWidth - paddingX + 4} 
                        y={y + 3} 
                        fill="#71717a" 
                        fontSize="9" 
                        fontFamily="monospace"
                      >
                        ${priceAtY.toFixed(1)}
                      </text>
                    </g>
                  );
                })}

                {/* Area Gradient */}
                <path d={areaD} fill={fillColor} />

                {/* Price Line */}
                <path 
                  d={pathD} 
                  fill="none" 
                  stroke={strokeColor} 
                  strokeWidth="2.5" 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                />

                {/* Interactive points / Hover targets */}
                {points.map((p, idx) => (
                  <circle
                    key={idx}
                    cx={p.x}
                    cy={p.y}
                    r={hoveredCandle === p.candle ? 5 : 2}
                    fill={hoveredCandle === p.candle ? '#ffffff' : strokeColor}
                    stroke={hoveredCandle === p.candle ? strokeColor : 'none'}
                    strokeWidth="2"
                    className="cursor-pointer transition-all"
                    onMouseEnter={() => setHoveredCandle(p.candle)}
                  />
                ))}
              </svg>
            )}
          </div>

          {/* Quick Metrics & Actions */}
          <div className="flex items-center justify-between pt-2 border-t border-zinc-800">
            <div className="flex items-center gap-6 text-xs text-zinc-400 font-mono">
              <div>
                <span className="block text-[10px] text-zinc-500 uppercase">Period High</span>
                <span className="font-bold text-emerald-400">${maxPrice.toFixed(2)}</span>
              </div>
              <div>
                <span className="block text-[10px] text-zinc-500 uppercase">Period Low</span>
                <span className="font-bold text-rose-400">${minPrice.toFixed(2)}</span>
              </div>
              <div>
                <span className="block text-[10px] text-zinc-500 uppercase">Candles</span>
                <span className="font-bold text-zinc-300">{candles.length} Days</span>
              </div>
            </div>

            {handleTrade && (
              <button
                onClick={() => {
                  onClose();
                  handleTrade(ticker);
                }}
                className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs shadow-md shadow-indigo-600/30 transition flex items-center gap-1.5"
              >
                <DollarSign className="w-3.5 h-3.5" />
                Trade {ticker}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
