import React from 'react';
import { CloudRain, AlertTriangle, ShieldCheck, Droplets, Info } from 'lucide-react';

export default function PredictionCard({ prediction, locationName }) {
  if (!prediction) return None;

  const { rain_probability, rain_prediction, expected_rainfall_mm, risk_level, open_meteo_probability } = prediction;

  const getRiskBadge = (level) => {
    switch (level) {
      case 'HIGH':
        return {
          bg: 'bg-red-500/10 border-red-500/30 text-red-400',
          dot: 'bg-red-500 animate-ping',
          icon: <AlertTriangle className="w-4 h-4 text-red-400" />
        };
      case 'MEDIUM':
        return {
          bg: 'bg-amber-500/10 border-amber-500/30 text-amber-400',
          dot: 'bg-amber-500',
          icon: <AlertTriangle className="w-4 h-4 text-amber-400" />
        };
      default:
        return {
          bg: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400',
          dot: 'bg-emerald-500',
          icon: <ShieldCheck className="w-4 h-4 text-emerald-400" />
        };
    }
  };

  const riskStyle = getRiskBadge(risk_level);

  return (
    <div className="bg-gradient-to-br from-slate-900 via-slate-900/90 to-blue-950/40 border border-slate-800 rounded-2xl p-6 shadow-2xl relative overflow-hidden">
      
      {/* Background Accent Glow */}
      <div className="absolute -right-16 -top-16 w-48 h-48 bg-blue-500/10 rounded-full blur-3xl pointer-events-none" />

      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6 relative z-10">
        
        {/* Left Side: Prediction Outcome & Probability */}
        <div className="space-y-4 max-w-lg">
          <div className="flex items-center gap-3">
            <span className="px-3 py-1 bg-blue-500/10 border border-blue-500/20 text-blue-400 rounded-full text-xs font-semibold uppercase tracking-wider">
              ML Rain Forecast (Next 1-Hour)
            </span>
            <div className={`px-3 py-1 rounded-full text-xs font-bold border flex items-center gap-1.5 ${riskStyle.bg}`}>
              <span className={`w-2 h-2 rounded-full ${riskStyle.dot}`} />
              {riskStyle.icon}
              RISK: {risk_level}
            </div>
          </div>

          <div>
            <h2 className="text-3xl font-extrabold text-white tracking-tight flex items-center gap-3">
              {rain_prediction ? (
                <>
                  <CloudRain className="w-8 h-8 text-blue-400 animate-bounce" />
                  <span className="text-blue-400">RAIN LIKELY</span>
                </>
              ) : (
                <>
                  <ShieldCheck className="w-8 h-8 text-emerald-400" />
                  <span className="text-slate-200">NO RAIN EXPECTED</span>
                </>
              )}
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Location: <strong className="text-slate-200">{locationName}</strong>
            </p>
          </div>

          {/* Metric Badges Grid */}
          <div className="grid grid-cols-2 gap-4 pt-2">
            <div className="bg-slate-950/60 border border-slate-800 p-3.5 rounded-xl">
              <span className="text-xs text-slate-400 block mb-1">Rain Probability</span>
              <span className="text-2xl font-bold text-blue-400 font-mono">
                {rain_probability}%
              </span>
            </div>
            <div className="bg-slate-950/60 border border-slate-800 p-3.5 rounded-xl">
              <span className="text-xs text-slate-400 block mb-1">Expected Rainfall</span>
              <span className="text-2xl font-bold text-cyan-300 font-mono">
                {expected_rainfall_mm} <span className="text-sm font-normal text-slate-400">mm</span>
              </span>
            </div>
          </div>
        </div>

        {/* Right Side: Custom ML vs Open-Meteo Benchmark Card */}
        <div className="w-full md:w-64 bg-slate-950 border border-slate-800/80 rounded-xl p-4 space-y-3">
          <div className="flex items-center justify-between text-xs border-b border-slate-800 pb-2">
            <span className="text-slate-400 flex items-center gap-1 font-medium">
              <Info className="w-3.5 h-3.5 text-blue-400" /> Model Comparison
            </span>
          </div>

          <div className="space-y-2 text-xs">
            <div className="flex justify-between items-center bg-blue-950/30 p-2 rounded-lg border border-blue-800/30">
              <span className="text-blue-300 font-medium">Custom XGBoost ML:</span>
              <span className="font-bold text-blue-400 font-mono text-sm">{rain_probability}%</span>
            </div>
            {open_meteo_probability !== undefined && (
              <div className="flex justify-between items-center bg-slate-900 p-2 rounded-lg border border-slate-800">
                <span className="text-slate-400">Open-Meteo Raw:</span>
                <span className="font-bold text-slate-300 font-mono text-sm">{open_meteo_probability}%</span>
              </div>
            )}
          </div>
          <p className="text-[10px] text-slate-500 italic leading-snug">
            *Custom ML model predicts 1-hour future target trained on historical weather time-series.
          </p>
        </div>

      </div>
    </div>
  );
}
