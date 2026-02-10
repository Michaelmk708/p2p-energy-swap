import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000/api';

interface EnergyReading {
  id: number;
  household_id: string;
  pv_power_kw: number;
  load_power_kw: number;
  net_power_kw: number;
  timestamp: number;
  created_at: string;
}

export const EnergyMeterPanel: React.FC = () => {
  const [latestReading, setLatestReading] = useState<EnergyReading | null>(null);
  const [readings, setReadings] = useState<EnergyReading[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const householdId = localStorage.getItem('household_id') || 'sim-1';

  // Fetch latest reading
  const fetchLatestReading = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get(`${BACKEND_URL}/energy-reading/latest/`, {
        params: { household_id: householdId }
      });
      if (response.data.status === 'success') {
        setLatestReading(response.data);
      }
    } catch (err: any) {
      console.error('Error fetching latest reading:', err);
      if (err.response?.status !== 404) {
        setError('Failed to fetch meter data');
      }
    } finally {
      setLoading(false);
    }
  };

  // Fetch reading history
  const fetchReadings = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/energy-reading/`, {
        params: {
          household_id: householdId,
          limit: 15
        }
      });
      if (response.data.status === 'success') {
        setReadings(response.data.readings);
      }
    } catch (err) {
      console.error('Error fetching readings:', err);
    }
  };

  useEffect(() => {
    fetchLatestReading();
    fetchReadings();

    if (autoRefresh) {
      const interval = setInterval(() => {
        fetchLatestReading();
        fetchReadings();
      }, 2000); // Refresh every 2 seconds

      return () => clearInterval(interval);
    }
  }, [householdId, autoRefresh]);

  if (!latestReading) {
    return (
      <div className="bg-gradient-to-br from-slate-50 to-slate-100 p-6 rounded-xl border border-slate-200 shadow-sm">
        <h2 className="text-2xl font-bold mb-4 text-slate-800">Live Energy Meter</h2>
        <div className="text-center py-12">
          {loading ? (
            <div className="flex flex-col items-center gap-3">
              <div className="w-8 h-8 border-4 border-slate-300 border-t-blue-500 rounded-full animate-spin"></div>
              <p className="text-slate-600">Loading sensor data...</p>
            </div>
          ) : (
            <p className="text-slate-500">No meter data available. Check Wokwi simulation.</p>
          )}
        </div>
      </div>
    );
  }

  // Determine if exporting or importing
  const isExporting = latestReading.net_power_kw > 0;
  const flowColor = isExporting ? 'text-green-600' : 'text-orange-600';

  return (
    <div className="bg-gradient-to-br from-slate-50 to-slate-100 p-6 rounded-xl border border-slate-200 shadow-lg">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold text-slate-800">Live Energy Meter</h2>
          <p className="text-sm text-slate-600">Household {householdId}</p>
        </div>
        <div className="flex items-center gap-3">
          <label className="flex items-center gap-2 cursor-pointer bg-white px-3 py-2 rounded-lg border border-slate-300">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="w-4 h-4 text-blue-600"
            />
            <span className="text-sm text-slate-700">Auto-refresh</span>
          </label>
          <button
            onClick={() => {
              fetchLatestReading();
              fetchReadings();
            }}
            disabled={loading}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium disabled:opacity-50 transition-colors"
          >
            Refresh
          </button>
        </div>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-lg text-sm">
          {error}
        </div>
      )}

      {/* Main Meter Display - Three Column Layout */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        {/* Solar PV Meter */}
        <div className="bg-white rounded-lg border-2 border-yellow-300 p-6 shadow-md hover:shadow-lg transition-shadow">
          <div className="text-center">
            <div className="mb-3">
              <svg className="w-12 h-12 mx-auto text-yellow-500" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm3.5-9c.83 0 1.5-.67 1.5-1.5S16.33 8 15.5 8 14 8.67 14 9.5s.67 1.5 1.5 1.5z" />
              </svg>
            </div>
            <p className="text-sm text-slate-600 font-medium mb-1">SOLAR PANELS</p>
            <p className="text-4xl font-bold text-yellow-600">{latestReading.pv_power_kw.toFixed(2)}</p>
            <p className="text-xs text-slate-500 mt-1">Kilowatts (kW)</p>
          </div>
        </div>

        {/* House Consumption Meter */}
        <div className="bg-white rounded-lg border-2 border-orange-300 p-6 shadow-md hover:shadow-lg transition-shadow">
          <div className="text-center">
            <div className="mb-3">
              <svg className="w-12 h-12 mx-auto text-orange-500" fill="currentColor" viewBox="0 0 24 24">
                <path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z" />
              </svg>
            </div>
            <p className="text-sm text-slate-600 font-medium mb-1">HOUSE CONSUMPTION</p>
            <p className="text-4xl font-bold text-orange-600">{latestReading.load_power_kw.toFixed(2)}</p>
            <p className="text-xs text-slate-500 mt-1">Kilowatts (kW)</p>
          </div>
        </div>

        {/* Net Power (Export/Import) */}
        <div className={`bg-white rounded-lg border-2 p-6 shadow-md hover:shadow-lg transition-shadow ${
          isExporting ? 'border-green-300' : 'border-red-300'
        }`}>
          <div className="text-center">
            <div className="mb-3">
              <svg className={`w-12 h-12 mx-auto ${isExporting ? 'text-green-500' : 'text-red-500'}`} fill="currentColor" viewBox="0 0 24 24">
                {isExporting ? (
                  <path d="M4 12a1 1 0 0 0 1 1h12.17l-3.59 3.59a1 1 0 0 0 1.42 1.42l5-5a1 1 0 0 0 0-1.42l-5-5a1 1 0 1 0-1.42 1.42L17.17 11H5a1 1 0 0 0-1 1z" />
                ) : (
                  <path d="M20 12a1 1 0 0 0-1-1H6.83l3.59-3.59a1 1 0 0 0-1.42-1.42l-5 5a1 1 0 0 0 0 1.42l5 5a1 1 0 1 0 1.42-1.42L6.83 13H19a1 1 0 0 0 1-1z" />
                )}
              </svg>
            </div>
            <p className="text-sm text-slate-600 font-medium mb-1">
              {isExporting ? 'EXPORTING' : 'IMPORTING'}
            </p>
            <p className={`text-4xl font-bold ${flowColor}`}>
              {Math.abs(latestReading.net_power_kw).toFixed(2)}
            </p>
            <p className="text-xs text-slate-500 mt-1">Kilowatts (kW)</p>
          </div>
        </div>
      </div>

      {/* Status and Timestamp */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <div className="flex justify-between items-center">
          <div>
            <p className="text-sm text-blue-700 font-medium">
              Status: <span className="font-bold">{isExporting ? '🟢 EXPORTING' : '🔴 IMPORTING'}</span>
            </p>
            <p className="text-xs text-blue-600 mt-1">
              Last Update: {new Date(latestReading.created_at).toLocaleString()}
            </p>
          </div>
          <div className="text-right">
            <p className="text-xs text-blue-600">Household ID</p>
            <p className="text-sm font-mono text-blue-900">{latestReading.household_id}</p>
          </div>
        </div>
      </div>

      {/* Energy Flow Diagram */}
      <div className="bg-white border border-slate-200 rounded-lg p-4 mb-6">
        <p className="text-sm font-semibold text-slate-700 mb-4">Energy Flow:</p>
        <div className="flex items-center justify-between">
          {/* Solar Generation */}
          <div className="text-center">
            <div className="w-16 h-16 bg-yellow-100 border-2 border-yellow-400 rounded-full flex items-center justify-center mb-2">
              <span className="text-2xl">☀️</span>
            </div>
            <p className="text-xs font-mono font-bold text-yellow-700">{latestReading.pv_power_kw.toFixed(2)} kW</p>
          </div>

          {/* Arrow and Net Power */}
          <div className="flex-1 flex flex-col items-center">
            <div className="text-2xl font-bold text-slate-600 mb-2">→</div>
            <div className={`px-3 py-1 rounded text-xs font-bold ${
              isExporting 
                ? 'bg-green-100 text-green-700' 
                : 'bg-orange-100 text-orange-700'
            }`}>
              {isExporting ? '↗ EXPORT' : '↙ IMPORT'}
            </div>
            <div className="text-lg font-bold mt-2">
              {Math.abs(latestReading.net_power_kw).toFixed(2)} kW
            </div>
          </div>

          {/* House Consumption */}
          <div className="text-center">
            <div className="w-16 h-16 bg-orange-100 border-2 border-orange-400 rounded-full flex items-center justify-center mb-2">
              <span className="text-2xl">🏠</span>
            </div>
            <p className="text-xs font-mono font-bold text-orange-700">{latestReading.load_power_kw.toFixed(2)} kW</p>
          </div>
        </div>
      </div>

      {/* Reading History Table */}
      {readings.length > 0 && (
        <div className="overflow-x-auto">
          <h3 className="text-lg font-semibold text-slate-800 mb-3">Recent Readings</h3>
          <table className="w-full text-sm border-collapse">
            <thead>
              <tr className="bg-slate-200 border-b-2 border-slate-400">
                <th className="text-left p-3 text-slate-700">Time</th>
                <th className="text-right p-3 text-slate-700">Solar (kW)</th>
                <th className="text-right p-3 text-slate-700">Load (kW)</th>
                <th className="text-right p-3 text-slate-700">Net (kW)</th>
                <th className="text-center p-3 text-slate-700">Status</th>
              </tr>
            </thead>
            <tbody>
              {readings.map((reading) => (
                <tr key={reading.id} className="border-b border-slate-200 hover:bg-slate-100 transition-colors">
                  <td className="p-3 text-slate-600">
                    {new Date(reading.created_at).toLocaleTimeString()}
                  </td>
                  <td className="text-right p-3 font-mono text-yellow-600 font-semibold">
                    {reading.pv_power_kw.toFixed(2)}
                  </td>
                  <td className="text-right p-3 font-mono text-orange-600 font-semibold">
                    {reading.load_power_kw.toFixed(2)}
                  </td>
                  <td className="text-right p-3 font-mono font-bold">
                    <span className={reading.net_power_kw > 0 ? 'text-green-600' : 'text-red-600'}>
                      {reading.net_power_kw.toFixed(2)}
                    </span>
                  </td>
                  <td className="text-center p-3">
                    <span className={`px-2 py-1 rounded text-xs font-bold ${
                      reading.net_power_kw > 0
                        ? 'bg-green-100 text-green-700'
                        : 'bg-orange-100 text-orange-700'
                    }`}>
                      {reading.net_power_kw > 0 ? 'Export' : 'Import'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default EnergyMeterPanel;
