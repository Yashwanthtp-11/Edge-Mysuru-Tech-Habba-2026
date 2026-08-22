import React, { useState } from 'react';
import {
  CloudSun,
  TrendingUp,
  Landmark,
  Bell,
  Calendar,
  MapPin,
  CloudRain,
  Sun,
  CloudLightning,
  AlertTriangle,
  Bot,
  Mic,
  Camera,
  MessageSquare,
  ArrowRight,
  Send,
  Droplets,
  Wind
} from 'lucide-react';

export default function DashboardView({ weatherData, currentLocation, setActiveTab }) {
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState([
    {
      sender: 'assistant',
      text: 'Hello! How can I help you today? You can ask me anything about farming, crops, weather, or markets.'
    }
  ]);

  const handleAsk = (e) => {
    e.preventDefault();
    if (!question.trim()) return;
    const userText = question;
    setMessages((prev) => [
      ...prev,
      { sender: 'user', text: userText },
      {
        sender: 'assistant',
        text: `Based on your farm location (${currentLocation.name}), the XGBoost ML model forecasts a ${
          weatherData?.prediction?.rain_probability || 48
        }% probability of rain today with expected temperature around ${
          weatherData?.weather?.temperature || 22
        }°C.`
      }
    ]);
    setQuestion('');
  };

  const weatherMetrics = weatherData?.weather || {
    temperature: 22.0,
    humidity: 62.0,
    wind_speed: 12.0,
  };

  const predictionMetrics = weatherData?.prediction || {
    rain_probability: 35.0,
    expected_rainfall_mm: 0.1,
    risk_level: 'LOW',
  };

  return (
    <div className="space-y-6 pb-10">
      
      {/* Welcome Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            Welcome back <span className="inline-block animate-bounce">👋</span>
          </h2>
          <p className="text-xs text-slate-300 mt-1">
            Here's what's happening on your farm today.
          </p>
        </div>

        {/* Date Range Picker */}
        <div className="flex items-center gap-2 px-3.5 py-2 bg-[#0a2318] border border-[#174630] rounded-xl text-xs text-slate-200 shadow-md">
          <Calendar className="w-4 h-4 text-emerald-400" />
          <span>Jun 20 – Jun 26, 2024</span>
        </div>
      </div>

      {/* Main Grid: Left KPI & AI Assistant, Right Weather Today & Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Column (Span 2) */}
        <div className="lg:col-span-2 space-y-6">
          
          {/* Top 4 KPI Cards */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            
            {/* Card 1: Weather */}
            <div
              onClick={() => setActiveTab('weather')}
              className="bg-[#0b271a]/90 border border-[#164931] hover:border-emerald-500/50 p-4 rounded-2xl cursor-pointer transition-all hover:scale-[1.02]"
            >
              <div className="flex items-center gap-2.5 mb-3">
                <div className="p-2 rounded-xl bg-emerald-950/80 text-emerald-400 border border-emerald-800/40">
                  <CloudSun className="w-5 h-5" />
                </div>
                <span className="text-xs font-semibold text-slate-200">Weather</span>
              </div>
              <div className="text-2xl font-bold text-white font-mono">
                {Math.round(weatherMetrics.temperature)}°C
              </div>
              <div className="text-xs text-slate-400 mt-0.5">Partly Cloudy</div>
            </div>

            {/* Card 2: Market */}
            <div
              onClick={() => setActiveTab('market')}
              className="bg-[#0b271a]/90 border border-[#164931] hover:border-emerald-500/50 p-4 rounded-2xl cursor-pointer transition-all hover:scale-[1.02]"
            >
              <div className="flex items-center gap-2.5 mb-3">
                <div className="p-2 rounded-xl bg-emerald-950/80 text-emerald-400 border border-emerald-800/40">
                  <TrendingUp className="w-5 h-5" />
                </div>
                <span className="text-xs font-semibold text-slate-200">Market</span>
              </div>
              <div className="text-xl font-bold text-white font-mono">
                ₹2,450 <span className="text-xs font-normal text-slate-400">/ qtl</span>
              </div>
              <div className="text-xs text-emerald-400 font-medium mt-0.5 flex items-center gap-1">
                <span>↑ 5.2%</span>
              </div>
            </div>

            {/* Card 3: Subsidies */}
            <div
              onClick={() => setActiveTab('subsidies')}
              className="bg-[#0b271a]/90 border border-[#164931] hover:border-emerald-500/50 p-4 rounded-2xl cursor-pointer transition-all hover:scale-[1.02]"
            >
              <div className="flex items-center gap-2.5 mb-3">
                <div className="p-2 rounded-xl bg-emerald-950/80 text-emerald-400 border border-emerald-800/40">
                  <Landmark className="w-5 h-5" />
                </div>
                <span className="text-xs font-semibold text-slate-200">Subsidies</span>
              </div>
              <div className="text-2xl font-bold text-white font-mono">
                6 <span className="text-xs font-normal text-slate-300">Schemes</span>
              </div>
              <div className="text-xs text-slate-400 mt-0.5">Available</div>
            </div>

            {/* Card 4: Alerts */}
            <div
              onClick={() => setActiveTab('alerts')}
              className="bg-[#0b271a]/90 border border-[#164931] hover:border-emerald-500/50 p-4 rounded-2xl cursor-pointer transition-all hover:scale-[1.02]"
            >
              <div className="flex items-center gap-2.5 mb-3">
                <div className="p-2 rounded-xl bg-emerald-950/80 text-emerald-400 border border-emerald-800/40">
                  <Bell className="w-5 h-5" />
                </div>
                <span className="text-xs font-semibold text-slate-200">Alerts</span>
              </div>
              <div className="text-2xl font-bold text-white font-mono">
                2 <span className="text-xs font-normal text-slate-300">Alerts</span>
              </div>
              <div className="text-xs text-slate-400 mt-0.5">Important</div>
            </div>

          </div>

          {/* AI FARM ASSISTANT Box */}
          <div className="bg-[#0b271a]/90 border border-[#164931] rounded-2xl p-5 space-y-4 shadow-xl">
            <div className="flex items-center gap-2 text-emerald-400">
              <Bot className="w-5 h-5" />
              <h3 className="text-xs font-bold uppercase tracking-wider">
                AI FARM ASSISTANT
              </h3>
            </div>

            {/* Messages Display */}
            <div className="space-y-3 max-h-48 overflow-y-auto pr-1">
              {messages.map((m, idx) => (
                <div
                  key={idx}
                  className={`p-3.5 rounded-2xl text-xs max-w-md ${
                    m.sender === 'user'
                      ? 'bg-emerald-700 text-white ml-auto'
                      : 'bg-[#061b12] border border-[#13422c] text-slate-200'
                  }`}
                >
                  {m.text}
                </div>
              ))}
            </div>

            {/* Action Buttons Row (Voice, Image, Chat) */}
            <div className="flex items-center gap-6 pt-2 justify-center sm:justify-start">
              <button className="flex flex-col items-center gap-1.5 text-xs text-slate-300 hover:text-emerald-400">
                <div className="p-3 rounded-full bg-[#071f15] border border-[#14472f] hover:border-emerald-500">
                  <Mic className="w-4 h-4 text-emerald-400" />
                </div>
                <span>Voice</span>
              </button>
              <button className="flex flex-col items-center gap-1.5 text-xs text-slate-300 hover:text-emerald-400">
                <div className="p-3 rounded-full bg-[#071f15] border border-[#14472f] hover:border-emerald-500">
                  <Camera className="w-4 h-4 text-emerald-400" />
                </div>
                <span>Image</span>
              </button>
              <button className="flex flex-col items-center gap-1.5 text-xs text-slate-300 hover:text-emerald-400">
                <div className="p-3 rounded-full bg-[#071f15] border border-[#14472f] hover:border-emerald-500">
                  <MessageSquare className="w-4 h-4 text-emerald-400" />
                </div>
                <span>Chat</span>
              </button>
            </div>

            {/* Input Question Box */}
            <form onSubmit={handleAsk} className="relative pt-2">
              <input
                type="text"
                placeholder="Type your question..."
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                className="w-full pl-4 pr-12 py-3 bg-[#061b12] border border-[#13422c] rounded-full text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-500"
              />
              <button
                type="submit"
                className="absolute right-2 top-3.5 p-1.5 rounded-full bg-[#29783d] text-white hover:bg-emerald-600 transition-colors"
              >
                <Send className="w-3.5 h-3.5" />
              </button>
            </form>
          </div>

        </div>

        {/* Right Column: Weather Today & Alerts */}
        <div className="space-y-6">
          
          {/* Weather Today Widget */}
          <div className="bg-[#0b271a]/90 border border-[#164931] rounded-2xl p-5 space-y-4 shadow-xl">
            <div className="flex items-center justify-between border-b border-[#13422c] pb-3">
              <div>
                <h3 className="text-sm font-semibold text-white">Weather Today</h3>
                <p className="text-xs text-slate-400 flex items-center gap-1 mt-0.5">
                  <MapPin className="w-3.5 h-3.5 text-emerald-400" />
                  {currentLocation.name}
                </p>
              </div>
              <CloudSun className="w-9 h-9 text-amber-400" />
            </div>

            {/* Main Temperature Display */}
            <div className="flex items-baseline gap-3">
              <span className="text-4xl font-bold text-white font-mono">
                {Math.round(weatherMetrics.temperature)}°C
              </span>
              <span className="text-xs text-slate-300 font-medium">Partly Cloudy</span>
            </div>

            {/* Stats Row */}
            <div className="grid grid-cols-3 gap-2 py-2 border-y border-[#13422c] text-xs">
              <div>
                <span className="text-[10px] text-slate-400 block">💧 Humidity</span>
                <span className="font-bold text-slate-100 font-mono">
                  {Math.round(weatherMetrics.humidity)}%
                </span>
              </div>
              <div>
                <span className="text-[10px] text-slate-400 block">💨 Wind</span>
                <span className="font-bold text-slate-100 font-mono">
                  {Math.round(weatherMetrics.wind_speed)} km/h
                </span>
              </div>
              <div>
                <span className="text-[10px] text-slate-400 block">🌧️ ML Rain</span>
                <span className="font-bold text-emerald-400 font-mono">
                  {predictionMetrics.rain_probability}%
                </span>
              </div>
            </div>

            {/* 7-Day Forecast Horizontal Row */}
            <div>
              <h4 className="text-[11px] font-semibold text-slate-400 mb-2">
                7-Day Forecast
              </h4>
              <div className="grid grid-cols-5 gap-1.5 text-center">
                <div className="p-2 rounded-xl bg-[#061b12] border border-[#13422c]">
                  <span className="text-[10px] text-slate-400 block mb-1">Mon</span>
                  <CloudRain className="w-4 h-4 text-blue-400 mx-auto mb-1" />
                  <span className="text-[10px] text-slate-200 font-mono">24°/18°</span>
                </div>
                <div className="p-2 rounded-xl bg-[#061b12] border border-[#13422c]">
                  <span className="text-[10px] text-slate-400 block mb-1">Tue</span>
                  <CloudLightning className="w-4 h-4 text-amber-400 mx-auto mb-1" />
                  <span className="text-[10px] text-slate-200 font-mono">23°/17°</span>
                </div>
                <div className="p-2 rounded-xl bg-[#061b12] border border-[#13422c]">
                  <span className="text-[10px] text-slate-400 block mb-1">Wed</span>
                  <CloudSun className="w-4 h-4 text-emerald-400 mx-auto mb-1" />
                  <span className="text-[10px] text-slate-200 font-mono">24°/18°</span>
                </div>
                <div className="p-2 rounded-xl bg-[#061b12] border border-[#13422c]">
                  <span className="text-[10px] text-slate-400 block mb-1">Thu</span>
                  <Sun className="w-4 h-4 text-amber-400 mx-auto mb-1" />
                  <span className="text-[10px] text-slate-200 font-mono">26°/19°</span>
                </div>
                <div className="p-2 rounded-xl bg-[#061b12] border border-[#13422c]">
                  <span className="text-[10px] text-slate-400 block mb-1">Fri</span>
                  <CloudSun className="w-4 h-4 text-amber-400 mx-auto mb-1" />
                  <span className="text-[10px] text-slate-200 font-mono">27°/20°</span>
                </div>
              </div>
            </div>
          </div>

          {/* Alerts Widget */}
          <div className="bg-[#0b271a]/90 border border-[#164931] rounded-2xl p-5 space-y-3 shadow-xl">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-white">Alerts</h3>
              <button
                onClick={() => setActiveTab('alerts')}
                className="text-xs text-emerald-400 hover:underline font-medium"
              >
                View All
              </button>
            </div>

            {/* Alert 1 */}
            <div className="p-3 rounded-xl bg-[#1c120c] border border-red-900/40 space-y-1">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-red-400 flex items-center gap-1.5">
                  <AlertTriangle className="w-3.5 h-3.5 text-red-400" />
                  Heavy rainfall expected tomorrow
                </span>
                <span className="text-[10px] text-slate-400">2h ago</span>
              </div>
              <p className="text-[11px] text-slate-300">
                Your area may receive 60–80mm rainfall.
              </p>
            </div>

            {/* Alert 2 */}
            <div className="p-3 rounded-xl bg-[#1c1a0c] border border-amber-900/40 space-y-1">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-amber-400 flex items-center gap-1.5">
                  <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
                  Tomato prices increased by 5.2%
                </span>
                <span className="text-[10px] text-slate-400">5h ago</span>
              </div>
              <p className="text-[11px] text-slate-300">
                Check the market for more details.
              </p>
            </div>
          </div>

        </div>

      </div>

      {/* Bottom 4 Feature Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 pt-2">
        
        {/* Card 1: Weather */}
        <div className="bg-[#0b271a]/90 border border-[#164931] p-5 rounded-2xl space-y-3 flex flex-col justify-between">
          <div className="space-y-2">
            <div className="w-10 h-10 rounded-xl bg-blue-950 border border-blue-800/40 flex items-center justify-center text-blue-400">
              <CloudRain className="w-5 h-5" />
            </div>
            <h4 className="text-sm font-bold text-white">Weather</h4>
            <p className="text-xs text-slate-400 leading-snug">
              Get real-time weather updates and XGBoost rainfall forecasts.
            </p>
          </div>
          <button
            onClick={() => setActiveTab('weather')}
            className="text-xs font-semibold text-emerald-400 flex items-center gap-1 hover:text-emerald-300 pt-2"
          >
            View Weather <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Card 2: Market */}
        <div className="bg-[#0b271a]/90 border border-[#164931] p-5 rounded-2xl space-y-3 flex flex-col justify-between">
          <div className="space-y-2">
            <div className="w-10 h-10 rounded-xl bg-emerald-950 border border-emerald-800/40 flex items-center justify-center text-emerald-400">
              <TrendingUp className="w-5 h-5" />
            </div>
            <h4 className="text-sm font-bold text-white">Market</h4>
            <p className="text-xs text-slate-400 leading-snug">
              Check latest market prices and price trends.
            </p>
          </div>
          <button
            onClick={() => setActiveTab('market')}
            className="text-xs font-semibold text-emerald-400 flex items-center gap-1 hover:text-emerald-300 pt-2"
          >
            View Market <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Card 3: Subsidies */}
        <div className="bg-[#0b271a]/90 border border-[#164931] p-5 rounded-2xl space-y-3 flex flex-col justify-between">
          <div className="space-y-2">
            <div className="w-10 h-10 rounded-xl bg-amber-950 border border-amber-800/40 flex items-center justify-center text-amber-400">
              <Landmark className="w-5 h-5" />
            </div>
            <h4 className="text-sm font-bold text-white">Subsidies</h4>
            <p className="text-xs text-slate-400 leading-snug">
              Explore government schemes and subsidies.
            </p>
          </div>
          <button
            onClick={() => setActiveTab('subsidies')}
            className="text-xs font-semibold text-emerald-400 flex items-center gap-1 hover:text-emerald-300 pt-2"
          >
            View Subsidies <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Card 4: Alerts */}
        <div className="bg-[#0b271a]/90 border border-[#164931] p-5 rounded-2xl space-y-3 flex flex-col justify-between">
          <div className="space-y-2">
            <div className="w-10 h-10 rounded-xl bg-red-950 border border-red-800/40 flex items-center justify-center text-red-400">
              <Bell className="w-5 h-5" />
            </div>
            <h4 className="text-sm font-bold text-white">Alerts</h4>
            <p className="text-xs text-slate-400 leading-snug">
              Stay updated with important alerts and notifications.
            </p>
          </div>
          <button
            onClick={() => setActiveTab('alerts')}
            className="text-xs font-semibold text-emerald-400 flex items-center gap-1 hover:text-emerald-300 pt-2"
          >
            View Alerts <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

      </div>

    </div>
  );
}
