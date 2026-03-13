import { useState, useEffect } from "react";
import { Layout } from "@/components/Layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Zap, Wallet, Sun, Power, Coins, Link as LinkIcon, ShieldCheck } from "lucide-react";
import { useUser } from "@/contexts/UserContext";
import api from "@/lib/api";

export default function Dashboard() {
  const { user } = useUser();
  const [marketData, setMarketData] = useState<any>(null);
  // Initialized with safe defaults
  const [meterData, setMeterData] = useState<any>({ solar: 0, load: 0, net: 0 });
  const [currentTime, setCurrentTime] = useState(new Date());
  const [tokensMinted, setTokensMinted] = useState(0);

  // 1. Clock
  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  // 2. Fetch Data (Bulletproofed)
  useEffect(() => {
    const fetchData = async () => {
      try {
        const marketRes = await api.get('/trade/status/');
        setMarketData(marketRes.data);
        
        const meterRes = await api.get('/meter/status/');
        // Normalize data just in case backend uses different keys (solar vs solar_kw)
        const rawData = meterRes.data || {};
        const safeData = {
            solar: Number(rawData.solar || rawData.solar_kw || 0),
            load: Number(rawData.load || rawData.load_kw || 0),
            net: Number(rawData.net || rawData.net_kw || 0)
        };
        
        // Calculate net if backend doesn't provide it
        if (!safeData.net) {
            safeData.net = safeData.solar - safeData.load;
        }
        
        setMeterData(safeData);
        
        // Simulating Token Minting if Selling (Surplus)
        if (safeData.net > 0) {
            setTokensMinted(prev => prev + (safeData.net * 0.1)); // Increment realistically
        }
      } catch (error) { 
          console.error("Dashboard Fetch Error:", error); 
      }
    };
    
    fetchData();
    const interval = setInterval(fetchData, 1000);
    return () => clearInterval(interval);
  }, []);

  if (!marketData) return <Layout><div className="p-10 text-muted-foreground animate-pulse">Connecting to IoT Oracle...</div></Layout>;

  // LOGIC: Determine Active Source
  const isSelling = meterData.net > 0;
  const isP2PBuying = !isSelling && marketData.status === 'SOLAR_GLUT';
  const isKPLC = !isSelling && !isP2PBuying;

  return (
    <Layout>
      <div className="space-y-6 animate-fade-in pb-20">
        
        {/* HEADER */}
        <div className="flex justify-between items-center border-b pb-4">
          <div>
            <h1 className="text-3xl font-bold text-foreground tracking-tight">DePIN Energy Command</h1>
            <p className="text-muted-foreground font-mono text-sm mt-1">{currentTime.toLocaleTimeString()} | Sub-Meter Node Active</p>
          </div>
          <Badge variant={marketData.status === 'SOLAR_GLUT' ? 'default' : 'outline'} 
            className={`px-4 py-1 text-sm ${marketData.color === 'green' ? 'bg-green-100 text-green-800 border-green-300' : ''}`}>
            {marketData.status.replace('_', ' ')}
          </Badge>
        </div>

        {/* --- ROW 1: REGULATORY LAYER (EPRA Compliance) --- */}
        <h2 className="text-xs font-bold text-muted-foreground uppercase tracking-widest flex items-center gap-2">
            <ShieldCheck className="w-4 h-4" /> Physical Infrastructure (EPRA Compliant)
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          
          {/* SOLAR */}
          <Card className="bg-gradient-to-br from-white to-orange-50/30">
            <CardHeader className="pb-2"><CardTitle className="flex items-center gap-2 text-sm text-muted-foreground"><Sun className="h-4 w-4 text-orange-500" /> CAPTIVE SOLAR PV</CardTitle></CardHeader>
            <CardContent>
              <div className="text-4xl font-bold">{meterData.solar.toFixed(2)} <span className="text-lg text-muted-foreground font-normal">kW</span></div>
            </CardContent>
          </Card>

          {/* LOAD */}
          <Card>
            <CardHeader className="pb-2"><CardTitle className="flex items-center gap-2 text-sm text-muted-foreground"><Zap className="h-4 w-4 text-blue-500" /> TENANT LOAD</CardTitle></CardHeader>
            <CardContent>
              <div className="text-4xl font-bold">{meterData.load.toFixed(2)} <span className="text-lg text-muted-foreground font-normal">kW</span></div>
            </CardContent>
          </Card>

          {/* ACTIVE SOURCE (THE SMART SWITCH) */}
          <Card className={isP2PBuying ? "bg-green-50 border-green-500" : isKPLC ? "bg-red-50 border-red-200" : "bg-blue-50 border-blue-500"}>
            <CardHeader className="pb-2"><CardTitle className="flex items-center gap-2 text-sm text-muted-foreground"><Power className="h-4 w-4" /> MAIN GRID STATUS</CardTitle></CardHeader>
            <CardContent>
              {isSelling ? (
                 <div>
                    <div className="text-2xl font-bold text-blue-700">EXPORTING</div>
                    <div className="text-sm mt-1 text-blue-600/80">KPLC Bulk Meter: <span className="font-mono bg-blue-100 px-1 rounded">PAUSED ⏸️</span></div>
                 </div>
              ) : isP2PBuying ? (
                 <div>
                    <div className="text-2xl font-bold text-green-700">LOCAL P2P</div>
                    <div className="text-sm mt-1 text-green-600/80">KPLC Bulk Meter: <span className="font-mono bg-green-100 px-1 rounded">PAUSED ⏸️</span></div>
                 </div>
              ) : (
                 <div>
                    <div className="text-2xl font-bold text-red-700">KPLC GRID</div>
                    <div className="text-sm mt-1 text-red-600/80">KPLC Bulk Meter: <span className="font-mono animate-pulse bg-red-100 px-1 rounded">IMPORTING ⚡</span></div>
                 </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* --- ROW 2: WEB3 LAYER (Investor Tokenomics) --- */}
        <h2 className="text-xs font-bold text-muted-foreground uppercase tracking-widest flex items-center gap-2 mt-4">
            <LinkIcon className="w-4 h-4" /> Web3 Settlement Ledger (Solana Network)
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          
          {/* TARIFF */}
          <Card className={`border-2 ${marketData.color === 'green' ? 'border-green-600 shadow-green-100' : 'border-slate-200'}`}>
            <CardHeader className="pb-2"><CardTitle className="flex items-center gap-2 text-sm text-muted-foreground"><Wallet className="h-4 w-4" /> SMART CONTRACT TARIFF</CardTitle></CardHeader>
            <CardContent>
              <div className="text-5xl font-extrabold font-mono text-slate-800">KES {marketData.price}</div>
              <p className="text-sm text-muted-foreground mt-2">{marketData.message}</p>
            </CardContent>
          </Card>

          {/* TRADING ENGINE */}
          <Card className="bg-slate-900 text-slate-50 border-slate-800">
            <CardHeader className="pb-2"><CardTitle className="flex items-center gap-2 text-sm text-slate-400"><Coins className="h-4 w-4 text-yellow-500" /> TOKENIZATION ENGINE</CardTitle></CardHeader>
            <CardContent>
              <div className="flex justify-between items-end mb-4">
                <div>
                   <div className="text-3xl font-bold">{isSelling ? "Minting RWA" : "Awaiting Surplus"}</div>
                   <div className="text-xs text-slate-400 mt-1">Status: {isSelling ? "Anchoring to Blockchain" : "Hardware Oracle Standby"}</div>
                </div>
                {isSelling && <Badge className="bg-yellow-500 animate-pulse text-black hover:bg-yellow-400 border-none">LIVE ON CHAIN</Badge>}
              </div>
              
              <div className="bg-slate-800/50 border border-slate-700 p-3 rounded-lg flex justify-between items-center font-mono text-sm">
                 <span className="text-slate-400">Total KES Pegged:</span>
                 <span className="text-lg font-bold text-green-400">+{tokensMinted.toFixed(2)} TK</span>
              </div>
            </CardContent>
          </Card>

        </div>
      </div>
    </Layout>
  );
}