import React from 'react';
import { Cpu, ArrowUpRight, ArrowDownRight, Layers } from 'lucide-react';

export default function ShapExplanationCard({ explanation }) {
  if (!explanation || !explanation.top_factors) return null;

  const getImpactBadge = (dir) => {
    if (dir.includes('+')) {
      return (
        <span className="px-2.5 py-1 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20 text-xs font-mono font-bold flex items-center gap-1">
          <ArrowUpRight className="w-3.5 h-3.5 text-blue-400" />
          {dir} Increases Rain
        </span>
      );
    } else {
      return (
        <span className="px-2.5 py-1 rounded bg-slate-800 text-slate-400 border border-slate-700 text-xs font-mono font-bold flex items-center gap-1">
          <ArrowDownRight className="w-3.5 h-3.5 text-slate-500" />
          {dir} Lowers Rain
        </span>
      );
    }
  };

  const formatFeatureName = (name) => {
    return name
      .replace(/_/g, ' ')
      .replace(/\b\w/g, (l) => l.toUpperCase());
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <Cpu className="w-5 h-5 text-indigo-400" />
          <h3 className="text-base font-semibold text-slate-100">
            SHAP Model Explainability (XGBoost)
          </h3>
        </div>
        <span className="text-xs text-slate-400 bg-slate-950 px-2.5 py-1 rounded-lg border border-slate-800">
          Base ML Probability: <strong className="text-indigo-300">{explanation.base_probability}%</strong>
        </span>
      </div>

      <p className="text-xs text-slate-400">
        Top feature factors driving the rainfall prediction for this location:
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
        {explanation.top_factors.map((factor, idx) => (
          <div
            key={idx}
            className="bg-slate-950/80 border border-slate-800/80 p-3 rounded-xl flex items-center justify-between hover:border-slate-700 transition-colors"
          >
            <div className="space-y-0.5">
              <span className="text-xs font-medium text-slate-200 block">
                {formatFeatureName(factor.feature)}
              </span>
              <span className="text-[10px] text-slate-500 font-mono">
                SHAP score: {factor.importance_value > 0 ? '+' : ''}{factor.importance_value.toFixed(4)}
              </span>
            </div>
            <div>{getImpactBadge(factor.impact_direction)}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
