import React from 'react';
import { CloudRain, Sun, Droplets } from 'lucide-react';

export default function HourlyCards({ hourlyData }) {
  if (!hourlyData || hourlyData.length === 0) return null;

  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider px-1">
        Hourly Weather Cards (Next 24 Hours)
      </h3>

      <div className="flex items-center gap-3 overflow-x-auto pb-3 pt-1 scrollbar-thin">
        {hourlyData.slice(0, 24).map((item, idx) => {
          const date = new Date(item.timestamp);
          const timeStr = isNaN(date.getTime())
            ? item.timestamp.split('T')[1]?.substring(0, 5) || item.timestamp
            : date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

          const isRain = item.rain_probability > 40 || item.precipitation > 0.1;

          return (
            <div
              key={idx}
              className={`min-w-[110px] p-3.5 rounded-xl border flex flex-col items-center justify-between gap-2.5 transition-all hover:border-blue-500/50 ${
                isRain
                  ? 'bg-blue-950/40 border-blue-800/40'
                  : 'bg-slate-900 border-slate-800'
              }`}
            >
              <span className="text-xs text-slate-400 font-medium">{timeStr}</span>

              <div className="my-1">
                {isRain ? (
                  <CloudRain className="w-7 h-7 text-blue-400" />
                ) : (
                  <Sun className="w-7 h-7 text-amber-400" />
                )}
              </div>

              <div className="text-center space-y-0.5">
                <div className="text-sm font-bold text-slate-100 font-mono">
                  {item.temperature.toFixed(1)}°C
                </div>
                <div className="text-[11px] text-blue-400 font-medium flex items-center justify-center gap-0.5 font-mono">
                  <Droplets className="w-3 h-3 text-blue-400" />
                  {item.rain_probability}%
                </div>
                {item.precipitation > 0 && (
                  <div className="text-[10px] text-cyan-300 font-mono">
                    {item.precipitation} mm
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
