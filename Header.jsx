import React, { useState } from 'react';
import { Search, MapPin, Sparkles, Navigation } from 'lucide-react';
import { geocodeLocation } from '../services/api';

const PRESET_LOCATIONS = [
  { name: 'Mysuru, India', lat: 12.2958, lon: 76.6394 },
  { name: 'Mumbai, India', lat: 19.0760, lon: 72.8777 },
  { name: 'Chennai, India', lat: 13.0827, lon: 80.2707 },
  { name: 'London, UK', lat: 51.5074, lon: -0.1278 },
  { name: 'Seattle, USA', lat: 47.6062, lon: -122.3321 },
  { name: 'Tokyo, Japan', lat: 35.6762, lon: 139.6503 },
];

export default function Header({ currentLocation, onSelectLocation, loading }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [customLat, setCustomLat] = useState('');
  const [customLon, setCustomLon] = useState('');

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    setIsSearching(true);
    const results = await geocodeLocation(searchQuery);
    setSearchResults(results);
    setIsSearching(false);
  };

  const handleSelectResult = (item) => {
    onSelectLocation({
      name: `${item.name}${item.admin1 ? ', ' + item.admin1 : ''}, ${item.country || ''}`,
      lat: item.latitude,
      lon: item.longitude,
    });
    setSearchResults([]);
    setSearchQuery('');
  };

  const handleCustomCoordinatesSubmit = (e) => {
    e.preventDefault();
    const lat = parseFloat(customLat);
    const lon = parseFloat(customLon);
    if (!isNaN(lat) && !isNaN(lon)) {
      onSelectLocation({
        name: `Custom Location (${lat.toFixed(2)}, ${lon.toFixed(2)})`,
        lat,
        lon
      });
    }
  };

  return (
    <header className="bg-slate-900/80 backdrop-blur-md border-b border-slate-800 sticky top-0 z-50 py-4 px-4 sm:px-8">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        
        {/* Brand Title */}
        <div className="flex items-center gap-3 w-full md:w-auto justify-between md:justify-start">
          <div className="flex items-center gap-2">
            <div className="p-2.5 bg-blue-600/20 text-blue-400 rounded-xl border border-blue-500/30 shadow-lg shadow-blue-500/10">
              <Sparkles className="w-6 h-6 animate-pulse" />
            </div>
            <div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 via-cyan-300 to-indigo-400 bg-clip-text text-transparent">
                WeatherAI
              </h1>
              <p className="text-xs text-slate-400">XGBoost ML Rainfall Engine</p>
            </div>
          </div>
          
          <div className="md:hidden text-xs px-2.5 py-1 bg-slate-800 text-slate-300 rounded-full border border-slate-700 flex items-center gap-1.5">
            <MapPin className="w-3.5 h-3.5 text-blue-400" />
            {currentLocation.name.split(',')[0]}
          </div>
        </div>

        {/* Search Bar & Location Selector */}
        <div className="flex flex-col sm:flex-row items-center gap-3 w-full md:w-auto relative">
          
          {/* Geocoding Search Form */}
          <form onSubmit={handleSearch} className="relative w-full sm:w-72">
            <input
              type="text"
              placeholder="Search city (e.g. Mysuru, London)..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors"
            />
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            
            {/* Search Dropdown Results */}
            {searchResults.length > 0 && (
              <div className="absolute left-0 right-0 top-12 bg-slate-900 border border-slate-800 rounded-xl shadow-2xl overflow-hidden z-50 max-h-60 overflow-y-auto">
                {searchResults.map((item) => (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => handleSelectResult(item)}
                    className="w-full text-left px-4 py-2.5 hover:bg-slate-800 text-xs text-slate-200 border-b border-slate-800/50 last:border-0 flex items-center justify-between"
                  >
                    <span>
                      <strong className="font-semibold text-slate-100">{item.name}</strong>
                      {item.admin1 && `, ${item.admin1}`}, {item.country}
                    </span>
                    <span className="text-slate-500 font-mono text-[10px]">
                      {item.latitude.toFixed(2)}, {item.longitude.toFixed(2)}
                    </span>
                  </button>
                ))}
              </div>
            )}
          </form>

          {/* Preset City Pills */}
          <div className="flex items-center gap-1.5 overflow-x-auto max-w-full py-1 scrollbar-none">
            {PRESET_LOCATIONS.map((loc) => (
              <button
                key={loc.name}
                onClick={() => onSelectLocation(loc)}
                disabled={loading}
                className={`px-3 py-1.5 text-xs rounded-lg transition-all whitespace-nowrap border ${
                  currentLocation.name === loc.name
                    ? 'bg-blue-600 text-white border-blue-500 font-medium shadow-md shadow-blue-600/20'
                    : 'bg-slate-900 text-slate-400 border-slate-800 hover:text-slate-200 hover:bg-slate-800'
                }`}
              >
                {loc.name.split(',')[0]}
              </button>
            ))}
          </div>

        </div>

      </div>
    </header>
  );
}
