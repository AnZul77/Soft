import React, { useState, useEffect, useRef } from 'react';
import { X, ArrowRight, ShieldCheck, AlertCircle } from 'lucide-react';
import { api } from '../api';

export default function TradeOrderModal({ 
  isOpen, 
  onClose, 
  portfolio, 
  quotes, 
  defaultTicker = "NVDA", 
  onOrderSuccess 
}) {
  const dialogRef = useRef(null);
  const [ticker, setTicker] = useState(defaultTicker);
  const [side, setSide] = useState('BUY');
  const [orderType, setOrderType] = useState('MARKET');
  const [quantity, setQuantity] = useState('10');
  const [limitPrice, setLimitPrice] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  // Synchronize modal state with native <dialog>
  useEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) return;

    if (isOpen) {
      if (!dialog.open) {
        dialog.showModal();
      }
    } else {
      if (dialog.open) {
        dialog.close();
      }
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
    if (defaultTicker) setTicker(defaultTicker);
  }, [defaultTicker]);

  const currentQuote = quotes.find(q => q.ticker === ticker);
  const currentPrice = currentQuote ? currentQuote.price : 100.0;
  const numQty = parseFloat(quantity) || 0;
  const effectivePrice = orderType === 'LIMIT' ? (parseFloat(limitPrice) || currentPrice) : currentPrice;
  const totalCost = (numQty * effectivePrice).toFixed(2);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (numQty <= 0) {
      setError("Quantity must be greater than 0");
      return;
    }

    if (orderType === 'LIMIT' && (!limitPrice || parseFloat(limitPrice) <= 0)) {
      setError("Please specify a valid limit price > 0");
      return;
    }

    setIsSubmitting(true);
    try {
      const idempotencyKey = "ord-" + crypto.randomUUID();
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
      setError(err.message);
      setIsSubmitting(false);
    }
  };

  return (
    <dialog
      ref={dialogRef}
      closedby="any"
      onClose={onClose}
      aria-labelledby="tradeDialogTitle"
      className="m-auto rounded-2xl bg-zinc-900 border border-zinc-800 text-zinc-100 shadow-2xl max-w-md w-full overflow-hidden p-0"
    >
      <div className="p-6">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-zinc-800 pb-4 mb-5">
          <div>
            <h3 id="tradeDialogTitle" className="text-base font-bold text-white tracking-tight">
              Simulated Trade Desk
            </h3>
            <p className="text-xs text-zinc-400 mt-0.5">
              Account: <span className="font-semibold text-zinc-300">{portfolio?.name}</span>
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-zinc-400 hover:text-white hover:bg-zinc-800 transition"
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
          <div className="grid grid-cols-2 gap-2 p-1 bg-zinc-950 rounded-xl border border-zinc-800">
            <button
              type="button"
              onClick={() => setSide('BUY')}
              className={`py-2 rounded-lg text-xs font-bold transition-all ${
                side === 'BUY'
                  ? 'bg-emerald-600 text-white shadow-md shadow-emerald-600/30'
                  : 'text-zinc-400 hover:text-white'
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
                  : 'text-zinc-400 hover:text-white'
              }`}
            >
              SELL / SHORT
            </button>
          </div>

          {/* Ticker & Order Type */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-[11px] font-medium text-zinc-400 mb-1">Asset Ticker</label>
              <select
                value={ticker}
                onChange={(e) => setTicker(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-3 py-2 text-xs font-mono font-bold text-white focus:outline-none focus:ring-1 focus:ring-indigo-500"
              >
                {quotes.map(q => (
                  <option key={q.ticker} value={q.ticker}>
                    {q.ticker} (${q.price.toFixed(2)})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-[11px] font-medium text-zinc-400 mb-1">Order Execution</label>
              <select
                value={orderType}
                onChange={(e) => setOrderType(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-3 py-2 text-xs font-medium text-white focus:outline-none focus:ring-1 focus:ring-indigo-500"
              >
                <option value="MARKET">Market Order</option>
                <option value="LIMIT">Limit Order</option>
              </select>
            </div>
          </div>

          {/* Quantity & Limit Price */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-[11px] font-medium text-zinc-400 mb-1">Share Quantity</label>
              <input
                type="number"
                min="0.1"
                step="any"
                value={quantity}
                onChange={(e) => setQuantity(e.target.value)}
                required
                className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-3 py-2 text-xs font-mono text-white focus:outline-none focus:ring-1 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="block text-[11px] font-medium text-zinc-400 mb-1">
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
                className={`w-full bg-zinc-950 border border-zinc-800 rounded-xl px-3 py-2 text-xs font-mono ${
                  orderType === 'MARKET' ? 'text-zinc-500 bg-zinc-950/50' : 'text-white'
                } focus:outline-none focus:ring-1 focus:ring-indigo-500`}
              />
            </div>
          </div>

          {/* Double-entry Ledger Preview */}
          <div className="p-3.5 rounded-xl bg-zinc-950/70 border border-zinc-800/80 space-y-1.5 text-xs font-mono">
            <div className="flex justify-between text-zinc-400">
              <span>Estimated Value:</span>
              <span className="font-semibold text-white">${totalCost}</span>
            </div>
            {orderType === 'LIMIT' && side === 'BUY' && (
              <div className="flex justify-between text-amber-400 text-[11px]">
                <span>Escrow Reserved Cash:</span>
                <span>${totalCost}</span>
              </div>
            )}
            <div className="flex justify-between text-zinc-400 text-[11px]">
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
    </dialog>
  );
}
