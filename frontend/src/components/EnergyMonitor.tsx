import { useEffect, useState } from 'react';
import api from '@/lib/api';

interface EnergyData {
  pv_power: number;
  load_power: number;
  timestamp: number;
}

export function EnergyMonitor() {
  const [pvPower, setPvPower] = useState<number>(0);
  const [loadPower, setLoadPower] = useState<number>(0);
  const [netPower, setNetPower] = useState<number>(0);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // Poll for latest IoT data every 1 second
    const interval = setInterval(async () => {
      try {
        // Fetch PV data
        const pvRes = await api.get('/iotcentral/latest/?device=wokwi-sim-1&component=pv_array', { 
          validateStatus: () => true 
        }).catch(() => null);
        
        // Fetch Load data
        const loadRes = await api.get('/iotcentral/latest/?device=wokwi-sim-1&component=house_load', { 
          validateStatus: () => true 
        }).catch(() => null);
        
        let updated = false;
        
        if (pvRes?.status === 200 && pvRes.data?.data) {
          const power = pvRes.data.data.power || pvRes.data.data.pv_power || 0;
          setPvPower(Number(power) || 0);
          updated = true;
        }
        
        if (loadRes?.status === 200 && loadRes.data?.data) {
          const power = loadRes.data.data.power || loadRes.data.data.load_power || 0;
          setLoadPower(Number(power) || 0);
          updated = true;
        }
        
        if (updated) {
          setLastUpdate(new Date());
          setIsConnected(true);
        }
      } catch (error) {
        // Silently fail - IoT data may not be available yet
      }
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    setNetPower(pvPower - loadPower);
  }, [pvPower, loadPower]);

  const getStatusColor = (power: number) => {
    if (power > 5) return 'bg-green-500';
    if (power > 2) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className="p-6 bg-gradient-to-br from-slate-900 to-slate-800 rounded-lg shadow-lg">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-white">Live Energy Monitor</h2>
        <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
      </div>

      <div className="grid grid-cols-3 gap-4 mb-6">
        {/* PV Solar */}
        <div className="bg-slate-700 p-4 rounded-lg">
          <div className="text-sm text-slate-400 mb-2">Solar Panel (PV)</div>
          <div className="text-3xl font-bold text-yellow-400">{pvPower.toFixed(2)}</div>
          <div className="text-xs text-slate-500 mt-1">kW</div>
          <div className={`mt-3 h-2 rounded ${getStatusColor(pvPower)}`} />
        </div>

        {/* Load/Consumption */}
        <div className="bg-slate-700 p-4 rounded-lg">
          <div className="text-sm text-slate-400 mb-2">Load/Consumption</div>
          <div className="text-3xl font-bold text-blue-400">{loadPower.toFixed(2)}</div>
          <div className="text-xs text-slate-500 mt-1">kW</div>
          <div className={`mt-3 h-2 rounded ${getStatusColor(loadPower)}`} />
        </div>

        {/* Net Power */}
        <div className="bg-slate-700 p-4 rounded-lg">
          <div className="text-sm text-slate-400 mb-2">Net Power</div>
          <div className={`text-3xl font-bold ${netPower > 0 ? 'text-green-400' : 'text-red-400'}`}>
            {netPower > 0 ? '+' : ''}{netPower.toFixed(2)}
          </div>
          <div className="text-xs text-slate-500 mt-1">{netPower > 0 ? 'Surplus' : 'Deficit'}</div>
          <div className="mt-3 text-xs text-slate-400">
            {netPower > 0 ? '🟢 Ready to sell' : '🔴 Need to buy'}
          </div>
        </div>
      </div>

      {/* Status Info */}
      <div className="bg-slate-700 p-4 rounded-lg text-xs text-slate-400">
        <div>Last update: {lastUpdate?.toLocaleTimeString() || 'Waiting for data...'}</div>
        <div className="mt-2">
          {isConnected ? (
            <span className="text-green-400">✓ Connected to IoT device</span>
          ) : (
            <span className="text-yellow-400">⚠ Waiting for IoT data (open Wokwi simulation)</span>
          )}
        </div>
      </div>

      {/* Energy Status Indicator */}
      <div className="mt-6 bg-slate-700 p-4 rounded-lg">
        <div className="text-sm font-semibold text-slate-300 mb-3">Energy Status</div>
        <div className="flex items-center gap-2">
          <div className={`w-4 h-4 rounded-full ${netPower > 0 ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
          <span className="text-slate-300">
            {netPower > 0
              ? `You have ${netPower.toFixed(2)} kW surplus power available for trading`
              : `You need ${Math.abs(netPower).toFixed(2)} kW more power`}
          </span>
        </div>
      </div>
    </div>
  );
}
