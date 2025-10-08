import React, { useEffect, useState } from 'react';
import { Layout } from '@/components/Layout';
import api from '@/lib/api';
import { Button } from '@/components/ui/button';
import ToastContainer, { showToast } from '@/components/Toast';

export default function Marketplace() {
	const [listings, setListings] = useState<any[]>([]);
	const [loading, setLoading] = useState(false);
	const [marketPrediction, setMarketPrediction] = useState<any | null>(null);
	const [stkModal, setStkModal] = useState<{open:boolean, checkout_request_id?:string, amount?:number, trade_id?:string}>(()=>({open:false}));
  const [phoneModal, setPhoneModal] = useState<{open:boolean, listing?:any, phone:string, error?:string}>(()=>({open:false, phone: localStorage.getItem('phone') || ''}));

	useEffect(() => {
		api
			.get('/marketplace/')
			.then((r) => setListings(r.data.listings || []))
			.catch(() => {
				// fallback mock: create 9 listings, some SELL orders and some BUY orders
				setListings([
					{ id: 'S1', side: 'SELL', seller: 'HH001', amount_kwh: 5, price_kes: 0.12 },
					{ id: 'S2', side: 'SELL', seller: 'HH002', amount_kwh: 3, price_kes: 0.11 },
					{ id: 'S3', side: 'SELL', seller: 'HH003', amount_kwh: 8, price_kes: 0.09 },
					{ id: 'S4', side: 'SELL', seller: 'HH004', amount_kwh: 1, price_kes: 0.14 },
					{ id: 'B1', side: 'BUY', seller: 'HH101', amount_kwh: 4, price_kes: 0.13 },
					{ id: 'B2', side: 'BUY', seller: 'HH102', amount_kwh: 2, price_kes: 0.16 },
					{ id: 'B3', side: 'BUY', seller: 'HH103', amount_kwh: 6, price_kes: 0.10 },
					{ id: 'S5', side: 'SELL', seller: 'HH005', amount_kwh: 7, price_kes: 0.08 },
					{ id: 'B4', side: 'BUY', seller: 'HH104', amount_kwh: 3, price_kes: 0.12 },
				]);
			});

		// Fetch market-level prediction/guidance from AI via backend (GET with query params)
		api
			.get('/predict/', { params: { household: 'sim-1', live_avg_production: 1.5, live_avg_consumption: 2.0 } })
			.then((r) => setMarketPrediction(r.data || null))
			.catch(() => {
				setMarketPrediction({ summary: 'No prediction available', best_action: 'hold', reason: 'AI service unavailable.' });
			});
	}, []);


	// Helper: validate Kenyan MSISDN in 2547XXXXXXXX format
	const isValidMsisdn = (msisdn: string) => /^2547\d{8}$/.test(msisdn);

	// Start STK push (backend will simulate or call Daraja)
	const startStk = async (listing: any, phone: string) => {
		setLoading(true);
		try {
				phone = phone.replace(/\s+/g, '');
				localStorage.setItem('phone', phone);

			const amountKES = Math.max(1, Math.round((listing.price_kes || 0.1) * listing.amount_kwh));
				const trade_id = `buy-${listing.id}-${Date.now()}`;
				const resp = await api.post('/mpesa/stk_push/', { phone, amount: amountKES, trade_id, listing_id: listing.id });
			const data = resp.data || {};
			// show modal instructing user to enter MPESA PIN (simulated)
				setStkModal({ open: true, checkout_request_id: data.checkout_request_id, amount: data.amount_kes || amountKES, trade_id: data.trade_id || trade_id });
			// Prefer concise backend user message
			const userMsg = data.user_message || data.customer_message || 'Checkout initiated. Enter your M-Pesa PIN.';
			showToast(userMsg, 'info');

				// Begin polling for payment status; stop after ~2 minutes
				const tid = data.trade_id || trade_id;
				const start = Date.now();
				const poll = async () => {
					try {
						const r = await api.get('/mpesa/status/', { params: { trade_id: tid } });
						const status = (r.data && (r.data.status || r.data.payment_status)) || 'unknown';
						if (status === 'confirmed' || status === 'success') {
							setStkModal({ open: false });
							showToast('Payment confirmed. Thank you!', 'success');
							return;
						}
					} catch (_) { /* ignore transient errors */ }
					if (Date.now() - start < 120000) {
						setTimeout(poll, 2500);
					}
				};
				setTimeout(poll, 2500);
		} catch (e: any) {
			const resp = e?.response;
			if (resp && resp.data) {
				const userMsg = resp.data.user_message || resp.data.customer_message;
				const detail = resp.data.error || resp.data?.raw?.errorMessage || resp.data?.raw?.error || resp.data.text;
				const msg = userMsg || detail || 'STK Push failed';
				showToast(`${msg}${resp.status ? ` (status ${resp.status})` : ''}`, 'error');
			} else {
				showToast('Buy failed: ' + String(e?.message || e), 'error');
			}
		} finally {
			setLoading(false);
		}
	};

	// Open phone entry modal for Buy
	const openPhoneModal = (listing: any) => {
      setPhoneModal({ open: true, listing, phone: (localStorage.getItem('phone') || '').trim(), error: '' });
    };

	const confirmPhone = async () => {
      const listing = phoneModal.listing;
      const phone = (phoneModal.phone || '').trim();
      if (!listing) { setPhoneModal({ open:false, phone: phone, listing: undefined }); return; }
      if (!isValidMsisdn(phone)) {
        setPhoneModal((s) => ({ ...s, error: 'Enter a valid number in format 2547XXXXXXXX' }));
        return;
      }
      setPhoneModal({ open: false, listing: undefined, phone: phone });
      await startStk(listing, phone);
    };

	const closeStkModal = () => setStkModal({ open: false });

	const sell = async (listing: any) => {
		// For now we simulate creating a sell order (backend endpoint could be /marketplace/sell/)
		try {
			await api.post('/marketplace/sell/', { listing_id: listing.id, amount_kwh: listing.amount_kwh, price_kes: listing.price_kes });
			showToast('Sell order posted', 'success');
		} catch (e: any) {
			showToast('Sell failed: ' + String(e?.message || e), 'error');
		}
	};

	return (
		<Layout>
			<ToastContainer />
			<div className="p-4">
				<h2 className="text-2xl font-bold">Marketplace</h2>
				<p className="text-muted-foreground">Buy and sell energy tokens. Exporting energy mints tokens (1 kWh → 1 token). Use tokens when you need power, or trade them on the marketplace.</p>

				<CreateSellingForm onListingCreated={() => {
					// Refresh listings after creating new one
					api.get('/marketplace/').then((r) => setListings(r.data.listings || [])).catch(() => {});
				}} />

				<div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
					<div>
						<h3 className="font-semibold mb-2">Sell Orders</h3>
						<div className="overflow-x-auto">
							<table className="w-full table-auto text-sm">
								<thead>
									<tr className="text-left text-xs text-muted-foreground">
										<th className="px-2 py-2">Seller</th>
										<th className="px-2 py-2">Amount (tokens)</th>
										<th className="px-2 py-2">Price (KES)</th>
										<th className="px-2 py-2">Total (KES)</th>
										<th className="px-2 py-2">Action</th>
									</tr>
								</thead>
								<tbody>
									{listings.filter((x) => (x.side || 'SELL') === 'SELL').map((l) => (
										<tr key={l.id} className="border-t">
											<td className="px-2 py-3">{l.seller}</td>
											<td className="px-2 py-3">{l.amount_kwh}</td>
											<td className="px-2 py-3">{l.price_kes}</td>
											<td className="px-2 py-3">{(l.amount_kwh * l.price_kes).toFixed(2)}</td>
											<td className="px-2 py-3"><Button onClick={() => openPhoneModal(l)} disabled={loading}>Buy</Button></td>
										</tr>
									))}
								</tbody>
							</table>
						</div>
					</div>
					<div>
						<h3 className="font-semibold mb-2">Buy Orders</h3>
						<div className="overflow-x-auto">
							<table className="w-full table-auto text-sm">
								<thead>
									<tr className="text-left text-xs text-muted-foreground">
							<th className="px-2 py-2">Buyer</th>
							<th className="px-2 py-2">Amount (tokens)</th>
										<th className="px-2 py-2">Price (KES)</th>
										<th className="px-2 py-2">Total (KES)</th>
										<th className="px-2 py-2">Action</th>
									</tr>
								</thead>
								<tbody>
									{listings.filter((x) => (x.side || 'SELL') === 'BUY').map((l) => (
										<tr key={l.id} className="border-t">
											<td className="px-2 py-3">{l.seller}</td>
											<td className="px-2 py-3">{l.amount_kwh}</td>
											<td className="px-2 py-3">{l.price_kes}</td>
											<td className="px-2 py-3">{(l.amount_kwh * l.price_kes).toFixed(2)}</td>
											<td className="px-2 py-3"><Button variant="outline" onClick={() => sell(l)} disabled={loading}>Sell</Button></td>
										</tr>
									))}
								</tbody>
							</table>
						</div>
					</div>
				</div>

				{/* STK PIN Modal (simple) */}
				{stkModal.open && (
					<div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
						<div className="bg-white p-6 rounded shadow max-w-md w-full">
							<h3 className="text-lg font-semibold">Complete payment</h3>
							<p className="mt-2">An STK Push has been sent to your phone for KES {stkModal.amount} (price for tokens).</p>
							<p className="mt-2 text-sm text-muted-foreground">Please enter your M-Pesa PIN on your phone to complete the token purchase.</p>
							<div className="mt-4 flex justify-end">
								<Button onClick={closeStkModal}>Close</Button>
							</div>
						</div>
					</div>
				)}

				{/* Phone entry modal */}
				{phoneModal.open && (
					<div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
						<div className="bg-white p-6 rounded shadow max-w-md w-full">
							<h3 className="text-lg font-semibold">Enter your M-Pesa number</h3>
							<p className="mt-2 text-sm text-muted-foreground">Format: 2547XXXXXXXX</p>
							<input
								type="tel"
								className="mt-3 w-full p-2 rounded border"
								placeholder="2547XXXXXXXX"
								value={phoneModal.phone}
								onChange={(e) => setPhoneModal((s) => ({ ...s, phone: e.target.value, error: '' }))}
							/>
							{phoneModal.error && <div className="text-sm text-destructive mt-2">{phoneModal.error}</div>}
							<div className="mt-4 flex justify-end gap-2">
								<Button variant="outline" onClick={() => setPhoneModal({ open: false, listing: undefined, phone: phoneModal.phone })}>Cancel</Button>
								<Button onClick={confirmPhone} disabled={loading}>Continue</Button>
							</div>
						</div>
					</div>
				)}

				{/* Market prediction */}
				<div className="mt-6 p-4 border rounded bg-slate-50">
					<h4 className="font-semibold">Market prediction</h4>
					{marketPrediction ? (
						(() => {
							// Normalize prediction object
							const pred = marketPrediction.prediction || marketPrediction;
							const decision = (pred?.decision || pred?.action || marketPrediction.best_action || 'hold').toUpperCase();
							const confidence = pred?.confidence ?? pred?.confidence_score ?? marketPrediction.confidence ?? null;
							const reason = pred?.reason || marketPrediction.reason || pred?.explanation || '';
							const timing = pred?.optimal_timing || pred?.optimal_time || marketPrediction.optimal_timing || '';
							const priceSuggestion = pred?.price_suggestion || pred?.price_per_kwh || marketPrediction.price_suggestion || null;
							const nextPrices = pred?.next_day_prices || marketPrediction.next_day_prices || null;
							return (
								<div className="space-y-2">
									<div className="flex items-center justify-between">
										<div className="text-sm">Decision</div>
										<div className="font-semibold">{decision}</div>
									</div>
									{confidence != null && (
										<div className="text-xs text-muted-foreground">Confidence: {Math.round(Number(confidence))}%</div>
									)}
									{reason && <div className="text-sm mt-1">Why: <span className="text-muted-foreground">{reason}</span></div>}
									{timing && <div className="text-sm mt-1">Best timing: <strong>{timing}</strong></div>}
									{priceSuggestion != null && <div className="text-sm mt-1">Price suggestion: KES {priceSuggestion}</div>}
									{nextPrices && Array.isArray(nextPrices) && (
										<div className="mt-2">
											<div className="text-sm">Next days price forecast:</div>
											<pre className="text-xs p-2 bg-white border rounded">{JSON.stringify(nextPrices, null, 2)}</pre>
										</div>
									)}
								</div>
							);
						})()
					) : (
						<p className="text-sm text-muted-foreground">Loading prediction...</p>
					)}
				</div>
			</div>
		</Layout>
	);
}

function CreateSellingForm({ onListingCreated }: { onListingCreated: () => void }) {
	const [sellAmount, setSellAmount] = useState<number>(1);
	const [sellPrice, setSellPrice] = useState<number>(0.12);
	const [userBalance, setUserBalance] = useState<number>(0);
	const [loading, setLoading] = useState(false);

	// Fetch user's token balance
	React.useEffect(() => {
		api.get('/account/balance/').then((r) => {
			const balance = Number(r.data?.token_balance ?? 0);
			setUserBalance(balance);
		}).catch(() => {
			// Fallback: try to get balance from DOM if available
			const balanceEl = document.getElementById('token-balance');
			if (balanceEl) {
				const balance = parseFloat(balanceEl.textContent || '0');
				setUserBalance(balance);
			}
		});
	}, []);

	const createListing = async () => {
		if (sellAmount <= 0 || sellPrice <= 0) {
			showToast('Please enter valid amount and price', 'error');
			return;
		}
		if (sellAmount > userBalance) {
			showToast(`Insufficient tokens. You have ${userBalance.toFixed(3)} tokens.`, 'error');
			return;
		}

		setLoading(true);
		try {
			const response = await api.post('/marketplace/', {
				amount: sellAmount,
				price_per_token: sellPrice,
				seller: 'You'
			});
			
			showToast(`Successfully listed ${sellAmount} tokens for sale at ${sellPrice} KES each`, 'success');
			setSellAmount(1);
			setSellPrice(0.12);
			onListingCreated();
			
			// Update user balance
			setUserBalance(prev => prev - sellAmount);
		} catch (e: any) {
			const errorMsg = e?.response?.data?.error || e?.message || 'Failed to create listing';
			showToast(`Sell listing failed: ${errorMsg}`, 'error');
		} finally {
			setLoading(false);
		}
	};

	return (
		<div className="mt-6 p-4 border rounded bg-blue-50">
			<h3 className="font-semibold mb-4">🏷️ List Your Tokens for Sale</h3>
			<p className="text-sm text-muted-foreground mb-4">
				You have <strong>{userBalance.toFixed(3)} tokens</strong> available to sell.
			</p>
			
			<div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
				<div>
					<label className="text-sm font-medium block mb-1">Amount (tokens)</label>
					<input
						type="number"
						step="0.1"
						min="0.1"
						max={userBalance}
						value={sellAmount}
						onChange={(e) => setSellAmount(parseFloat(e.target.value) || 0)}
						className="w-full p-2 border rounded"
						placeholder="1.0"
					/>
				</div>
				
				<div>
					<label className="text-sm font-medium block mb-1">Price per Token (KES)</label>
					<input
						type="number"
						step="0.01"
						min="0.01"
						value={sellPrice}
						onChange={(e) => setSellPrice(parseFloat(e.target.value) || 0)}
						className="w-full p-2 border rounded"
						placeholder="0.12"
					/>
				</div>
				
				<div>
					<Button 
						onClick={createListing} 
						disabled={loading || sellAmount <= 0 || sellPrice <= 0 || sellAmount > userBalance}
						className="w-full"
					>
						{loading ? 'Creating...' : `List for ${(sellAmount * sellPrice).toFixed(2)} KES`}
					</Button>
				</div>
			</div>
			
			{sellAmount > 0 && sellPrice > 0 && (
				<div className="mt-3 text-sm text-muted-foreground">
					Total value: <strong>{(sellAmount * sellPrice).toFixed(2)} KES</strong> 
					{sellAmount > userBalance && <span className="text-red-500 ml-2">⚠️ Exceeds available tokens</span>}
				</div>
			)}
		</div>
	);
}
