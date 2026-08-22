import React, { useState } from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Area,
  AreaChart,
} from 'recharts';
import { BarChart3, TrendingUp, Droplet } from 'lucide-react';

export default function ForecastCharts({ hourlyData }) {
  const [activeTab, setActiveTab] = useState('rainfall');

  if (!hourlyData || hourlyData.length === 0) return null;

  // Format timestamps for chart X-Axis (e.g. 14:00)
  const formattedData = hourlyData.map((item) => {
    const date = new Date(item.timestamp);
    const timeStr = isNaN(date.getTime())
      ? item.timestamp.split('T')[1]?.substring(0, 5) || item.timestamp
      : date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    return {
      ...item,
      timeLabel: timeStr,
    };
  });

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
      
      {/* Header & Tabs */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h3 className="text-base font-semibold text-slate-100 flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-blue-400" />
            24-Hour ML Forecast Analytics
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Interactive predictions computed hour-by-hour
          </p>
        </div>

        {/* Tab Buttons */}
        <div className="flex items-center gap-1.5 bg-slate-950 p-1 rounded-xl border border-slate-800">
          <button
            onClick={() => setActiveTab('rainfall')}
            className={`px-3 py-1.5 text-xs rounded-lg font-medium transition-all flex items-center gap-1.5 ${
              activeTab === 'rainfall'
                ? 'bg-blue-600 text-white shadow'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Droplet className="w-3.5 h-3.5" /> Rainfall (mm)
          </button>

          <button
            onClick={() => setActiveTab('temperature')}
            className={`px-3 py-1.5 text-xs rounded-lg font-medium transition-all flex items-center gap-1.5 ${
              activeTab === 'temperature'
                ? 'bg-amber-600 text-white shadow'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <TrendingUp className="w-3.5 h-3.5" /> Temp & Humidity
          </button>
        </div>
      </div>

      {/* Chart Display Container */}
      <div className="h-72 w-full pt-2">
        {activeTab === 'rainfall' ? (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={formattedData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="timeLabel" stroke="#64748b" fontSize={11} />
              <YAxis stroke="#64748b" fontSize={11} label={{ value: 'mm', angle: -90, position: 'insideLeft', fill: '#64748b' }} />
              <Tooltip
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px', fontSize: '12px' }}
                formatter={(val) => [`${val} mm`, 'Predicted Rain']}
              />
              <Bar dataKey="precipitation" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={formattedData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="timeLabel" stroke="#64748b" fontSize={11} />
              <YAxis yAxisId="left" stroke="#f59e0b" fontSize={11} label={{ value: '°C', angle: -90, position: 'insideLeft', fill: '#f59e0b' }} />
              <YAxis yAxisId="right" orientation="right" stroke="#3b82f6" fontSize={11} label={{ value: '%', angle: 90, position: 'insideRight', fill: '#3b82f6' }} />
              <Tooltip
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px', fontSize: '12px' }}
              />
              <Line yAxisId="left" type="monotone" dataKey="temperature" name="Temperature (°C)" stroke="#f59e0b" strokeWidth={2} dot={false} />
              <Line yAxisId="right" type="monotone" dataKey="humidity" name="Humidity (%)" stroke="#3b82f6" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>

    </div>
  );
}
