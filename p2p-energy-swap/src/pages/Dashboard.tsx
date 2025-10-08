// src/pages/Dashboard.tsx
import { useMemo, useEffect, useState, useCallback } from "react";
import useGeolocation from "@/hooks/useGeolocation";
import ToastContainer, { showToast } from '@/components/Toast';
import { Layout } from "@/components/Layout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Zap,
  Battery,
  Sun,
  Wind,
  ArrowUpRight,
  ArrowDownRight,
  Sparkles,
} from "lucide-react";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis, CartesianGrid } from "recharts";
import { useNavigate } from "react-router-dom";
import { useUser } from "@/contexts/UserContext";
import api from "@/lib/api";
// (useState is imported above together with useEffect/useMemo)

// Generate realistic household consumption patterns
function getRealisticConsumption(timeStr: string): number {
  const [hours, minutes] = timeStr.split(':').map(Number);
  const hour = hours + (minutes / 60);
  
  // Base consumption patterns (kW)
  if (hour >= 7 && hour < 9) {
    // Morning peak: cooking, heating, getting ready
    return 1.8 + Math.random() * 0.4; // 1.8-2.2 kW
  } else if (hour >= 9 && hour < 17) {
    // Daytime: low usage (people at work)
    return 0.8 + Math.random() * 0.3; // 0.8-1.1 kW
  } else if (hour >= 17 && hour < 22) {
    // Evening peak: cooking, lights, TV, appliances
    return 2.2 + Math.random() * 0.6; // 2.2-2.8 kW
  } else {
    // Night: minimal usage (sleep mode)
    return 0.4 + Math.random() * 0.2; // 0.4-0.6 kW
  }
}

// Shared predicted surplus hook to ensure both components show the same values
function usePredictedSurplus(energyData: Array<{ time: string; usage: number; production: number; net: number; }>) {
  const [predictedSurplus, setPredictedSurplus] = useState<number>(0);
  
  // Use REAL-TIME data for accurate surplus/deficit calculation
  const calculatePredictedSurplus = useCallback(() => {
    if (!energyData || energyData.length === 0) {
      return 0;
    }

    // Use the LATEST (most recent) data point for real-time calculation
    const latestData = energyData[energyData.length - 1];
    if (latestData) {
      // Direct current surplus/deficit calculation: PV - Load
      const currentSurplus = latestData.production - latestData.usage;
      
      // For daily energy export prediction, scale current power to daily kWh
      // Assume current conditions continue for remainder of day
      const now = new Date();
      const hoursRemaining = 24 - now.getHours() - now.getMinutes() / 60;
      const dailyProjection = currentSurplus * Math.max(hoursRemaining, 1);
      
      // Return current surplus (for immediate display) with some daily context
      // Positive = surplus (can export), Negative = deficit (need to import)
      return currentSurplus; // Real-time surplus in kW
    }

    // Fallback to average if no current data
    const productions = energyData.map(d => d.production).filter(p => p > 0);
    const consumptions = energyData.map(d => d.usage);
    const avgProduction = productions.length > 0 ? productions.reduce((a, b) => a + b, 0) / productions.length : 0;
    const avgConsumption = consumptions.reduce((a, b) => a + b, 0) / consumptions.length;
    
    return avgProduction - avgConsumption;
  }, [energyData]);

  useEffect(() => {
    const surplus = calculatePredictedSurplus();
    setPredictedSurplus(surplus);
  }, [calculatePredictedSurplus]);

  return predictedSurplus;
}

// Live energy data from Wokwi: PV array + house load (both real potentiometers)
function useEnergyFlow(deviceId?: string) {
  const [data, setData] = useState<{ time: string; usage: number; production: number; net: number; }[]>([]);
  useEffect(() => {
    let mounted = true;
    let t: any;
    const fetchTS = async () => {
      try {
        // Fetch BOTH PV and load data from Wokwi
        const params: Record<string, any> = { device: deviceId || 'sim-1', components: 'pv_array,house_load', minutes: 60 };
        const r = await api.get('/iotcentral/timeseries/', { params });
        const pv = (r.data?.series?.pv_array || []) as Array<{t:number; kw:number}>;
        const load = (r.data?.series?.house_load || []) as Array<{t:number; kw:number}>;
        
        // Merge PV and Load data by timestamps
        const byMinute = new Map<string, {p?: number; l?: number}>();
        const toKey = (ms:number) => new Date(ms).toLocaleTimeString(undefined, { hour:'2-digit', minute:'2-digit' });
        
        // Process PV data
        for (const p of pv) {
          const k = toKey(p.t);
          const obj = byMinute.get(k) || {};
          obj.p = p.kw;
          byMinute.set(k, obj);
        }
        
        // Process Load data
        for (const l of load) {
          const k = toKey(l.t);
          const obj = byMinute.get(k) || {};
          obj.l = l.kw;
          byMinute.set(k, obj);
        }
        
        const arr = Array.from(byMinute.entries()).sort((a,b) => a[0].localeCompare(b[0])).map(([k,v]) => {
          const production = Number(v.p||0);
          const usage = Number(v.l||0); // Use REAL load data instead of simulated
          const net = production - usage; // Real net energy calculation
          return { time: k, usage: Number(usage.toFixed(2)), production, net: Number(net.toFixed(2)) };
        });
        if (mounted) setData(arr);
      } catch {}
    };
    fetchTS();
    t = setInterval(fetchTS, 5000);
    return () => { mounted = false; if (t) clearInterval(t); };
  }, [deviceId]);
  return data;
}

export default function Dashboard() {
  const navigate = useNavigate();
  const { user, loading } = useUser();
  const geo = useGeolocation();
    // Configure IoT Central target via backend user mapping (devices_mine); fallback to Vite env
    const defaultDevice = (import.meta as any)?.env?.VITE_IOTC_DEVICE_ID || 'sim-1';
    const envComponent = (import.meta as any)?.env?.VITE_IOTC_COMPONENT || undefined;
    const [selectedDevice, setSelectedDevice] = useState<string>(defaultDevice);
    const [pvComponent, setPvComponent] = useState<string | undefined>(envComponent || 'pv_array');
    const [exportComponent, setExportComponent] = useState<string | undefined>('grid_export');

  const displayName = useMemo(() => {
    if (!user) return "";
    // Prefer backend-provided full name (`user.name`) if present, otherwise fallback
    return (
      user.name?.trim() || user.first_name?.trim() || user.username?.trim() || (user.email?.split("@")[0] ?? "")
    );
  }, [user]);

  // Energy Exported (today) state pulls from backend accumulator
  const [exportedToday, setExportedToday] = useState<number | null>(null);
  const [tokenBalance, setTokenBalance] = useState<number>(0);
  // Fetch initial token balance
  useEffect(() => {
    let mounted = true;
    api.get('/account/balance/').then((r) => {
      if (!mounted) return;
      const v = Number(r.data?.token_balance ?? 0);
      if (!Number.isNaN(v)) setTokenBalance(v);
    }).catch(() => {
      // keep 0 if backend not available
    });
    return () => { mounted = false; };
  }, []);
  // Listen for token balance updates dispatched from export flow
  useEffect(() => {
    const onTB = (e: any) => {
      const v = Number(e?.detail?.value);
      if (!Number.isNaN(v)) setTokenBalance(v);
    };
    window.addEventListener('tokenBalanceUpdate', onTB as any);
    return () => { window.removeEventListener('tokenBalanceUpdate', onTB as any); };
  }, []);
  useEffect(() => {
    let mounted = true;
    let t: any;
    const onUpdate = (e: any) => {
      if (!mounted) return;
      const v = e?.detail?.value;
      const d = e?.detail?.delta;
      if (typeof v === 'number') setExportedToday(v);
      else if (typeof d === 'number') setExportedToday((prev) => (prev == null ? d : prev + d));
    };
    window.addEventListener('exportedTodayUpdate', onUpdate as any);
    const fetchExported = async () => {
      try {
        const params: Record<string, any> = { device: selectedDevice };
        if (exportComponent) params.component = exportComponent;
        const r = await api.get('/iotcentral/daily_exported/', { params });
        const v = r.data?.energy_kwh;
        if (mounted && typeof v === 'number') setExportedToday(v);
      } catch {}
    };
    fetchExported();
    t = setInterval(fetchExported, 30000); // refresh every 30s
    return () => { mounted = false; if (t) clearInterval(t); window.removeEventListener('exportedTodayUpdate', onUpdate as any); };
  }, [selectedDevice, exportComponent]);

  // Load device mapping dynamically for the logged-in user
  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const r = await api.get('/devices/mine/');
        const dev = r?.data?.devices?.[0];
        if (mounted && dev) {
          if (dev.device_id) setSelectedDevice(dev.device_id);
          if (dev.pv_component) setPvComponent(dev.pv_component);
          if (dev.export_component) setExportComponent(dev.export_component);
        }
        // If no mapping from backend, try last_seen for device only.
        // Do NOT override pvComponent here: the bridge's last_seen component
        // flips based on the most recent post (often house_load). We want the
        // Live Meter to stay on PV by default unless explicitly configured.
        if (mounted && (!dev || !dev.device_id)) {
          try {
            const ls = await api.get('/iotcentral/last_seen/');
            const d = (ls.data?.device || '').trim();
            if (d) setSelectedDevice(d);
          } catch {}
        }
      } catch {}
    })();
    return () => { mounted = false; };
  }, [user?.id]);

  const energyUsageData = useEnergyFlow(selectedDevice);
  const sharedPredictedSurplus = usePredictedSurplus(energyUsageData);
  return (
    <Layout>
      <div className="space-y-6 animate-fade-in pb-20 md:pb-6">
        <div>
          <h1 className="text-3xl font-bold text-foreground">
            {loading ? "Loading…" : displayName ? `Welcome back, ${displayName}! 👋` : "Dashboard"}
          </h1>
          <p className="text-muted-foreground">Monitor your energy usage and trading activity</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Send Energy to Grid</CardTitle>
            <CardDescription>Export surplus energy and mint equivalent tokens (1 kWh → 1 token)</CardDescription>
          </CardHeader>
          <CardContent>
            <ProductionIntegration selectedDevice={selectedDevice} energyData={energyUsageData} sharedPredictedSurplus={sharedPredictedSurplus} />
          </CardContent>
        </Card>

  <ToastContainer />        {/* Dedicated Live Meter card (separate from Energy Exported) */}
        <Card className="hover:shadow-lg transition-smooth">
          <CardHeader className="pb-2">
            <CardTitle>Live Meter</CardTitle>
            <CardDescription>Real-time power reading from your device</CardDescription>
          </CardHeader>
          <CardContent>
            <LiveMeter
              deviceId={selectedDevice}
              component={pvComponent}
              label="Current Power"
              unit="kW"
              formatter={(v) => `${(v || 0).toFixed(2)} kW`}
            />
            <div className="mt-3 flex items-center gap-2 text-xs">
              <span className="text-muted-foreground">Source: Solar PV</span>
            </div>
            <div className="text-xs text-muted-foreground mt-2">
              Device: <span className="font-mono">{selectedDevice}</span>
            </div>
            {/* No demo toggles on website; device/components come from backend mapping */}
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card className="hover:shadow-lg transition-smooth">
            <CardHeader className="pb-2">
              <CardDescription className="flex items-center gap-2">
                <Zap className="h-4 w-4 text-primary" />
                Token Balance
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-foreground" id="token-balance">{tokenBalance.toFixed(3)}</div>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-smooth">
            <CardHeader className="pb-2">
              <CardDescription className="flex items-center gap-2">
                <ArrowUpRight className="h-4 w-4 text-accent" />
                Energy Exported
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-foreground">{exportedToday != null ? `${exportedToday.toFixed(3)} kWh` : '0.000 kWh'}</div>
              <div className="text-xs text-muted-foreground">Total energy exported (today)</div>
              <div className="flex items-center gap-1 text-sm text-accent mt-1">
                <Sun className="h-3 w-3" />
                <span>Solar surplus</span>
              </div>
              <div className="text-xs text-muted-foreground mt-2">
                Using: Device <span className="font-mono">{selectedDevice}</span>
                {exportComponent ? (<><span> · </span>component <span className="font-mono">{exportComponent}</span></>) : null}
              </div>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-smooth">
            <CardHeader className="pb-2">
              <CardDescription className="flex items-center gap-2">
                <ArrowDownRight className="h-4 w-4 text-red-500" />
                House Consumption
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-foreground">
                {energyUsageData.length > 0 ? `${energyUsageData[energyUsageData.length - 1]?.usage?.toFixed(2) || '0.00'} kW` : '0.00 kW'}
              </div>
              <div className="text-xs text-muted-foreground">Live from Load potentiometer</div>
              <div className="flex items-center gap-1 text-sm text-red-500 mt-1">
                <Zap className="h-3 w-3" />
                <span>Real-time Wokwi data</span>
              </div>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-smooth">
            <CardHeader className="pb-2">
              <CardDescription className="flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-blue-500" />
                Net Energy
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-foreground">
                {(() => {
                  const latest = energyUsageData.length > 0 ? energyUsageData[energyUsageData.length - 1] : null;
                  const net = latest?.net || 0;
                  return `${net >= 0 ? '+' : ''}${net.toFixed(2)} kW`;
                })()}
              </div>
              <div className="text-xs text-muted-foreground">Production - Consumption</div>
              <div className="flex items-center gap-1 text-sm mt-1">
                {(() => {
                  const latest = energyUsageData.length > 0 ? energyUsageData[energyUsageData.length - 1] : null;
                  const net = latest?.net || 0;
                  if (net > 0) {
                    return (
                      <>
                        <ArrowUpRight className="h-3 w-3 text-green-500" />
                        <span className="text-green-500">Surplus - Selling energy</span>
                      </>
                    );
                  } else {
                    return (
                      <>
                        <ArrowDownRight className="h-3 w-3 text-orange-500" />
                        <span className="text-orange-500">Deficit - Buying energy</span>
                      </>
                    );
                  }
                })()}
              </div>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Battery className="h-5 w-5 text-primary" />
              Energy Flow (24h)
            </CardTitle>
            <CardDescription>Live solar production vs. realistic household consumption patterns</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={energyUsageData}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis dataKey="time" stroke="hsl(var(--muted-foreground))" fontSize={12} />
                <YAxis
                  stroke="hsl(var(--muted-foreground))"
                  fontSize={12}
                  label={{ value: "kW", angle: -90, position: "insideLeft" }}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "hsl(var(--card))",
                    border: "1px solid hsl(var(--border))",
                    borderRadius: "8px",
                  }}
                  formatter={(value: number, name: string) => [
                    `${value.toFixed(2)} kW`,
                    name === 'production' ? '🌞 Solar Production' : 
                    name === 'usage' ? '🏠 House Consumption' : 
                    name === 'net' ? (value >= 0 ? '⚡ Surplus (Sellable)' : '🔋 Deficit (Need to Buy)') : name
                  ]}
                />
                <Line type="monotone" dataKey="production" stroke="hsl(142 76% 36%)" strokeWidth={3} name="Solar Production" dot={{ fill: "hsl(142 76% 36%)", r: 4 }} />
                <Line type="monotone" dataKey="usage" stroke="hsl(345 82% 55%)" strokeWidth={3} name="House Consumption" dot={{ fill: "hsl(345 82% 55%)", r: 4 }} />
                <Line type="monotone" dataKey="net" stroke="hsl(221 83% 53%)" strokeWidth={2} strokeDasharray="5 5" name="Net Energy" dot={{ fill: "hsl(221 83% 53%)", r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <AIPredictionCard energyData={energyUsageData} />
          <QuickActions />
        </div>
      </div>
    </Layout>
  );
}

function ResultSummary({ result }: { result: any }) {
  const [showDetails, setShowDetails] = useState(false);
  const tradeId = result.execute?.trade?.id ?? result.execute?.trade_id ?? '—';
  const status = result.execute?.status ?? result.execute?.trade?.status ?? 'unknown';
  const tokens = result.mint?.tokens_minted ?? result.mint?.amount_kwh ?? '—';
  const tx = result.mint?.tx_hash ?? result.mint?.tx ?? 'pending';
  const userMsg = result.mint?.user_message || result.execute?.user_message || result.user_message || null;

  return (
    <div className="space-y-2 text-sm bg-muted p-3 rounded">
      <div className="flex items-center justify-between">
        <div>
          <div className="font-medium">Trade Result</div>
          <div>Trade ID: <span className="font-mono text-xs">{tradeId}</span></div>
          <div>Status: <strong>{status}</strong></div>
        </div>
        <div className="text-right">
          <div className="font-medium">Mint Result</div>
          <div>Tokens minted: <strong>{tokens}</strong></div>
          <div>Transaction: <span className="font-mono text-xs">{tx}</span></div>
        </div>
      </div>

      {userMsg && <div className="text-sm text-muted-foreground">{userMsg}</div>}

      <div className="flex items-center gap-2">
        <button className="text-sm text-primary underline" onClick={() => setShowDetails((s) => !s)}>
          {showDetails ? 'Hide details' : 'Show details'}
        </button>
      </div>

      {showDetails && (
        <pre className="whitespace-pre-wrap text-xs bg-white p-3 rounded border mt-2">{JSON.stringify(result, null, 2)}</pre>
      )}
    </div>
  );
}

function QuickActions() {
  const navigate = useNavigate();
  return (
    <Card>
      <CardHeader>
        <CardTitle>Quick Actions</CardTitle>
        <CardDescription>Manage your energy trading</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        <Button variant="energy" className="w-full justify-start" size="lg" onClick={() => navigate("/marketplace?tab=my-listings") }>
          <Zap className="mr-2 h-5 w-5" />
          List Tokens for Sale
        </Button>
        <Button variant="eco" className="w-full justify-start" size="lg" onClick={() => navigate("/marketplace?tab=buy")}>
          <Sun className="mr-2 h-5 w-5" />
          Buy Energy Tokens
        </Button>
        <Button variant="outline" className="w-full justify-start" size="lg" onClick={() => navigate("/marketplace")}>
          <Wind className="mr-2 h-5 w-5" />
          View Market Trends
        </Button>
      </CardContent>
    </Card>
  );
}

function AIPredictionCard({ energyData }: { energyData: Array<{ time: string; usage: number; production: number; net: number; }> }) {
  const geo = useGeolocation();
  const [data, setData] = useState<any>(null);
  const [city, setCity] = useState<string | null>(null);
  const [nextDate, setNextDate] = useState<string>("");
  const [sysKw, setSysKw] = useState<number>(() => {
    const v = Number(localStorage.getItem('energy_sys_kw') || '3');
    return Number.isFinite(v) && v > 0 ? v : 3;
  });
  const [baseKwh, setBaseKwh] = useState<number>(() => {
    const v = Number(localStorage.getItem('energy_base_kwh') || '6');
    return Number.isFinite(v) && v >= 0 ? v : 6;
  });
  const [editing, setEditing] = useState(false);

  // compute tomorrow label in local time
  useEffect(() => {
    const d = new Date();
    d.setDate(d.getDate() + 1);
    setNextDate(d.toLocaleDateString(undefined, { weekday: 'long', month: 'short', day: 'numeric' }));
  }, []);

  // Analyze live data patterns with emphasis on CURRENT real-time values
  const analyzeLiveData = () => {
    if (!energyData || energyData.length === 0) {
      return { avgProduction: 0, avgConsumption: 0, peakProduction: 0, totalSurplus: 0, efficiency: 0 };
    }

    // Get CURRENT values (most recent data point) for real-time accuracy
    const latestData = energyData[energyData.length - 1];
    const currentProduction = latestData?.production || 0;
    const currentConsumption = latestData?.usage || 0;
    const currentNet = latestData?.net || (currentProduction - currentConsumption);

    // Also calculate historical averages for context
    const productions = energyData.map(d => d.production).filter(p => p > 0);
    const consumptions = energyData.map(d => d.usage);
    const surpluses = energyData.map(d => d.net);

    // Prioritize current values with historical context
    const avgProduction = productions.length > 0 ? productions.reduce((a, b) => a + b, 0) / productions.length : 0;
    const avgConsumption = consumptions.reduce((a, b) => a + b, 0) / consumptions.length;
    const peakProduction = Math.max(...productions, currentProduction);
    const totalSurplus = surpluses.reduce((a, b) => a + b, 0);
    
    // Weight current values more heavily for real-time responsiveness
    const liveAvgProduction = currentProduction > 0 ? (0.7 * currentProduction + 0.3 * avgProduction) : avgProduction;
    const liveAvgConsumption = 0.7 * currentConsumption + 0.3 * avgConsumption;
    
    // For total surplus, prioritize current real-time status especially when in deficit
    let liveTotalSurplus;
    if (currentNet < 0) {
      // Currently in deficit - weight heavily toward current deficit status
      liveTotalSurplus = 0.9 * currentNet + 0.1 * (totalSurplus / Math.max(1, energyData.length));
    } else {
      // Currently in surplus - use balanced weighting
      liveTotalSurplus = 0.7 * currentNet + 0.3 * (totalSurplus / Math.max(1, energyData.length));
    }
    
    return { 
      avgProduction: liveAvgProduction, 
      avgConsumption: liveAvgConsumption, 
      peakProduction, 
      totalSurplus: liveTotalSurplus, 
      efficiency: 0.8 
    };
  };

  const liveStats = analyzeLiveData();

  const fetchPred = async () => {
    const params: Record<string, any> = {};
    if (geo.coords) { params.lat = geo.coords.lat; params.lon = geo.coords.lon; }
    // pass hints the AI can optionally use
    params.system_kw = sysKw;
    params.baseline_kwh = baseKwh;
    
    // Add live data analysis for more accurate predictions
    params.live_avg_production = liveStats.avgProduction;
    params.live_avg_consumption = liveStats.avgConsumption;
    params.live_peak_production = liveStats.peakProduction;
    params.live_total_surplus = liveStats.totalSurplus;
    params.live_efficiency = liveStats.efficiency;
    params.historical_data_points = energyData.length;
    try {
      const raw = localStorage.getItem('geo');
      if (raw) {
        const obj = JSON.parse(raw);
        if (obj?.city) params.city = obj.city;
      }
    } catch {}
    try {
      const r = await api.get('/predict/', { params });
      setData(r.data);
      const c = r.data?.weather?.location?.city || r.data?.weather?.city || params.city || null;
      if (c) {
        setCity(c);
        try {
          const raw = localStorage.getItem('geo');
          const prev = raw ? JSON.parse(raw) : {};
          localStorage.setItem('geo', JSON.stringify({ ...prev, city: c }));
        } catch {}
      }
    } catch {}
  };

  useEffect(() => { fetchPred(); }, [geo.coords?.lat, geo.coords?.lon]);
  useEffect(() => {
    const t = setInterval(fetchPred, 60000);
    return () => clearInterval(t);
  }, [geo.coords?.lat, geo.coords?.lon]);

  const pred = data?.prediction || data || {};
  const productionAI = pred?.expected_production_kwh ?? pred?.production_kwh ?? pred?.production ?? null;
  const consumptionAI = pred?.expected_consumption_kwh ?? pred?.consumption_kwh ?? pred?.consumption ?? null;
  const surplusAI = pred?.estimated_surplus_kwh ?? pred?.predicted_surplus_kwh ?? pred?.predicted_surplus ?? pred?.surplus_kwh ?? null;
  const conf = pred?.confidence ?? data?.confidence ?? null;
  const weather = data?.weather?.summary || data?.weather?.condition || null;
  const aiReason = pred?.reason ?? data?.reason ?? null;
  const aiRecommendation = pred?.recommendation ?? pred?.market_suggestion ?? data?.recommendation ?? data?.market_suggestion ?? null;

  // Fallback derivations if AI doesn’t provide production/consumption
  const wobj: any = data?.weather || {};
  const sunrise = wobj?.sunrise || wobj?.astronomy?.sunrise;
  const sunset = wobj?.sunset || wobj?.astronomy?.sunset;
  const cloud = ((): number | null => {
    const c = wobj?.cloud_cover ?? wobj?.clouds ?? null;
    if (c == null) return null;
    const n = Number(c);
    if (!Number.isFinite(n)) return null;
    if (n > 1) return Math.min(1, Math.max(0, n / 100));
    return Math.min(1, Math.max(0, n));
  })();
  const tempC = ((): number | null => {
    const t = wobj?.temp_c ?? wobj?.temperature_c ?? wobj?.temp ?? null;
    const n = Number(t);
    return Number.isFinite(n) ? n : null;
  })();
  const daylightHours = ((): number => {
    try {
      if (sunrise && sunset) {
        const sr = new Date(sunrise).getTime();
        const ss = new Date(sunset).getTime();
        if (Number.isFinite(sr) && Number.isFinite(ss) && ss > sr) {
          const hrs = (ss - sr) / 3600000;
          // Assume at least some usable daylight tomorrow
          return Math.max(4.0, hrs);
        }
      }
    } catch {}
    return 5.0; // reasonable default effective sun hours
  })();
  const eff = 0.8;
  // Even with heavy clouds, assume at least 15% irradiance makes it through
  const cloudFactor = Math.max(0.15, (cloud != null ? (1 - cloud) : 0.8));
  const derivedProductionRaw = sysKw * daylightHours * eff * cloudFactor;
  // Minimum daily production floor to avoid zero, scaled by system size
  const minProdFloor = Math.max(0.5, 0.25 * sysKw);
  const derivedProduction = Math.max(minProdFloor, derivedProductionRaw);
  const tempAdj = tempC != null ? Math.min(1.3, Math.max(0.7, 1 + 0.02 * (tempC - 22))) : 1.0;
  const derivedConsumption = Math.max(0, baseKwh * tempAdj);
  // Use live data to enhance predictions
  let production = productionAI != null ? Number(productionAI) : derivedProduction;
  
  // If we have live data, blend it with weather-based predictions for better accuracy
  if (liveStats.avgProduction > 0) {
    const liveBasedProduction = liveStats.peakProduction * daylightHours * cloudFactor * liveStats.efficiency;
    // Weighted average: 70% live data trend, 30% weather prediction
    production = productionAI != null ? Number(productionAI) : (0.7 * liveBasedProduction + 0.3 * derivedProduction);
  }
  
  if (!Number.isFinite(production) || production <= 0) {
    production = derivedProduction;
  }

  // Enhanced consumption prediction using live patterns
  let consumption = consumptionAI != null ? Number(consumptionAI) : derivedConsumption;
  if (liveStats.avgConsumption > 0) {
    // Use actual consumption patterns with temperature adjustment
    consumption = consumptionAI != null ? Number(consumptionAI) : (liveStats.avgConsumption * 24 * tempAdj);
  }
  
  // Apply 5kW system constraints for logical predictions
  const maxDailyProduction = 5.0 * daylightHours * 0.9; // 5kW system with 90% efficiency cap
  const maxDailyConsumption = 5.0 * 24; // Maximum theoretical daily consumption at 5kW continuous
  
  production = Math.min(production, maxDailyProduction);
  consumption = Math.min(consumption, maxDailyConsumption);

  // Real-time surplus calculation using CURRENT deficit/surplus status
  const baseSurplus = production - consumption;
  let surplus = surplusAI != null ? Number(surplusAI) : baseSurplus;
  
  // Use CURRENT real-time data to predict tomorrow realistically
  if (energyData.length > 0) {
    const latestData = energyData[energyData.length - 1];
    const currentRealSurplus = latestData ? (latestData.production - latestData.usage) : 0;
    
    // Realistic daily projection accounting for solar cycles
    if (currentRealSurplus < 0) {
      // Currently in deficit - create a sensible daily energy balance
      const currentDeficitKw = Math.abs(currentRealSurplus);
      
      // More realistic approach: consider that current conditions might be nighttime/low solar
      // Don't project current deficit for the whole day - that's unrealistic
      
      // Estimate a realistic daily deficit based on system constraints
      const typicalDailyConsumption = Math.min(consumption, 40); // Realistic household: max 40kWh/day
      const expectedDailyProduction = Math.min(production, 30); // Realistic solar: max 30kWh/day
      
      // Simple but realistic daily balance
      const estimatedDailyDeficit = Math.max(expectedDailyProduction - typicalDailyConsumption, -20); // Cap at -20kWh
      
      // If current deficit is very high, it might be temporary (nighttime, clouds, etc.)
      // Use a conservative multiplier
      const conservativeDeficit = Math.max(-12, estimatedDailyDeficit * 0.7); // Cap at -12kWh max
      
      surplus = surplusAI != null ? 
        (0.5 * Number(surplusAI) + 0.5 * conservativeDeficit) : 
        conservativeDeficit;
    } else {
      // Current surplus case - use balanced weighting
      const avgHourlySurplus = liveStats.totalSurplus !== 0 ? liveStats.totalSurplus : currentRealSurplus;
      const projectedDailySurplus = avgHourlySurplus * daylightHours * cloudFactor; // Only project during solar hours
      surplus = surplusAI != null ? 
        (0.3 * Number(surplusAI) + 0.7 * projectedDailySurplus) : 
        (0.3 * baseSurplus + 0.7 * projectedDailySurplus);
    }
  }
  
  // Apply realistic system limits (but allow negative values for deficit scenarios)
  if (surplus > 0) {
    const maxPossibleSurplus = maxDailyProduction * 0.9;
    surplus = Math.min(surplus, maxPossibleSurplus);
  }

  return (
    <Card className="border-primary/20 bg-gradient-to-br from-primary/5 to-transparent">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-primary" />
          AI Prediction: {nextDate}{city ? ` · ${city}` : ''}
        </CardTitle>
        <CardDescription>
          Smart forecast using live PV data & consumption patterns
          {energyData.length > 0 && (
            <span className="text-primary"> • {energyData.length} data points</span>
          )}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <button className="underline" onClick={() => setEditing((s) => !s)}>{editing ? 'Hide' : 'Energy settings'}</button>
          {editing && (
            <div className="flex items-center gap-2">
              <label className="flex items-center gap-1">System kW <input className="w-16 p-1 border rounded" type="number" min={0} step={0.1} value={sysKw} onChange={(e)=>setSysKw(Number(e.target.value))} /></label>
              <label className="flex items-center gap-1">Baseline kWh <input className="w-20 p-1 border rounded" type="number" min={0} step={0.1} value={baseKwh} onChange={(e)=>setBaseKwh(Number(e.target.value))} /></label>
              <Button size="sm" variant="outline" onClick={()=>{ try{ localStorage.setItem('energy_sys_kw', String(Math.max(0, sysKw))); localStorage.setItem('energy_base_kwh', String(Math.max(0, baseKwh))); }catch{}; }}>
                Save
              </Button>
            </div>
          )}
        </div>
        <div>
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm text-muted-foreground">Expected Production</span>
            {conf != null && <Badge variant="secondary">{Math.round(Number(conf))}%</Badge>}
          </div>
          <div className="text-2xl font-bold text-foreground">{production != null ? `${Number(production).toFixed(0)} kWh` : '—'}</div>
          {weather && (
            <p className="text-sm text-muted-foreground flex items-center gap-1 mt-1">
              <Sun className="h-3 w-3" />
              {String(weather)}
            </p>
          )}
        </div>
        <div>
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm text-muted-foreground">Expected Consumption</span>
          </div>
          <div className="text-2xl font-bold text-foreground">{consumption != null ? `${Number(consumption).toFixed(0)} kWh` : '—'}</div>
        </div>
        
        {energyData.length > 0 && (
          <div className="pt-3 border-t border-border/50">
            <div className="text-xs font-medium text-muted-foreground mb-2">📊 Live Data Analysis</div>
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div>
                <div className="text-muted-foreground">Current Peak</div>
                <div className="font-semibold">{liveStats.peakProduction.toFixed(1)} kW</div>
              </div>
              <div>
                <div className="text-muted-foreground">Avg Usage</div>
                <div className="font-semibold">{liveStats.avgConsumption.toFixed(1)} kW</div>
              </div>
              <div>
                <div className="text-muted-foreground">PV Efficiency</div>
                <div className="font-semibold">{(liveStats.efficiency * 100).toFixed(0)}%</div>
              </div>
              <div>
                <div className="text-muted-foreground">Net Status</div>
                <div className={`font-semibold ${liveStats.totalSurplus > 0 ? 'text-green-600' : 'text-orange-600'}`}>
                  {liveStats.totalSurplus > 0 ? 'Surplus' : 'Deficit'}
                </div>
              </div>
            </div>
          </div>
        )}

        {aiReason && (
          <div className="pt-3 border-t border-border/50">
            <div className="text-xs font-medium text-muted-foreground mb-2">🧠 AI Analysis</div>
            <p className="text-sm text-foreground leading-relaxed mb-2">{aiReason}</p>
            {aiRecommendation && (
              <div className="flex items-center gap-2">
                <span className="text-xs font-medium text-muted-foreground">Recommendation:</span>
                <Badge variant={aiRecommendation === 'buy' ? 'destructive' : aiRecommendation === 'sell' ? 'default' : 'secondary'}>
                  {aiRecommendation.toUpperCase()}
                </Badge>
              </div>
            )}
          </div>
        )}

        <div className="pt-4 border-t border-border">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-foreground">
              {surplus != null && surplus < 0 ? 'Predicted Deficit' : 'Predicted Surplus'}
            </span>
            <span className={`text-xl font-bold ${surplus != null && surplus < 0 ? 'text-red-600' : 'text-primary'}`}>
              {surplus != null ? `${surplus < 0 ? '' : '+'}${Number(surplus).toFixed(0)} kWh` : '—'}
            </span>
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            {energyData.length > 0 ? 
              `Enhanced with ${energyData.length}h of live data • Auto-refreshes 60s` : 
              'Auto-refreshes every 60s'
            }
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

function ProductionIntegration({ selectedDevice, energyData, sharedPredictedSurplus }: { selectedDevice: string; energyData: Array<{ time: string; usage: number; production: number; net: number; }>; sharedPredictedSurplus: number | null }) {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [predictData, setPredictData] = useState<any>(null);
  const [amount, setAmount] = useState<number>(1);
  const geo = useGeolocation();
  // Use the shared predicted surplus instead of calculating our own
  const predictedSurplus = sharedPredictedSurplus;
  // Testing helper: add ?testSurplus=1 to URL to force predicted surplus positive
  const TEST_FORCE_POS = (() => {
    try {
      const usp = new URLSearchParams(window.location.search);
      return usp.has('testSurplus') || usp.has('forcePositive');
    } catch {
      return false;
    }
  })();

  // ProductionIntegration now uses shared predicted surplus from Dashboard
  
  // Update amount when predictedSurplus changes
  useEffect(() => {
    if (predictedSurplus != null && predictedSurplus > 0) {
      setAmount(Number(predictedSurplus.toFixed(2)));
    }
  }, [predictedSurplus]);

  useEffect(() => {
    let mounted = true;
    // helper to compute enhanced predicted surplus using live data
    const computeFallbackSurplus = (): number => {
      // If we don't have energy data yet, return 0 to indicate we're still loading
      if (energyData.length === 0) {
        return 0;
      }
      // read persisted settings
      let sysKw = 3;
      let baseKwh = 6;
      try {
        const v1 = Number(localStorage.getItem('energy_sys_kw'));
        if (Number.isFinite(v1) && v1 > 0) sysKw = v1;
      } catch {}
      try {
        const v2 = Number(localStorage.getItem('energy_base_kwh'));
        if (Number.isFinite(v2) && v2 >= 0) baseKwh = v2;
      } catch {}
      
      // Get weather data for fallback calculation
      let cloud: number | null = null;
      let sunrise: any = null; let sunset: any = null;
      let tempC: number | null = null;
      try {
        const pdRaw = localStorage.getItem('last_ai_data');
        if (pdRaw) {
          const pd = JSON.parse(pdRaw);
          const w = pd?.weather || {};
          const c = w.cloud_cover ?? w.clouds;
          if (c != null) {
            const n = Number(c);
            cloud = Number.isFinite(n) ? (n > 1 ? Math.min(1, Math.max(0, n / 100)) : Math.min(1, Math.max(0, n))) : null;
          }
          sunrise = w.sunrise || w.astronomy?.sunrise || null;
          sunset = w.sunset || w.astronomy?.sunset || null;
          const t = w.temp_c ?? w.temperature_c ?? w.temp ?? null;
          tempC = Number.isFinite(Number(t)) ? Number(t) : null;
        }
      } catch {}
      
      // Calculate daylight hours
      let daylightHrs = 5.0;
      try {
        if (sunrise && sunset) {
          const sr = new Date(sunrise).getTime();
          const ss = new Date(sunset).getTime();
          if (Number.isFinite(sr) && Number.isFinite(ss) && ss > sr) {
            const hrs = (ss - sr) / 3600000;
            daylightHrs = Math.max(4.0, hrs);
          }
        }
      } catch {}
      
      const eff = 0.8;
      const cloudFactor = Math.max(0.15, (cloud != null ? (1 - cloud) : 0.8));
      const derivedProduction = sysKw * daylightHrs * eff * cloudFactor;
      
      // Enhanced production using live data
      let production = derivedProduction;
      if (energyData.length > 0) {
        const productions = energyData.map(d => d.production).filter(p => p > 0);
        if (productions.length > 0) {
          const avgProduction = productions.reduce((a, b) => a + b, 0) / productions.length;
          const peakProduction = Math.max(...productions);
          const liveBasedProduction = peakProduction * daylightHrs * cloudFactor * 0.8; // efficiency 0.8
          production = 0.7 * liveBasedProduction + 0.3 * derivedProduction;
        }
      }
      
      // Enhanced consumption using live patterns
      const tempAdj = tempC != null ? Math.min(1.3, Math.max(0.7, 1 + 0.02 * (tempC - 22))) : 1.0;
      let consumption = Math.max(0, baseKwh * tempAdj);
      if (energyData.length > 0) {
        const consumptions = energyData.map(d => d.usage);
        const avgConsumption = consumptions.reduce((a, b) => a + b, 0) / consumptions.length;
        consumption = avgConsumption * 24 * tempAdj;
      }
      
      // Accurate surplus calculation - can be negative (deficit)
      const baseSurplus = production - consumption;  // Removed Math.max(0, ...) to allow negative values
      let surplus = baseSurplus;
      
      if (energyData.length > 0) {
        const surpluses = energyData.map(d => d.net);
        const totalSurplus = surpluses.reduce((a, b) => a + b, 0);
        if (totalSurplus !== 0) {
          const avgHourlySurplus = totalSurplus / energyData.length;
          const projectedDailySurplus = avgHourlySurplus * 24 * cloudFactor;
          // Use weighted average instead of Math.max to preserve negative values
          surplus = 0.7 * baseSurplus + 0.3 * projectedDailySurplus;
        }
      }
      
      return surplus;
    };
    const params: Record<string, any> = {};
    if (geo.coords) {
      params.lat = geo.coords.lat;
      params.lon = geo.coords.lon;
    }
    
    // Add live data analysis for consistent predictions
    if (energyData.length > 0) {
      const productions = energyData.map(d => d.production).filter(p => p > 0);
      const consumptions = energyData.map(d => d.usage);
      const surpluses = energyData.map(d => d.net);
      
      params.live_avg_production = productions.length > 0 ? productions.reduce((a, b) => a + b, 0) / productions.length : 0;
      params.live_avg_consumption = consumptions.reduce((a, b) => a + b, 0) / consumptions.length;
      params.live_peak_production = productions.length > 0 ? Math.max(...productions) : 0;
      params.live_total_surplus = surpluses.reduce((a, b) => a + b, 0);
      params.live_efficiency = 0.8; // default efficiency
    }
    params.historical_data_points = energyData.length;
    
    try {
      const raw = localStorage.getItem('geo');
      if (raw) {
        const { city } = JSON.parse(raw);
        if (city) params.city = city;
      }
    } catch {}
    api
      .get('/predict/', { params })
      .then((r) => {
        if (!mounted) return;
        setPredictData(r.data);
        try { localStorage.setItem('last_ai_data', JSON.stringify(r.data)); } catch {}
        // Persist city if backend/AI returned weather.location.city
        const city = r.data?.weather?.location?.city || r.data?.weather?.city || null;
        if (city) {
          try {
            const raw = localStorage.getItem('geo');
            const prev = raw ? JSON.parse(raw) : {};
            localStorage.setItem('geo', JSON.stringify({ ...prev, city }));
          } catch {}
        }
        // derive a predicted surplus number from several possible fields the AI may return
        const predObj = r.data?.prediction || r.data;
        const iot = r.data?.iot_data || {};
        let predicted =
          // common names used in older/newer AI responses
          (predObj?.estimated_surplus_kwh ?? predObj?.predicted_surplus_kwh ?? predObj?.predicted_surplus ?? predObj?.surplus_kwh)
          // sometimes the microservice returns a nearby iot field with current surplus/deficit
          ?? (iot?.surplus_deficit_kwh ?? iot?.solar_generation_kwh ?? null)
          ?? null;
        if (typeof predicted === 'number') {
          // Allow negative values (deficits) - removed Math.max(0, ...)
          predicted = Number(predicted);
          // In testing mode, ensure it's positive so flows can be exercised easily
          if (TEST_FORCE_POS && predicted <= 0) {
            predicted = 3; // default positive test value
          }
          if (predicted > 0) setAmount(Number(predicted.toFixed(2)));
        } else {
          // fallback to heuristic surplus
          let fb = computeFallbackSurplus();
          if (TEST_FORCE_POS && fb <= 0) fb = 3;
          // Only set amount if we have actual surplus, not deficit
          if (fb > 0) setAmount(Number(fb.toFixed(2)));
        }
      })
      .catch(() => {
        // On failure, supply a derived fallback so the user isn't blocked
        let fb = computeFallbackSurplus();
        if (TEST_FORCE_POS && fb <= 0) fb = 3;
        if (fb > 0) setAmount(Number(fb.toFixed(2)));
      });
    return () => {
      mounted = false;
    };
  }, [geo.coords?.lat, geo.coords?.lon, energyData.length]);

  // Keep AI prediction fresh every 60s while on the page
  useEffect(() => {
    let mounted = true;
    let t: any;
    const tick = async () => {
      try {
        const params: Record<string, any> = {};
        if (geo.coords) { params.lat = geo.coords.lat; params.lon = geo.coords.lon; }
        
        // Add live data analysis for consistent predictions
        if (energyData.length > 0) {
          const productions = energyData.map(d => d.production).filter(p => p > 0);
          const consumptions = energyData.map(d => d.usage);
          const surpluses = energyData.map(d => d.net);
          
          params.live_avg_production = productions.length > 0 ? productions.reduce((a, b) => a + b, 0) / productions.length : 0;
          params.live_avg_consumption = consumptions.reduce((a, b) => a + b, 0) / consumptions.length;
          params.live_peak_production = productions.length > 0 ? Math.max(...productions) : 0;
          params.live_total_surplus = surpluses.reduce((a, b) => a + b, 0);
          params.live_efficiency = 0.8; // default efficiency
        }
        params.historical_data_points = energyData.length;
        
        const r = await api.get('/predict/', { params });
        if (!mounted) return;
        setPredictData(r.data);
      } catch {}
    };
    t = setInterval(tick, 60000);
    return () => { mounted = false; if (t) clearInterval(t); };
  }, [geo.coords?.lat, geo.coords?.lon, energyData.length]);

  // On first load, if we don't have coords cached, prompt for location once from Dashboard
  useEffect(() => {
    const hasCached = Boolean(localStorage.getItem('geo'));
    if (!hasCached && geo.permission !== 'denied' && !geo.loading && !geo.coords) {
      // Soft prompt; user can deny
      geo.refresh();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const runFlow = async () => {
    setLoading(true);
    setResult(null);
    try {
      // Ensure amount is a positive number
      const amount_kwh = Number(amount) || 0;
      if (amount_kwh <= 0) throw new Error('Please enter a valid amount of energy to export (> 0)');
      // Validate export does not exceed predicted surplus when available
      if (predictedSurplus != null && amount_kwh > predictedSurplus) {
        throw new Error(`Export amount exceeds predicted surplus (${predictedSurplus.toFixed(2)} kWh)`);
      }

      // Execute trade via backend proxy (export semantics)
      const execResp = await api.post('/execute_trade/', {
        type: 'EXPORT',
        amount: amount_kwh,
      });

  // After payment/confirmation, mint tokens 1 token per 1 kWh
      let mintResp = null;
      try {
        const household = execResp.data?.household_id || predictData?.household_id || 'HH_UI_001';
        mintResp = await api.post('/mint_energy/', {
          household_id: household,
          amount_kwh,
          reason: 'User sell: mint 1 token per 1 kWh',
        });
        } catch (e) {
          mintResp = { error: (e as any)?.message || String(e), detail: (e as any)?.response?.data };
        }

  // Update token balance UI and show notifications
      const mintData = mintResp?.data ?? mintResp;
      const minted = mintData?.tokens_minted ?? (mintData?.amount_kwh ?? null) ?? amount;
      const tx = mintData?.tx_hash ?? mintData?.tx ?? mintData?.transaction ?? null;

      if (mintData && (tx || minted)) {
        // Prefer concise user_message if backend provided one
        const userMsg = mintData.user_message || `Exported ${amount} kWh — minted ${minted} tokens${tx ? ` — tx: ${tx}` : ' — tx pending'}`;
        showToast(userMsg, 'success');

        // Update token balance from backend (prefer authoritative source)
        try {
          const balanceResp = await api.get('/account/balance/');
          if (balanceResp?.data?.token_balance != null) {
            const el = document.getElementById('token-balance');
            if (el) el.textContent = String(Number(balanceResp.data.token_balance).toFixed(3));
            try { window.dispatchEvent(new CustomEvent('tokenBalanceUpdate', { detail: { value: Number(balanceResp.data.token_balance) } })); } catch {}
          }
        } catch (e) {
          // Fallback: simple DOM increment if backend balance not available
          try {
            const el = document.getElementById('token-balance');
            if (el) {
              const prev = Number(el.textContent) || 0;
              el.textContent = String((prev + Number(amount)).toFixed(3));
              try { window.dispatchEvent(new CustomEvent('tokenBalanceUpdate', { detail: { value: (prev + Number(amount)) } })); } catch {}
            }
          } catch (e2) {}
        }
        // Also update local state tokenBalance and exportedToday when possible
        try {
          // bump tokenBalance state if present on page
          const nb = document.getElementById('token-balance')?.textContent;
          // no-op; UI already updated
        } catch {}
      } else if (mintData && mintData.error) {
        const userMsg = mintData.user_message || `Mint failed: ${mintData.error}`;
        showToast(userMsg, 'error');
      }

      // After a successful mint, immediately reflect exported energy in our daily accumulator
      try {
        if (!mintData?.error) {
          const params: Record<string, any> = { device: (selectedDevice || (import.meta as any)?.env?.VITE_IOTC_DEVICE_ID || 'sim-1') };
          // Prefer current selected component persisted in localStorage
          let comp: string | undefined;
          try { comp = (localStorage.getItem('iotc_component') || '').trim() || undefined; } catch {}
          if (!comp) { comp = (import.meta as any)?.env?.VITE_IOTC_COMPONENT; }
          if (comp) params.component = comp;
          await api.post('/iotcentral/increment_energy/', { ...params, kwh: amount_kwh });
          // also simulate a small telemetry point so Live Meter/latest nudges immediately
          await api.get('/iotcentral/simulate/', { params: { device: params.device, component: params.component, power: Math.max(0.1, Math.min(5, amount_kwh)) } });
          // Refresh exportedToday immediately
          try {
            const r = await api.get('/iotcentral/daily_exported/', { params });
            const v = r.data?.energy_kwh;
            if (typeof v === 'number') {
              // Find the nearest set function via a dispatch event
              const evt = new CustomEvent('exportedTodayUpdate', { detail: { value: v } });
              window.dispatchEvent(evt);
            }
          } catch {
            // If we cannot read the new total right now, at least bump the UI by the exported amount
            try { window.dispatchEvent(new CustomEvent('exportedTodayUpdate', { detail: { delta: amount_kwh } })); } catch {}
          }
        }
      } catch {}

      setResult({ predict: predictData, execute: execResp.data, mint: mintData });
    } catch (e: any) {
      // Friendly toast for users — prefer backend-provided message when available
      const resp = e?.response;
      if (resp && resp.data) {
        const msg = resp.data.error || resp.data.message || JSON.stringify(resp.data);
        showToast(`Export failed: ${msg} (status ${resp.status})`, 'error');
        setResult({ error: msg, detail: resp.data });
      } else {
        const msg = e?.message || String(e);
        showToast(`Export failed: ${msg}`, 'error');
        setResult({ error: msg });
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-3">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-2 items-end">
        <div>
          <label className="text-sm text-muted-foreground block">Amount to export (kWh)</label>
          <input
            type="number"
            className="w-full p-2 rounded border"
            step="0.01"
            min="0"
            value={amount}
            onChange={(e) => setAmount(Number(e.target.value))}
          />
        </div>
      </div>

      <div className="flex gap-2">
        <Button onClick={runFlow} disabled={loading}>
          {loading ? 'Processing…' : `Export ${amount} kWh & Mint ${amount} tokens`}
        </Button>
      </div>

      {result && (
        <div className="space-y-2">
          {result.error ? (
            <div className="text-sm text-destructive">Error: {result.error}</div>
          ) : (
            <ResultSummary result={result} />
          )}
        </div>
      )}
    </div>
  );
}

function LiveMeter({ deviceId, component, label, unit, formatter }: { deviceId?: string; component?: string; label?: string; unit?: string; formatter?: (v:number)=>string }) {
  const [value, setValue] = useState<number | null>(null);
  const [ts, setTs] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    let t: any;
    const fetchLatest = async () => {
      try {
        const params: Record<string, any> = {};
        if (deviceId) params.device = deviceId;
        if (component) params.component = component;
        const r = await api.get('/iotcentral/latest/', { params });
        // Backend returns root object {device, component, timestamp, data:{power: X}}
        const root = r.data || {};
        
        // Direct access to the data.power field from backend response
        let v: any = root.data?.power;
        
        // Convert to kW if it's in watts (values > 100 likely watts)
        if (typeof v === 'number' && v > 100) {
          v = v / 1000.0;
        }
        
        if (typeof v === 'string') v = parseFloat(v);
        if (typeof v === 'number' && Number.isFinite(v) && mounted) {
          setValue(v);
          const tRoot = (typeof root?.timestamp === 'number' ? new Date(root.timestamp * 1000).toISOString() : null);
          setTs(tRoot);
        }
      } catch (e) {
        // ignore transient errors
      }
    };
    fetchLatest();
    t = setInterval(fetchLatest, 4000);
    return () => { mounted = false; if (t) clearInterval(t); };
  }, [deviceId, component]);

  const txt = typeof value === 'number' ? (formatter ? formatter(value) : `${value} ${unit||''}`.trim()) : '—';
  return (
    <div>
      <div className="text-3xl font-bold text-foreground">{txt}</div>
      {ts && <div className="text-xs text-muted-foreground">updated {new Date(ts).toLocaleTimeString()}</div>}
      {label && <div className="text-xs text-muted-foreground">{label}</div>}
    </div>
  );
}
