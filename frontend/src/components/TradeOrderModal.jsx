import React, { useState, useEffect } from 'react';
import { X, ArrowRight, ShieldCheck, AlertCircle } from 'lucide-react';
import { api } from '../api';

export default function TradeOrderModal({ 
  isOpen, 
  onClose, 
  portfolio, 
  quotes = [], 
  defaultTicker = "NVDA", 
  onOrderSuccess 
}) {
  const [ticker, setTicker] = useState(defaultTicker);
  const [side, setSide] = useState('BUY');
  const [orderType, setOrderType] = useState('MARKET');
  const [quantity, setQuantity] = useState('10');
  const [limitPrice, setLimitPrice] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  // Keyboard Escape listener
  useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  // Sync default ticker if prop changes
  useEffect(() => {
    if (defaultTicker) setTicker(defaultTicker);
  }, [defaultTicker]);

  if (!isOpen) return null;

  const currentQuote = quotes.find(q => q.ticker === ticker) || { price: 150.0 };
  const currentPrice = currentQuote.price;
  const numQty = parseFloat(quantity) || 0;
  const effectivePrice = orderType === 'LIMIT' ? (parseFloat(limitPrice) || currentPrice) : currentPrice;
  const totalCost = (numQty * effectivePrice).toFixed(2);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!portfolio) {
      setError("No active portfolio selected");
      return;
    }

    if (numQty <= 0) {
      setError("Order quantity must be greater than zero");
      return;
    }

    if (orderType === 'LIMIT' && (!limitPrice || parseFloat(limitPrice) <= 0)) {
      setError("A valid limit price is required for limit orders");
      return;
    }

    setError('');
    setIsSubmitting(true);

    try {
      const idempotencyKey = "ord_" + Math.random().toString(36).substring(2, 12);
      const payload = {
        ticker: ticker.toUpperCase(),
        side,
        type: orderType,
        quantity: numQty,
        limit_price: orderType === 'LIMIT' ? parseFloat(limitPrice) : null
      };

      await api.placeOrder(portfolio.id, payload, idempotencyKey);
      setIsSubmitting(false);
      onOrderSuccess();
      onClose();
    } catch (err) {
      setError(err.message || 'Order execution failed');
      setIsSubmitting(false);
    }
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="tradeDialogTitle"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md overflow-y-auto animate-in fade-in duration-200"
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div className="relative rounded-2xl bg-[#0f131c] border border-slate-700/80 text-zinc-100 shadow-2xl max-w-md w-full overflow-hidden p-6 my-auto ring-1 ring-white/10">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-5">
          <div>
            <h3 id="tradeDialogTitle" className="text-base font-bold text-white tracking-tight">
              Simulated Trade Desk
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Account: <span className="font-semibold text-slate-200">{portfolio?.name}</span>
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3 rounded-xl bg-rose-950/60 border border-rose-800/80 text-rose-300 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Side Selector (BUY vs SELL) */}
          <div className="grid grid-cols-2 gap-2 p-1 bg-[#090c10] rounded-xl border border-slate-800">
            <button
              type="button"
              onClick={() => setSide('BUY')}
              className={`py-2 rounded-lg text-xs font-bold transition-all ${
                side === 'BUY'
                  ? 'bg-emerald-600 text-white shadow-md shadow-emerald-600/30'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              BUY / LONG
            </button>
            <button
              type="button"
              onClick={() => setSide('SELL')}
              className={`py-2 rounded-lg text-xs font-bold transition-all ${
                side === 'SELL'
                  ? 'bg-rose-600 text-white shadow-md shadow-rose-600/30'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              SELL / SHORT
            </button>
          </div>

          {/* Ticker & Order Type */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-[11px] font-medium text-slate-400 mb-1">Asset Ticker</label>
              <select
                value={ticker}
                onChange={(e) => setTicker(e.target.value)}
                className="w-full bg-[#141925] border border-slate-700/80 rounded-xl px-3 py-2 text-xs font-mono font-bold text-white focus:outline-none focus:ring-1 focus:ring-indigo-500"
              >
                {quotes.map(q => (
                  <option key={q.ticker} value={q.ticker}>
                    {q.ticker} (${q.price.toFixed(2)})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-[11px] font-medium text-slate-400 mb-1">Order Execution</label>
              <select
                value={orderType}
                onChange={(e) => setOrderType(e.target.value)}
                className="w-full bg-[#141925] border border-slate-700/80 rounded-xl px-3 py-2 text-xs font-medium text-white focus:outline-none focus:ring-1 focus:ring-indigo-500"
              >
                <option value="MARKET">Market Order</option>
                <option value="LIMIT">Limit Order</option>
              </select>
            </div>
          </div>

          {/* Quantity & Limit Price */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-[11px] font-medium text-slate-400 mb-1">Share Quantity</label>
              <input
                type="number"
                min="0.1"
                step="any"
                value={quantity}
                onChange={(e) => setQuantity(e.target.value)}
                required
                className="w-full bg-[#141925] border border-slate-700/80 rounded-xl px-3 py-2 text-xs font-mono text-white focus:outline-none focus:ring-1 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="block text-[11px] font-medium text-slate-400 mb-1">
                {orderType === 'LIMIT' ? 'Limit Price ($)' : 'Estimated Market Price'}
              </label>
              <input
                type="number"
                min="0.01"
                step="any"
                disabled={orderType === 'MARKET'}
                value={orderType === 'LIMIT' ? limitPrice : currentPrice.toFixed(2)}
                onChange={(e) => setLimitPrice(e.target.value)}
                placeholder={currentPrice.toFixed(2)}
                className={`w-full bg-[#141925] border border-slate-700/80 rounded-xl px-3 py-2 text-xs font-mono ${
                  orderType === 'MARKET' ? 'text-slate-500 bg-[#10141d]/50' : 'text-white'
                } focus:outline-none focus:ring-1 focus:ring-indigo-500`}
              />
            </div>
          </div>

          {/* Double-entry Ledger Preview */}
          <div className="p-3.5 rounded-xl bg-[#141925] border border-slate-800 space-y-1.5 text-xs font-mono">
            <div className="flex justify-between text-slate-400">
              <span>Estimated Value:</span>
              <span className="font-semibold text-white">${totalCost}</span>
            </div>
            {orderType === 'LIMIT' && side === 'BUY' && (
              <div className="flex justify-between text-amber-400 text-[11px]">
                <span>Escrow Reserved Cash:</span>
                <span>${totalCost}</span>
              </div>
            )}
            <div className="flex justify-between text-slate-400 text-[11px]">
              <span>Available Balance:</span>
              <span>${portfolio?.virtual_cash_balance?.toLocaleString(undefined, { minimumFractionDigits: 2 })}</span>
            </div>
          </div>

          {/* Submit */}
          <button
            type="submit"
            disabled={isSubmitting}
            className={`w-full py-2.5 rounded-xl font-bold text-xs transition-all shadow-md flex items-center justify-center gap-1.5 ${
              side === 'BUY'
                ? 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-emerald-600/20'
                : 'bg-rose-600 hover:bg-rose-500 text-white shadow-rose-600/20'
            } ${isSubmitting ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            {isSubmitting ? 'Processing Transaction...' : `Confirm ${side} Order`}
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
}
