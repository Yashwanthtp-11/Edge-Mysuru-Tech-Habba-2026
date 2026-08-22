import React, { useState } from 'react';
import { Search, Bell, Plus, ChevronDown, User } from 'lucide-react';

export default function KrishivaaniHeader({ onSearchSubmit }) {
  const [query, setQuery] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (onSearchSubmit && query) {
      onSearchSubmit(query);
    }
  };

  return (
    <header className="flex items-center justify-between gap-4 py-4 px-6 bg-[#05140d]/80 backdrop-blur-md sticky top-0 z-30 border-b border-[#123624]">
      
      {/* Search Input */}
      <form onSubmit={handleSubmit} className="relative w-full max-w-md">
        <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
        <input
          type="text"
          placeholder="Search..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="w-full pl-10 pr-4 py-2 bg-[#0c2419] border border-[#16422e] rounded-full text-sm text-slate-100 placeholder-slate-400 focus:outline-none focus:border-emerald-500 transition-colors"
        />
      </form>

      {/* Right Header Actions */}
      <div className="flex items-center gap-4">
        
        {/* Bell Notification */}
        <button className="p-2.5 rounded-full bg-[#0c2419] border border-[#16422e] text-slate-300 hover:text-white hover:bg-[#123624] transition-colors relative">
          <Bell className="w-4 h-4" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-emerald-500 rounded-full animate-ping" />
        </button>

        {/* Plus Quick Action Button */}
        <button className="p-2.5 rounded-full bg-[#29783d] text-white hover:bg-[#226834] transition-colors shadow-md shadow-emerald-950">
          <Plus className="w-4 h-4" />
        </button>

        {/* User Profile Avatar (Blank Photo) */}
        <div className="flex items-center gap-3 pl-2 border-l border-[#16422e]">
          <div className="w-9 h-9 rounded-full bg-[#0c2419] border border-emerald-500/40 flex items-center justify-center text-slate-400">
            <User className="w-5 h-5 text-slate-400" />
          </div>
          <div className="hidden sm:block text-left">
            <h4 className="text-xs font-semibold text-white leading-tight">
              Farm Owner
            </h4>
          </div>
          <ChevronDown className="w-4 h-4 text-slate-400" />
        </div>

      </div>
    </header>
  );
}
