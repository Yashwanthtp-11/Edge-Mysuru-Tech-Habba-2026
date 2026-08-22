import React from 'react';
import {
  TrendingUp,
  Landmark,
  Bell,
  Bot,
  Settings as SettingsIcon,
  CheckCircle,
  AlertTriangle,
  ExternalLink,
  ChevronRight
} from 'lucide-react';

export function MarketView() {
  const marketItems = [
    { crop: 'Tomato', price: '₹2,450 / qtl', change: '+5.2%', status: 'high' },
    { crop: 'Onion', price: '₹1,820 / qtl', change: '-1.4%', status: 'low' },
    { crop: 'Potato', price: '₹1,450 / qtl', change: '+2.1%', status: 'high' },
    { crop: 'Wheat', price: '₹2,275 / qtl', change: '+0.8%', status: 'high' },
    { crop: 'Paddy / Rice', price: '₹2,183 / qtl', change: '0.0%', status: 'neutral' },
  ];

  return (
    <div className="space-y-6 pb-10">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <TrendingUp className="w-6 h-6 text-emerald-400" />
            Agriculture Market & Mandi Prices
          </h2>
          <p className="text-xs text-slate-300 mt-1">
            Real-time APMC Mandi commodity rates in Mysuru & Karnataka
          </p>
        </div>
        <span className="text-xs text-emerald-400 bg-[#0b271a] px-3 py-1.5 rounded-xl border border-[#164931]">
          Updated 10 mins ago
        </span>
      </div>

      <div className="bg-[#0b271a]/90 border border-[#164931] rounded-2xl p-5 shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-[#13422c] text-slate-400">
                <th className="pb-3 px-3">Crop Name</th>
                <th className="pb-3 px-3">Current Price</th>
                <th className="pb-3 px-3">Daily Change</th>
                <th className="pb-3 px-3">Trend</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#13422c]">
              {marketItems.map((item, i) => (
                <tr key={i} className="hover:bg-[#061b12]">
                  <td className="py-3.5 px-3 font-semibold text-white">{item.crop}</td>
                  <td className="py-3.5 px-3 font-mono font-bold text-slate-200">{item.price}</td>
                  <td className={`py-3.5 px-3 font-mono font-bold ${item.status === 'high' ? 'text-emerald-400' : 'text-red-400'}`}>
                    {item.change}
                  </td>
                  <td className="py-3.5 px-3">
                    <span className="px-2.5 py-1 rounded-full text-[10px] font-bold bg-[#061b12] border border-[#13422c] text-emerald-300">
                      APMC Verified
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export function SubsidiesView() {
  const schemes = [
    { title: 'PM-KISAN Samman Nidhi', desc: 'Financial benefit of ₹6,000 per year in 3 equal installments.', status: 'Active Eligible' },
    { title: 'Pradhan Mantri Fasal Bima Yojana', desc: 'Crop insurance coverage against natural calamities & crop failure.', status: 'Apply Now' },
    { title: 'Kisan Credit Card Scheme', desc: 'Short-term credit loans for agricultural needs at subsidized interest rates.', status: 'Enrolled' },
    { title: 'Soil Health Card Scheme', desc: 'Soil testing & customized nutrient recommendation for higher yields.', status: 'Available' },
  ];

  return (
    <div className="space-y-6 pb-10">
      <div>
        <h2 className="text-2xl font-bold text-white flex items-center gap-2">
          <Landmark className="w-6 h-6 text-amber-400" />
          Government Schemes & Subsidies
        </h2>
        <p className="text-xs text-slate-300 mt-1">
          Explore agricultural subsidies and financial assistance schemes
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {schemes.map((s, i) => (
          <div key={i} className="bg-[#0b271a]/90 border border-[#164931] p-5 rounded-2xl space-y-3 flex flex-col justify-between">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <h3 className="text-base font-bold text-white">{s.title}</h3>
                <span className="text-[10px] px-2.5 py-1 rounded-full bg-[#061b12] text-amber-300 border border-amber-800/40 font-semibold">
                  {s.status}
                </span>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">{s.desc}</p>
            </div>
            <button className="text-xs font-semibold text-emerald-400 flex items-center gap-1 hover:text-emerald-300 pt-2">
              View Details <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

export function AlertsView() {
  return (
    <div className="space-y-6 pb-10">
      <div>
        <h2 className="text-2xl font-bold text-white flex items-center gap-2">
          <Bell className="w-6 h-6 text-red-400" />
          Important Farm Alerts & Risk Notifications
        </h2>
        <p className="text-xs text-slate-300 mt-1">
          Real-time weather warnings, price surges, and crop disease advisories
        </p>
      </div>

      <div className="space-y-3">
        <div className="p-4 rounded-2xl bg-[#1c120c] border border-red-900/50 flex items-start gap-4">
          <AlertTriangle className="w-6 h-6 text-red-400 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <div className="flex items-center justify-between">
              <h4 className="text-sm font-bold text-red-300">Heavy Rainfall Warning (Open-Meteo Alert)</h4>
              <span className="text-xs text-slate-400">2 hours ago</span>
            </div>
            <p className="text-xs text-slate-300">
              Your area (Mysuru district) may receive heavy rainfall tomorrow. Ensure proper drainage in fields to prevent waterlogging.
            </p>
          </div>
        </div>

        <div className="p-4 rounded-2xl bg-[#1c1a0c] border border-amber-900/50 flex items-start gap-4">
          <AlertTriangle className="w-6 h-6 text-amber-400 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <div className="flex items-center justify-between">
              <h4 className="text-sm font-bold text-amber-300">Tomato Market Surge Alert</h4>
              <span className="text-xs text-slate-400">5 hours ago</span>
            </div>
            <p className="text-xs text-slate-300">
              Tomato wholesale prices surged by +5.2% in APMC Mysuru Mandi reaching ₹2,450 / qtl.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export function SettingsView() {
  return (
    <div className="space-y-6 pb-10 max-w-2xl">
      <div>
        <h2 className="text-2xl font-bold text-white flex items-center gap-2">
          <SettingsIcon className="w-6 h-6 text-slate-300" />
          Application Settings
        </h2>
        <p className="text-xs text-slate-300 mt-1">
          Manage farm preferences, notifications, and language settings
        </p>
      </div>

      <div className="bg-[#0b271a]/90 border border-[#164931] p-5 rounded-2xl space-y-4">
        <div className="flex items-center justify-between border-b border-[#13422c] pb-3">
          <div>
            <h4 className="text-sm font-semibold text-white">Default Farm Location</h4>
            <p className="text-xs text-slate-400">Mysuru, Karnataka (12.2958° N, 76.6394° E)</p>
          </div>
          <button className="text-xs text-emerald-400 font-semibold hover:underline">Change</button>
        </div>

        <div className="flex items-center justify-between border-b border-[#13422c] pb-3">
          <div>
            <h4 className="text-sm font-semibold text-white">AI Model Engine</h4>
            <p className="text-xs text-slate-400">XGBoost Classifier + XGBoost Regressor (SHAP Explainability)</p>
          </div>
          <span className="text-xs px-2.5 py-1 bg-emerald-950 text-emerald-300 rounded-full border border-emerald-800 font-semibold">Active</span>
        </div>

        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-sm font-semibold text-white">Language / भाषा</h4>
            <p className="text-xs text-slate-400">English (Kannada & Hindi available)</p>
          </div>
          <button className="text-xs text-emerald-400 font-semibold hover:underline">Select</button>
        </div>
      </div>
    </div>
  );
}
