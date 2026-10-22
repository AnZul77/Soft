import React from 'react';
import { 
  Bell, 
  Check, 
  Sparkles, 
  TrendingDown, 
  TrendingUp, 
  AlertTriangle 
} from 'lucide-react';

export default function AnomalyAlertsFeed({ 
  alerts, 
  onMarkRead, 
  onExplainAlert 
}) {
  if (alerts.length === 0) {
    return (
      <div className="text-center py-12 bg-zinc-900/40 border border-zinc-800 rounded-2xl">
        <div className="w-10 h-10 rounded-xl bg-zinc-800 flex items-center justify-center mx-auto text-zinc-500 mb-2">
          <Bell className="w-5 h-5" />
        </div>
        <p className="text-zinc-400 text-xs">No active anomaly alerts. Use the Market Sandbox to simulate an event.</p>
      </div>
    );
  }

  return (
    <div className="bg-zinc-900/60 border border-zinc-800 rounded-2xl overflow-hidden shadow-sm">
      <div className="px-6 py-4 border-b border-zinc-800 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-rose-500 animate-pulse" />
          <h3 className="text-sm font-bold text-white uppercase tracking-wider">In-App Notification Center</h3>
        </div>
        <span className="text-xs font-mono text-zinc-400">
          {alerts.filter(a => a.status !== 'READ').length} Unread Alerts
        </span>
      </div>

      <div className="divide-y divide-zinc-800/60">
        {alerts.map((a) => {
          const isUnread = a.status !== 'READ';
          const isDrop = a.event_type === 'PRICE_DROP';

          return (
            <div 
              key={a.id} 
              className={`p-4 transition-all flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 ${
                isUnread ? 'bg-indigo-950/20 hover:bg-indigo-950/30' : 'hover:bg-zinc-800/20'
              }`}
            >
              <div className="flex items-start gap-3">
                <div className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 mt-0.5 ${
                  isDrop ? 'bg-rose-950/80 text-rose-400 border border-rose-800' : 'bg-emerald-950/80 text-emerald-400 border border-emerald-800'
                }`}>
                  {isDrop ? <TrendingDown className="w-4 h-4" /> : <TrendingUp className="w-4 h-4" />}
                </div>

                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-extrabold text-sm text-white font-mono">{a.ticker}</span>
                    <span className={`text-[10px] font-mono px-1.5 py-0.2 rounded font-bold ${
                      isDrop ? 'bg-rose-950 text-rose-400' : 'bg-emerald-950 text-emerald-400'
                    }`}>
                      {a.price_change_pct > 0 ? '+' : ''}{a.price_change_pct.toFixed(1)}%
                    </span>
                    {a.portfolio_exposure_pct > 0 && (
                      <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-amber-950/80 text-amber-400 border border-amber-800 font-semibold">
                        {a.portfolio_exposure_pct.toFixed(1)}% Exposure in Portfolio
                      </span>
                    )}
                  </div>

                  <p className="text-xs text-zinc-300 mt-1">
                    {a.message}
                  </p>

                  <div className="text-[10px] text-zinc-500 font-mono mt-1">
                    {new Date(a.created_at).toLocaleString()}
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2 self-end sm:self-center shrink-0">
                <button
                  onClick={() => onExplainAlert(a)}
                  className="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-sm transition flex items-center gap-1.5"
                >
                  <Sparkles className="w-3.5 h-3.5 text-indigo-200" />
                  Explain Impact
                </button>

                {isUnread && (
                  <button
                    onClick={() => onMarkRead(a.id)}
                    title="Mark as Read"
                    className="p-1.5 rounded-lg text-zinc-400 hover:text-emerald-400 hover:bg-zinc-800 transition"
                  >
                    <Check className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
