import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import KrishivaaniHeader from './components/KrishivaaniHeader';
import DashboardView from './components/DashboardView';
import WeatherView from './components/WeatherView';
import { MarketView, SubsidiesView, AlertsView, SettingsView } from './components/OtherViews';
import { predictRainfall, getExplanation, getHealth } from './services/api';
import { Loader2, AlertCircle, RefreshCw } from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  const [currentLocation, setCurrentLocation] = useState({
    name: 'Mysuru, Karnataka',
    lat: 12.2958,
    lon: 76.6394,
  });

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [weatherData, setWeatherData] = useState(null);
  const [explanation, setExplanation] = useState(null);
  const [backendHealth, setBackendHealth] = useState(null);

  // Check Backend Status
  useEffect(() => {
    getHealth()
      .then((res) => setBackendHealth(res))
      .catch(() => setBackendHealth({ status: 'offline', models_loaded: false }));
  }, []);

  // Fetch Weather & XGBoost Prediction Data
  const fetchData = async (location) => {
    setLoading(true);
    setError(null);
    try {
      const predRes = await predictRainfall(location.lat, location.lon);
      setWeatherData(predRes);

      // Fetch SHAP Explanation
      const expRes = await getExplanation(location.lat, location.lon);
      setExplanation(expRes);
    } catch (err) {
      console.error('API Error:', err);
      setError(
        err.response?.data?.detail ||
          'Unable to connect to FastAPI ML backend at http://localhost:8000. Please check server status.'
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData(currentLocation);
  }, [currentLocation]);

  const handleSelectLocation = (loc) => {
    setCurrentLocation(loc);
  };

  return (
    <div className="min-h-screen text-slate-100 flex bg-black/25 backdrop-blur-[2px]">
      
      {/* Left Sidebar */}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        
        {/* Top Header */}
        <KrishivaaniHeader />

        {/* Dynamic View Body */}
        <main className="flex-1 p-6 max-w-7xl w-full mx-auto">
          
          {/* Backend Connection Alert if needed */}
          {backendHealth && !backendHealth.models_loaded && (
            <div className="mb-6 bg-amber-500/10 border border-amber-500/30 p-4 rounded-xl flex items-center justify-between text-xs text-amber-300">
              <div className="flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-amber-400" />
                <span>
                  Backend connection loading... Models status: training/evaluating.
                </span>
              </div>
              <button
                onClick={() => fetchData(currentLocation)}
                className="px-2.5 py-1 bg-amber-500/20 hover:bg-amber-500/30 text-amber-200 rounded-lg flex items-center gap-1"
              >
                <RefreshCw className="w-3 h-3" /> Retry
              </button>
            </div>
          )}

          {/* Loading Indicator */}
          {loading && (
            <div className="flex flex-col items-center justify-center py-20 space-y-4">
              <Loader2 className="w-10 h-10 text-emerald-500 animate-spin" />
              <p className="text-xs text-slate-400 font-medium">
                Fetching Open-Meteo weather data & running XGBoost ML inference...
              </p>
            </div>
          )}

          {/* Error Message */}
          {error && !loading && (
            <div className="bg-red-500/10 border border-red-500/30 p-6 rounded-2xl text-center space-y-3">
              <AlertCircle className="w-10 h-10 text-red-400 mx-auto" />
              <h3 className="text-base font-bold text-red-300">Backend Connection Error</h3>
              <p className="text-xs text-slate-400 max-w-md mx-auto">{error}</p>
              <button
                onClick={() => fetchData(currentLocation)}
                className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-semibold shadow-lg shadow-emerald-900/30"
              >
                Try Again
              </button>
            </div>
          )}

          {/* Render Active View */}
          {!loading && !error && (
            <>
              {activeTab === 'dashboard' && (
                <DashboardView
                  weatherData={weatherData}
                  currentLocation={currentLocation}
                  setActiveTab={setActiveTab}
                />
              )}

              {activeTab === 'weather' && (
                <WeatherView
                  data={weatherData}
                  explanation={explanation}
                  currentLocation={currentLocation}
                  onSelectLocation={handleSelectLocation}
                />
              )}

              {activeTab === 'market' && <MarketView />}
              {activeTab === 'subsidies' && <SubsidiesView />}
              {activeTab === 'alerts' && <AlertsView />}
              {activeTab === 'ai-assistant' && (
                <DashboardView
                  weatherData={weatherData}
                  currentLocation={currentLocation}
                  setActiveTab={setActiveTab}
                />
              )}
              {activeTab === 'settings' && <SettingsView />}
            </>
          )}

        </main>
      </div>

    </div>
  );
}
