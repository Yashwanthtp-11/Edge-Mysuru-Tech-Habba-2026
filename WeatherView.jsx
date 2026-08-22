import React, { useState } from 'react';
import PredictionCard from './PredictionCard';
import WeatherMetricsCard from './WeatherMetricsCard';
import ShapExplanationCard from './ShapExplanationCard';
import ForecastCharts from './ForecastCharts';
import HourlyCards from './HourlyCards';
import { geocodeLocation } from '../services/api';
import { Search, MapPin, Sparkles } from 'lucide-react';

export default function WeatherView({
  data,
  explanation,
  currentLocation,
  onSelectLocation,
}) {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);

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

  const PRESET_LOCATIONS = [
    { name: 'Mysuru, India', lat: 12.2958, lon: 76.6394 },
    { name: 'Mumbai, India', lat: 19.0760, lon: 72.8777 },
    { name: 'Chennai, India', lat: 13.0827, lon: 80.2707 },
    { name: 'London, UK', lat: 51.5074, lon: -0.1278 },
    { name: 'Seattle, USA', lat: 47.6062, lon: -122.3321 },
  ];

  return (
    <div className="space-y-6 pb-12">
      
      {/* Header & Geocoding Search Bar */}
      <div className="bg-[#0b271a]/90 border border-[#164931] p-5 rounded-2xl flex flex-col md:flex-row items-center justify-between gap-4 shadow-xl">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-emerald-400" />
            AI Weather & XGBoost Rainfall Predictions
          </h2>
          <p className="text-xs text-slate-300 mt-1">
            Real-time inference using Open-Meteo API data & trained ML models
          </p>
        </div>

        {/* Location Search Input */}
        <div className="w-full md:w-auto flex flex-col sm:flex-row items-center gap-2 relative">
          <form onSubmit={handleSearch} className="relative w-full sm:w-72">
            <input
              type="text"
              placeholder="Search location (e.g. Mysuru)..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-[#061b12] border border-[#13422c] rounded-xl text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-500"
            />
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-2.5" />
            
            {searchResults.length > 0 && (
              <div className="absolute left-0 right-0 top-11 bg-[#092217] border border-[#164931] rounded-xl shadow-2xl overflow-hidden z-50 max-h-56 overflow-y-auto">
                {searchResults.map((item) => (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => handleSelectResult(item)}
                    className="w-full text-left px-3.5 py-2 hover:bg-[#113826] text-xs text-slate-200 border-b border-[#14422e] last:border-0 flex items-center justify-between"
                  >
                    <span>
                      <strong className="text-white">{item.name}</strong>
                      {item.admin1 && `, ${item.admin1}`}, {item.country}
                    </span>
                    <span className="text-[10px] text-slate-400 font-mono">
                      {item.latitude.toFixed(2)}, {item.longitude.toFixed(2)}
                    </span>
                  </button>
                ))}
              </div>
            )}
          </form>

          {/* Location Presets */}
          <div className="flex items-center gap-1 overflow-x-auto w-full sm:w-auto">
            {PRESET_LOCATIONS.map((loc) => (
              <button
                key={loc.name}
                onClick={() => onSelectLocation(loc)}
                className={`px-2.5 py-1.5 text-[11px] rounded-lg border whitespace-nowrap transition-all ${
                  currentLocation.name === loc.name
                    ? 'bg-[#29783d] text-white border-emerald-500 font-semibold'
                    : 'bg-[#061b12] text-slate-400 border-[#13422c] hover:text-slate-200'
                }`}
              >
                {loc.name.split(',')[0]}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Predictions Content */}
      {data && (
        <div className="space-y-6">
          <PredictionCard
            prediction={data.prediction}
            locationName={currentLocation.name}
          />

          <WeatherMetricsCard weather={data.weather} />

          {explanation && <ShapExplanationCard explanation={explanation} />}

          <ForecastCharts hourlyData={data.hourly_forecast} />

          <HourlyCards hourlyData={data.hourly_forecast} />
        </div>
      )}

    </div>
  );
}
