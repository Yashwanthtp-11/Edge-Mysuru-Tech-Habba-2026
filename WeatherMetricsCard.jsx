import React from 'react';
import { Thermometer, Droplets, Gauge, Wind, Cloud } from 'lucide-react';

export default function WeatherMetricsCard({ weather }) {
  if (!weather) return null;

  const metrics = [
    {
      label: 'Temperature',
      value: `${weather.temperature.toFixed(1)} °C`,
      icon: <Thermometer className="w-5 h-5 text-amber-400" />,
      color: 'from-amber-500/10 to-transparent border-amber-500/20',
    },
    {
      label: 'Humidity',
      value: `${Math.round(weather.humidity)} %`,
      icon: <Droplets className="w-5 h-5 text-blue-400" />,
      color: 'from-blue-500/10 to-transparent border-blue-500/20',
    },
    {
      label: 'Pressure',
      value: `${Math.round(weather.pressure)} hPa`,
      icon: <Gauge className="w-5 h-5 text-indigo-400" />,
      color: 'from-indigo-500/10 to-transparent border-indigo-500/20',
    },
    {
      label: 'Wind Speed',
      value: `${weather.wind_speed.toFixed(1)} km/h`,
      icon: <Wind className="w-5 h-5 text-teal-400" />,
      color: 'from-teal-500/10 to-transparent border-teal-500/20',
    },
    {
      label: 'Cloud Cover',
      value: `${Math.round(weather.cloud_cover)} %`,
      icon: <Cloud className="w-5 h-5 text-sky-400" />,
      color: 'from-sky-500/10 to-transparent border-sky-500/20',
    },
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-4">
      {metrics.map((item, i) => (
        <div
          key={i}
          className={`bg-slate-900 border rounded-xl p-4 flex flex-col justify-between transition-all hover:border-slate-700 bg-gradient-to-b ${item.color}`}
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-slate-400 font-medium">{item.label}</span>
            {item.icon}
          </div>
          <div className="text-xl font-bold text-slate-100 font-mono">
            {item.value}
          </div>
        </div>
      ))}
    </div>
  );
}
