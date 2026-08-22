import React from 'react';
import {
  LayoutGrid,
  CloudSun,
  TrendingUp,
  Landmark,
  Bell,
  Bot,
  Settings,
  Sprout
} from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab }) {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutGrid },
    { id: 'weather', label: 'Weather', icon: CloudSun },
    { id: 'market', label: 'Market', icon: TrendingUp },
    { id: 'subsidies', label: 'Subsidies', icon: Landmark },
    { id: 'alerts', label: 'Alerts', icon: Bell },
  ];

  return (
    <aside className="w-64 bg-[#05180f]/85 backdrop-blur-md border-r border-[#153e2a] flex flex-col justify-between p-5 min-h-screen sticky top-0 z-40 select-none">
      
      {/* Top Brand Logo */}
      <div className="space-y-8">
        <div className="flex items-center gap-3 px-2">
          <div className="w-10 h-10 rounded-full border border-emerald-500/40 bg-emerald-950/60 flex items-center justify-center text-emerald-400 shadow-md shadow-emerald-900/30">
            <Sprout className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white tracking-wide leading-none">
              Krishivaani
            </h1>
            <p className="text-[11px] text-emerald-400 font-medium tracking-tight mt-0.5">
              Empowering Farmers
            </p>
          </div>
        </div>

        {/* Navigation Menu */}
        <nav className="space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;

            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center gap-3.5 px-4 py-3 rounded-xl font-medium text-sm transition-all duration-200 ${
                  isActive
                    ? 'bg-[#29783d] text-white shadow-lg shadow-emerald-900/40 font-semibold'
                    : 'text-slate-300 hover:text-white hover:bg-[#0e2c1e]'
                }`}
              >
                <Icon className={`w-5 h-5 ${isActive ? 'text-white' : 'text-slate-300'}`} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Bottom Settings Link */}
      <div className="pt-4 border-t border-[#153e2a]">
        <button
          onClick={() => setActiveTab('settings')}
          className={`w-full flex items-center gap-3.5 px-4 py-3 rounded-xl font-medium text-sm transition-all ${
            activeTab === 'settings'
              ? 'bg-[#29783d] text-white font-semibold'
              : 'text-slate-300 hover:text-white hover:bg-[#0e2c1e]'
          }`}
        >
          <Settings className="w-5 h-5 text-slate-300" />
          <span>Settings</span>
        </button>
      </div>

    </aside>
  );
}
