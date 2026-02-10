import { useState, useEffect } from "react";
import { Layout } from "@/components/Layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Zap, Wallet, Sun, Activity, Power, Coins } from "lucide-react";
import { useUser } from "@/contexts/UserContext";
import api from "@/lib/api";

export default function Dashboard() {
  const { user } = useUser();
  const [marketData, setMarketData] = useState<any>(null);
  const [meterData, setMeterData] = useState<any>({ solar_kw: 0, load_kw: 0, battery_percent: 85, net_kw: 0 });
  const [currentTime, setCurrentTime] = useState(new Date());
  const [tokensMinted, setTokensMinted] = useState(124); // Mock start

  // 1. Clock
  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  // 2. Fetch Data
  useEffect(() => {
    const fetchData = async () => {
      try {
        const marketRes = await api.get('/trade/status/');
        setMarketData(marketRes.data);
        const meterRes = await api.get('/meter/status/');
        setMeterData(meterRes.data);
        
        // Simulating Token Minting if Selling
        if (meterRes.data.net_kw > 0) {
            setTokensMinted(prev => prev + 1);
        }
      } catch (error) { console.error(error); }
    };
    fetchData();
    const interval = setInterval(fetchData, 1000);
    return () => clearInterval(interval);
  }, []);

  if (!marketData) return <Layout><div className="p-10">Connecting to Grid...</div></Layout>;

  // LOGIC: Determine Active Source
  const isSelling = meterData.net_kw > 0;
  const isP2PBuying = !isSelling && marketData.status === 'SOLAR_GLUT';
  const isKPLC = !isSelling && !isP2PBuying;

  return (
    <Layout>
      <div className="space-y-6 animate-fade-in pb-20">
        
        {/* HEADER */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Energy Command</h1>
            <p className="text-muted-foreground">{currentTime.toLocaleTimeString()}</p>
          </div>
          <Badge variant={marketData.status === 'SOLAR_GLUT' ? 'default' : 'outline'} 
            className={marketData.color === 'green' ? 'bg-green-100 text-green-800' : ''}>
            {marketData.status.replace('_', ' ')}
          </Badge>
        </div>

        {/* --- ROW 1: THE SMART METER (Physical Layer) --- */}
        <h2 className="text-sm font-bold text-muted-foreground uppercase tracking-wider">Physical Layer (Behind-The-Meter)</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          
          {/* SOLAR */}
          <Card>
            <CardHeader className="pb-2"><CardTitle className="flex items-center gap-2"><Sun className="h-5 w-5 text-orange-500" /> Solar PV</CardTitle></CardHeader>
            <CardContent>
              <div className="text-4xl font-bold">{meterData.solar_kw.toFixed(2)} <span className="text-lg text-muted-foreground">kW</span></div>
            </CardContent>
          </Card>

          {/* LOAD */}
          <Card>
            <CardHeader className="pb-2"><CardTitle className="flex items-center gap-2"><Zap className="h-5 w-5 text-blue-500" /> House Load</CardTitle></CardHeader>
            <CardContent>
              <div className="text-4xl font-bold">{meterData.load_kw.toFixed(2)} <span className="text-lg text-muted-foreground">kW</span></div>
            </CardContent>
          </Card>

          {/* ACTIVE SOURCE (THE SMART SWITCH) */}
          <Card className={isP2PBuying ? "bg-green-50 border-green-500" : isKPLC ? "bg-red-50 border-red-500" : "bg-blue-50 border-blue-500"}>
            <CardHeader className="pb-2"><CardTitle className="flex items-center gap-2"><Power className="h-5 w-5" /> Active Source</CardTitle></CardHeader>
            <CardContent>
              {isSelling ? (
                 <div>
                    <div className="text-2xl font-bold text-blue-700">EXPORTING</div>
                    <div className="text-sm mt-1">KPLC Meter: <span className="font-mono">PAUSED ⏸️</span></div>
                 </div>
              ) : isP2PBuying ? (
                 <div>
                    <div className="text-2xl font-bold text-green-700">NEIGHBOR (P2P)</div>
                    <div className="text-sm mt-1">KPLC Meter: <span className="font-mono">PAUSED ⏸️</span></div>
                    <div className="text-xs text-green-800 mt-2 font-bold">Saving Grid Tokens!</div>
                 </div>
              ) : (
                 <div>
                    <div className="text-2xl font-bold text-red-700">KPLC GRID</div>
                    <div className="text-sm mt-1">KPLC Meter: <span className="font-mono animate-pulse">RUNNING ⚡</span></div>
                    <div className="text-xs text-red-800 mt-2">P2P Unavailable</div>
                 </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* --- ROW 2: THE MARKET LAYER (Economics) --- */}
        <h2 className="text-sm font-bold text-muted-foreground uppercase tracking-wider mt-4">Market Layer (Tokenomics)</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          
          {/* TARIFF */}
          <Card className={`border-2 ${marketData.color === 'green' ? 'border-green-600' : 'border-blue-600'}`}>
            <CardHeader className="pb-2"><CardTitle className="flex items-center gap-2"><Wallet className="h-5 w-5" /> Live Tariff</CardTitle></CardHeader>
            <CardContent>
              <div className="text-5xl font-extrabold">KES {marketData.price}</div>
              <p className="text-sm text-muted-foreground mt-2">{marketData.message}</p>
            </CardContent>
          </Card>

          {/* TRADING ENGINE (Replaces Battery Status) */}
          <Card>
            <CardHeader className="pb-2"><CardTitle className="flex items-center gap-2"><Coins className="h-5 w-5 text-yellow-500" /> Trading Engine</CardTitle></CardHeader>
            <CardContent>
              <div className="flex justify-between items-end mb-2">
                <div>
                   <div className="text-3xl font-bold text-foreground">{isSelling ? "Active" : "Standby"}</div>
                   <div className="text-xs text-muted-foreground">Auto-Minting Protocol</div>
                </div>
                {isSelling && <Badge className="bg-yellow-500 animate-pulse text-black">MINTING TOKENS</Badge>}
              </div>
              
              {/* Visualizing Money being made */}
              <div className="bg-muted p-3 rounded-lg flex justify-between items-center">
                 <span className="text-sm font-medium">Session Earnings:</span>
                 <span className="text-xl font-bold text-green-600">+{tokensMinted} TK</span>
              </div>
            </CardContent>
          </Card>

        </div>
      </div>
    </Layout>
  );
}