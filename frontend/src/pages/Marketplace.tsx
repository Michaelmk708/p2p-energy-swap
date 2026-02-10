import React, { useEffect, useState } from 'react';
import { Layout } from '@/components/Layout';
import { Button } from '@/components/ui/button';
import ToastContainer, { showToast } from '@/components/Toast';
import axios from 'axios';
import { Badge } from '@/components/ui/badge'; // Ensure you have this or remove if not

// Helper: validate Kenyan MSISDN
const isValidMsisdn = (msisdn: string) => /^2547\d{8}$/.test(msisdn);

const Marketplace = () => {
    // --- 1. State Declarations ---
    const [listings, setListings] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);
    const [marketPrediction, setMarketPrediction] = useState<any | null>(null);
    const [stkModal, setStkModal] = useState<{open:boolean, checkout_request_id?:string, amount?:number, trade_id?:string}>(()=>({open:false}));
    const [phoneModal, setPhoneModal] = useState<{open:boolean, listing?:any, phone:string, error?:string}>(()=>({open:false, phone: localStorage.getItem('phone') || ''}));
    const [tokenBalance, setTokenBalance] = useState<number>(0);
    const [sellModal, setSellModal] = useState<{open: boolean, amount: number, price: number}>({open: false, amount: 1, price: 15.00}); // Default price 15

    // --- 2. Configuration ---
    const API_BASE_URL = import.meta.env.VITE_API_URL || 
        (window.location.hostname === 'localhost' ? 'http://localhost:8000/api' : `http://${window.location.hostname}:8000/api`);

    const householdId = localStorage.getItem('household_id') || 'sim-1';

    const getHeaders = () => {
        const token = localStorage.getItem('access');
        return {
            'Content-Type': 'application/json',
            ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        };
    };

    // --- 3. Data Fetching ---
    const refreshBalance = async () => {
        try {
            const res = await axios.get(`${API_BASE_URL}/account/balance/`, { 
                params: { household_id: householdId }, headers: getHeaders()
            });
            setTokenBalance(Number(res.data?.token_balance ?? 0));
        } catch (error) {
            console.error("Failed to refresh balance");
            // Keep existing balance if fail
        }
    };

    const fetchListings = async () => {
        try {
            const res = await axios.get(`${API_BASE_URL}/marketplace/`, { 
                params: { household_id: householdId }, headers: getHeaders()
            });
            // Merge API listings with current simulated ones (if any exist in state)
            const apiListings = res.data.listings || [];
            setListings(prev => {
                // Keep simulated ones, replace real ones
                const simulated = prev.filter(l => l.is_simulated);
                return [...simulated, ...apiListings];
            });
        } catch (error) {
            console.error("Failed to fetch listings");
        }
    };

    const fetchPrediction = async () => {
        try {
            const res = await axios.get(`${API_BASE_URL}/predict/`, { 
                params: { household: householdId, live_avg_production: 1.5, live_avg_consumption: 2.0 },
                headers: getHeaders()
            });
            setMarketPrediction(res.data || null);
        } catch (error) {
            setMarketPrediction({ summary: 'Stable', best_action: 'buy', reason: 'Grid rates are high. Buy P2P.' });
        }
    };

    // --- 4. SIMULATION ENGINE (THE PITCH SAVER) ---
    useEffect(() => {
        // Initial Fetch
        refreshBalance();
        fetchListings();
        fetchPrediction();

        // A. Real Polling (Every 10s)
        const realInterval = setInterval(() => {
            refreshBalance();
            fetchListings(); // This fetches REAL DB items
        }, 10000);

        // B. "Live Minting" Effect (Every 5s)
        // This injects fake neighbors into the list so the market looks busy
        const simulationInterval = setInterval(() => {
            // Only add if we have fewer than 8 items to avoid clutter
            setListings(prev => {
                if (prev.length > 8) return prev; 
                
                const newMockListing = {
                    id: `sim-${Date.now()}`, // Unique fake ID
                    seller: `Neighbor-${Math.floor(Math.random() * 20) + 1}`,
                    amount: (Math.random() * 3 + 0.5).toFixed(2),
                    price_per_token: 15.00,
                    side: 'SELL',
                    is_simulated: true, // FLAG: This is a fake item
                    created_at: new Date().toISOString()
                };
                
                // Show a toast sometimes to draw attention
                if (Math.random() > 0.7) {
                    showToast(`New Token Minted: ${newMockListing.amount} kWh from ${newMockListing.seller}`, 'info');
                }
                
                return [newMockListing, ...prev]; // Add to top
            });
        }, 5000);

        return () => {
            clearInterval(realInterval);
            clearInterval(simulationInterval);
        };
    }, [householdId]);


    // --- 5. Transaction Logic (Hybrid) ---

    // A. Start Transaction (Triggered by Modal)
    const confirmPhone = async () => {
      const listing = phoneModal.listing;
      const phone = (phoneModal.phone || '').trim();
      
      if (!listing) return;

      // VALIDATION
      if (!isValidMsisdn(phone)) {
        setPhoneModal((s) => ({ ...s, error: 'Enter valid number: 2547XXXXXXXX' }));
        return;
      }

      setPhoneModal({ open: false, listing: undefined, phone: phone });

      // *** HYBRID FORK ***
      if (listing.is_simulated) {
          // PATH 1: SIMULATED BUY (Instant Success for Pitch)
          setLoading(true);
          setTimeout(() => {
              showToast(`✅ Payment Received! P2P Power from ${listing.seller} Active.`, 'success');
              setListings(prev => prev.filter(l => l.id !== listing.id)); // Remove from list
              setLoading(false);
          }, 1500); // Fake delay for realism
      } else {
          // PATH 2: REAL M-PESA BUY (For Real Backend Items)
          await startStk(listing, phone);
      }
    };

    // B. Real M-Pesa Logic
    const startStk = async (listing: any, phone: string) => {
        setLoading(true);
        try {
            const cleanedPhone = phone.replace(/\s+/g, '');
            localStorage.setItem('phone', cleanedPhone);

            const amountKES = Math.max(1, Math.round((listing.price_kes || listing.price_per_token || 15) * listing.amount)); // Handle both data structures
            const trade_id = `buy-${listing.id}-${Date.now()}`;
            
            const resp = await axios.post(`${API_BASE_URL}/mpesa/stk_push/`, 
                { phone: cleanedPhone, amount: amountKES, trade_id, listing_id: listing.id },
                { headers: getHeaders() }
            );
            
            const data = resp.data || {};
            setStkModal({ open: true, checkout_request_id: data.checkout_request_id, amount: data.amount_kes || amountKES, trade_id: data.trade_id || trade_id });
            showToast('Checkout initiated. Check your phone.', 'info');

            // Poll for status
            pollMpesaStatus(data.trade_id || trade_id);

        } catch (e: any) {
            showToast('STK Push failed: ' + (e.response?.data?.error || e.message), 'error');
        } finally {
            setLoading(false);
        }
    };

    const pollMpesaStatus = (tid: string) => {
        const start = Date.now();
        const poll = async () => {
            try {
                const r = await axios.get(`${API_BASE_URL}/mpesa/status/`, { 
                    params: { trade_id: tid }, headers: getHeaders() 
                });
                const status = (r.data && (r.data.status || r.data.payment_status)) || 'unknown';
                
                if (status === 'confirmed' || status === 'success') {
                    setStkModal({ open: false });
                    showToast('Payment confirmed. Smart Meter Updated.', 'success');
                    refreshBalance();
                    fetchListings();
                    return;
                }
            } catch (_) { }
            
            if (Date.now() - start < 60000) setTimeout(poll, 3000); // Poll for 1 min
        };
        setTimeout(poll, 3000);
    };

    // C. Selling Logic (Create Listing)
    const handleCreateSellListing = async () => {
        const { amount, price } = sellModal;
        if (amount <= 0 || price <= 0) return showToast('Invalid input', 'error');
        if (amount > tokenBalance) return showToast('Insufficient tokens', 'error');

        setLoading(true);
        try {
            await axios.post(`${API_BASE_URL}/marketplace/`, {
                amount: amount, price_per_token: price, seller: householdId, household_id: householdId 
            }, { headers: getHeaders() });

            showToast(`Listed ${amount} tokens @ KES ${price}`, 'success');
            setSellModal(s => ({...s, open: false}));
            refreshBalance();
            fetchListings();
        } catch (e: any) {
            showToast('Failed to list: ' + (e.response?.data?.error || e.message), 'error');
        } finally {
            setLoading(false);
        }
    };

    const handleSellBuyOrder = (l: any) => {
        // Logic for selling to a buy order...
        // For the pitch, we focus mostly on Buying P2P power
        showToast("Feature active in Pro version", "info");
    }

    return (
        <Layout>
            <ToastContainer />
            <div className="p-4 space-y-6 pb-20">
                
                {/* Header */}
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                    <div>
                        <h2 className="text-3xl font-bold">P2P Marketplace</h2>
                        <p className="text-muted-foreground">Live community energy trading.</p>
                    </div>
                    {/* Token Balance Card */}
                    <div className="p-4 border rounded-xl bg-green-50 dark:bg-green-900/20 flex items-center gap-6 shadow-sm">
                        <div>
                            <h3 className="text-xs font-semibold uppercase text-green-700">My Wallet</h3>
                            <div className="text-2xl font-bold">{tokenBalance.toFixed(2)} <span className="text-sm text-muted-foreground">Tokens</span></div>
                        </div>
                        <Button onClick={() => setSellModal({open: true, amount: 1, price: 15.00})} className="bg-green-600 hover:bg-green-700">
                            Sell Energy
                        </Button>
                    </div>
                </div>

                {/* Sell Modal */}
                {sellModal.open && (
                    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 animate-in fade-in">
                        <div className="bg-white dark:bg-slate-800 p-6 rounded-lg shadow-xl max-w-md w-full">
                            <h3 className="text-xl font-bold mb-4">Mint & Sell Tokens</h3>
                            <div className="space-y-4">
                                <div>
                                    <label className="text-sm font-medium">Amount (kWh)</label>
                                    <input type="number" value={sellModal.amount} onChange={e => setSellModal(s => ({...s, amount: parseFloat(e.target.value)}))}
                                        className="w-full p-2 border rounded mt-1" />
                                </div>
                                <div>
                                    <label className="text-sm font-medium">Price (KES/kWh)</label>
                                    <input type="number" value={sellModal.price} onChange={e => setSellModal(s => ({...s, price: parseFloat(e.target.value)}))}
                                        className="w-full p-2 border rounded mt-1" />
                                </div>
                                <div className="flex justify-end gap-2 pt-2">
                                    <Button variant="outline" onClick={() => setSellModal(s => ({...s, open: false}))}>Cancel</Button>
                                    <Button onClick={handleCreateSellListing} disabled={loading}>Confirm Listing</Button>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* MAIN LISTINGS TABLE */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    
                    {/* LEFT: SELL ORDERS (The Main Attraction) */}
                    <div className="lg:col-span-2">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="font-bold text-lg flex items-center gap-2">
                                ⚡ Available Power
                                <span className="bg-green-100 text-green-700 text-xs px-2 py-0.5 rounded-full animate-pulse">LIVE</span>
                            </h3>
                        </div>
                        
                        <div className="border rounded-lg overflow-hidden bg-white dark:bg-slate-800 shadow-sm">
                            <table className="w-full text-sm">
                                <thead className="bg-gray-50 dark:bg-slate-700 text-xs uppercase text-muted-foreground">
                                    <tr>
                                        <th className="px-4 py-3 text-left">Source</th>
                                        <th className="px-4 py-3 text-left">Energy</th>
                                        <th className="px-4 py-3 text-left">Rate</th>
                                        <th className="px-4 py-3 text-left">Cost</th>
                                        <th className="px-4 py-3 text-right">Action</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y dark:divide-slate-700">
                                    {listings.filter(x => (x.side || 'SELL') === 'SELL').map((l) => (
                                        <tr key={l.id} className={`hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors ${l.is_simulated ? 'bg-green-50/30' : ''}`}>
                                            <td className="px-4 py-3 font-medium">
                                                {l.seller}
                                                {l.is_simulated && <span className="ml-2 text-[10px] bg-blue-100 text-blue-700 px-1 rounded">NEW</span>}
                                            </td>
                                            <td className="px-4 py-3">{Number(l.amount).toFixed(2)} kWh</td>
                                            <td className="px-4 py-3 text-green-600 font-semibold">KES {l.price_per_token}</td>
                                            <td className="px-4 py-3 font-bold">KES {(l.amount * l.price_per_token).toFixed(2)}</td>
                                            <td className="px-4 py-3 text-right">
                                                <Button size="sm" onClick={() => setPhoneModal({open: true, listing: l, phone: localStorage.getItem('phone') || '', error: ''})}>
                                                    Buy Now
                                                </Button>
                                            </td>
                                        </tr>
                                    ))}
                                    {listings.length === 0 && (
                                        <tr><td colSpan={5} className="p-8 text-center text-muted-foreground">Waiting for producers...</td></tr>
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </div>

                    {/* RIGHT: PREDICTIONS */}
                    <div>
                        <h3 className="font-bold text-lg mb-4">AI Insight</h3>
                        <div className="border rounded-lg p-5 bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-slate-800 dark:to-slate-900">
                            {marketPrediction ? (
                                <div>
                                    <div className="uppercase text-xs text-muted-foreground font-bold tracking-wider mb-1">Recommendation</div>
                                    <div className="text-2xl font-extrabold text-blue-700 mb-2">
                                        {marketPrediction.best_action || 'BUY NOW'}
                                    </div>
                                    <p className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
                                        {marketPrediction.reason || "Solar Glut detected. Prices are 30% lower than grid."}
                                    </p>
                                </div>
                            ) : (
                                <div className="text-sm">Analyzing market trends...</div>
                            )}
                        </div>
                    </div>
                </div>

                {/* Phone Confirmation Modal */}
                {phoneModal.open && (
                    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
                        <div className="bg-white dark:bg-slate-800 p-6 rounded-lg shadow-xl max-w-sm w-full">
                            <h3 className="text-lg font-bold mb-2">Confirm Purchase</h3>
                            <p className="text-sm text-muted-foreground mb-4">
                                Buying <strong>{phoneModal.listing?.amount} kWh</strong> for <strong>KES {(phoneModal.listing?.amount * phoneModal.listing?.price_per_token).toFixed(2)}</strong>
                            </p>
                            
                            <label className="text-xs font-semibold uppercase text-muted-foreground">M-Pesa Number</label>
                            <input
                                type="tel"
                                className="mt-1 w-full p-3 rounded border bg-slate-50 dark:bg-slate-900 font-mono text-lg"
                                placeholder="2547XXXXXXXX"
                                value={phoneModal.phone}
                                onChange={(e) => setPhoneModal((s) => ({ ...s, phone: e.target.value, error: '' }))}
                            />
                            {phoneModal.error && <div className="text-sm text-red-500 mt-2">{phoneModal.error}</div>}
                            
                            <div className="mt-6 flex justify-end gap-3">
                                <Button variant="outline" onClick={() => setPhoneModal({ open: false, listing: undefined, phone: phoneModal.phone })}>Cancel</Button>
                                <Button onClick={confirmPhone} disabled={loading} className="bg-green-600 hover:bg-green-700">
                                    {loading ? 'Processing...' : 'Pay with M-Pesa'}
                                </Button>
                            </div>
                        </div>
                    </div>
                )}
                
                {/* STK Modal */}
                {stkModal.open && (
                     <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
                        <div className="bg-white dark:bg-slate-800 p-8 rounded-lg shadow-xl max-w-sm w-full text-center">
                            <div className="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-4">
                                <span className="text-2xl animate-pulse">📲</span>
                            </div>
                            <h3 className="text-xl font-bold mb-2">Check your Phone</h3>
                            <p className="text-sm text-muted-foreground mb-6">
                                Enter your PIN to pay <strong>KES {stkModal.amount}</strong>
                            </p>
                            <Button variant="outline" onClick={() => setStkModal(s=>({...s, open: false}))}>Close</Button>
                        </div>
                    </div>
                )}
            </div>
        </Layout>
    );
};

export default Marketplace;