from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

import json
import os
import time
import requests
from typing import Any, Dict, List, Tuple
from datetime import datetime


# --- Utility helpers ---
def _write_latest(device: str, component: str, payload: Dict[str, Any]) -> None:
	"""Write a small latest snapshot to /tmp for quick demo consumption."""
	try:
		ts = int(time.time())
		payload_with_meta = {
			"device": device,
			"component": component,
			"timestamp": ts,
			"data": payload,
		}
		fname = f"/tmp/p2p_iot_latest_{device}_{component}.json"
		with open(fname, "w") as f:
			json.dump(payload_with_meta, f)
		# simple pointers for convenience
		with open(f"/tmp/p2p_iot_latest_device.txt", "w") as f:
			f.write(device)
		with open(f"/tmp/p2p_iot_latest_component.txt", "w") as f:
			f.write(component)
	except Exception:
		# best-effort only
		pass


# --- Timeseries helpers (simple JSON array per device/component in /tmp) ---
def _ts_file_path(device: str, component: str) -> str:
	safe_dev = device.replace("/", "_")
	safe_comp = component.replace("/", "_")
	return f"/tmp/p2p_iot_ts_{safe_dev}_{safe_comp}.json"


def _append_timeseries_point(device: str, component: str, power_kw: float, ts: float | None = None, cap: int = 3600) -> None:
	"""Append a single timeseries point as {t: epoch_ms, kw: float}. Cap length to 'cap'."""
	try:
		t_ms = int((ts or time.time()) * 1000)
		path = _ts_file_path(device, component)
		data: List[Dict[str, Any]] = []
		if os.path.exists(path):
			try:
				with open(path) as f:
					data = json.load(f) or []
			except Exception:
				data = []
		data.append({"t": t_ms, "kw": float(power_kw)})
		if len(data) > cap:
			data = data[-cap:]
		with open(path, "w") as f:
			json.dump(data, f)
	except Exception:
		pass


def _read_timeseries(device: str, component: str, since_ms: int | None = None, limit: int | None = None) -> List[Dict[str, Any]]:
	path = _ts_file_path(device, component)
	try:
		with open(path) as f:
			arr: List[Dict[str, Any]] = json.load(f) or []
		if since_ms is not None:
			arr = [p for p in arr if int(p.get("t", 0)) >= since_ms]
		if limit is not None and len(arr) > limit:
			arr = arr[-limit:]
		return arr
	except Exception:
		return []


def _daily_key(ts: float | None = None) -> str:
	dt = datetime.fromtimestamp(ts or time.time())
	return dt.strftime("%Y-%m-%d")


def _daily_path(device: str, component: str, day: str | None = None) -> str:
	d = day or _daily_key()
	safe_dev = device.replace("/", "_")
	safe_comp = component.replace("/", "_")
	return f"/tmp/p2p_iot_daily_{safe_dev}_{safe_comp}_{d}.json"


def _read_daily(device: str, component: str, day: str | None = None) -> Dict[str, Any]:
	path = _daily_path(device, component, day)
	if os.path.exists(path):
		try:
			with open(path) as f:
				return json.load(f)
		except Exception:
			pass
	return {"device": device, "component": component, "date": (day or _daily_key()), "energy_kwh": 0.0}


def _write_daily(device: str, component: str, energy_kwh: float, day: str | None = None) -> Dict[str, Any]:
	obj = {"device": device, "component": component, "date": (day or _daily_key()), "energy_kwh": float(max(0.0, energy_kwh))}
	path = _daily_path(device, component, obj["date"])
	try:
		with open(path, "w") as f:
			json.dump(obj, f)
	except Exception:
		pass
	return obj


@csrf_exempt
@api_view(["POST"]) 
@permission_classes([AllowAny])
def iotcentral_telemetry_bridge(request):
	"""
	Accept minimal Wokwi-style telemetry and acknowledge.

	Supported payloads:
	- {"device":"household-1","pv_power":<float>,"load_power":<float>}
	- [{"device":"household-1","component":"pv_array","measurements":{"power":<float>}}, ...]
	"""
	# Parse JSON body very defensively and capture the raw payload for debugging
	try:
		body = request.body.decode("utf-8") if request.body else "{}"
		data = json.loads(body)
		# write last good parse for troubleshooting
		try:
			with open("/tmp/p2p_iot_last_body.txt", "w") as f:
				f.write(body)
			with open("/tmp/p2p_iot_last_parsed.json", "w") as f:
				json.dump(data, f)
		except Exception:
			pass
	except json.JSONDecodeError:
		# dump the raw body so we can inspect malformed inputs
		try:
			with open("/tmp/p2p_iot_last_body.txt", "w") as f:
				f.write(request.body.decode(errors="ignore") if request.body else "<empty>")
		except Exception:
			pass
		return Response({"ok": False, "error": "invalid_json"}, status=status.HTTP_400_BAD_REQUEST)

	count = 0
	if isinstance(data, dict) and "device" in data:
		device = str(data.get("device"))
		# normalize pv and load (simple dict shape)
		pv = data.get("pv_power")
		load = data.get("load_power")
		if isinstance(pv, (int, float)):
			kw = float(pv)
			_write_latest(device, "pv_array", {"power": kw})
			_append_timeseries_point(device, "pv_array", kw)
			count += 1
		if isinstance(load, (int, float)):
			kw = float(load)
			_write_latest(device, "house_load", {"power": kw})
			_append_timeseries_point(device, "house_load", kw)
			count += 1
		# accept extended dict shape: {device, component, data:{power|watts|w}}
		component = data.get("component")
		data_block = data.get("data") if isinstance(data.get("data"), dict) else None
		if component and isinstance(component, str) and data_block is not None:
			kw_val = None
			val = data_block.get("power") or data_block.get("kW") or data_block.get("kw")
			if isinstance(val, (int, float)):
				kw_val = float(val)
			else:
				w = data_block.get("watts") or data_block.get("w")
				if isinstance(w, (int, float)):
					kw_val = float(w) / 1000.0
			# always write latest snapshot of provided measurements
			try:
				_write_latest(device, component, data_block)
				count += 1
			except Exception:
				pass
			if isinstance(kw_val, float):
				_append_timeseries_point(device, component, kw_val)
	elif isinstance(data, list):
		for item in data:
			try:
				device = str(item.get("device"))
				component = str(item.get("component"))
				measurements = item.get("measurements") or {}
				if device and component and isinstance(measurements, dict):
					# derive power in kW from common fields
					kw = None
					val = measurements.get("power")
					if isinstance(val, (int, float)):
						kw = float(val)
					else:
						w = measurements.get("watts") or measurements.get("w")
						if isinstance(w, (int, float)):
							kw = float(w) / 1000.0
					# write latest always; append timeseries if we have a numeric kw
					_write_latest(device, component, measurements)
					if isinstance(kw, float):
						_append_timeseries_point(device, component, kw)
					count += 1
			except Exception:
				continue
	else:
		return Response({"ok": False, "error": "unsupported_payload"}, status=status.HTTP_400_BAD_REQUEST)

	return Response({"ok": True, "count": count})


# --- AI Prediction Service Integration ---
@api_view(["GET", "POST"]) 
@permission_classes([AllowAny])
def predict(request):
	try:
		import requests
		
		# Forward all query parameters to AI service
		params = dict(request.GET.items())
		
		# Add default household if not specified
		if 'household' not in params:
			params['household'] = 'sim-1'
		
		# Forward request to AI service on port 5000
		ai_response = requests.get('http://localhost:5000/predict', params=params, timeout=30)
		
		if ai_response.status_code == 200:
			return Response(ai_response.json())
		else:
			return Response({
				"status": "error", 
				"message": f"AI service returned {ai_response.status_code}",
				"endpoint": "predict"
			}, status=ai_response.status_code)
			
	except requests.exceptions.RequestException as e:
		return Response({
			"status": "error",
			"message": f"Failed to connect to AI service: {str(e)}",
			"endpoint": "predict"
		}, status=502)
	except Exception as e:
		return Response({
			"status": "error", 
			"message": f"Internal error: {str(e)}",
			"endpoint": "predict"
		}, status=500)


@api_view(["GET", "POST"]) 
@permission_classes([AllowAny])
def execute_trade(request):
	return Response({"status": "ok", "endpoint": "execute_trade"})


@api_view(["GET", "POST"]) 
@permission_classes([AllowAny])
def mint_energy(request):
	"""Mint energy tokens through blockchain service"""
	if request.method == "GET":
		return Response({"status": "ok", "endpoint": "mint_energy"})
	
	# POST request - mint tokens
	try:
		data = request.data
		household_id = data.get('household_id', 'default')
		amount_kwh = float(data.get('amount_kwh', 0))
		reason = data.get('reason', 'Energy export')
		
		if amount_kwh <= 0:
			return Response({"error": "Invalid amount"}, status=400)
		
		# Call blockchain service
		import requests
		blockchain_url = "http://localhost:7000/mint_energy"
		api_key = "test-blockchain-apikey"  # Default API key
		
		mint_request = {
			"household_id": household_id,
			"amount_kwh": amount_kwh,
			"reason": reason
		}
		
		response = requests.post(
			blockchain_url,
			json=mint_request,
			headers={"X-API-Key": api_key},
			timeout=10
		)
		
		if response.status_code == 200:
			blockchain_data = response.json()
			
			# Update local token balance
			balance_file = "/tmp/token_balance.json"
			try:
				if os.path.exists(balance_file):
					with open(balance_file, 'r') as f:
						data = json.load(f)
					current_balance = data.get("balance", 0)
				else:
					current_balance = 0
				
				new_balance = current_balance + amount_kwh
				with open(balance_file, 'w') as f:
					json.dump({"balance": new_balance, "last_updated": time.time()}, f)
			except Exception as e:
				print(f"Error updating balance: {e}")
			
			# Record transaction
			_record_transaction(
				"mint",
				amount_kwh,
				description=f"Minted {amount_kwh} tokens from energy export",
				tx_hash=blockchain_data.get("tx_hash"),
				household_id=household_id,
				reason=reason
			)
			
			return Response({
				"status": "success",
				"tokens_minted": amount_kwh,  # 1 token per 1 kWh
				"tx_hash": blockchain_data.get("tx_hash"),
				"household_id": household_id,
				"amount_kwh": amount_kwh,
				"user_message": f"Successfully minted {amount_kwh} energy tokens!"
			})
		else:
			return Response({
				"error": "Blockchain service error",
				"status_code": response.status_code,
				"user_message": "Token minting failed - blockchain service unavailable"
			}, status=500)
			
	except Exception as e:
		return Response({
			"error": str(e),
			"user_message": "Token minting failed - internal error"
		}, status=500)


@api_view(["GET", "POST"]) 
@permission_classes([AllowAny])
def marketplace(request):
	"""Token marketplace - list and sell tokens"""
	
	if request.method == "GET":
		# Get current listings and user balance
		try:
			# Read token balance
			balance_file = "/tmp/token_balance.json"
			user_balance = 0
			if os.path.exists(balance_file):
				with open(balance_file, 'r') as f:
					data = json.load(f)
				user_balance = data.get("balance", 0)
			
			# Read marketplace listings
			listings_file = "/tmp/marketplace_listings.json"
			listings = []
			if os.path.exists(listings_file):
				with open(listings_file, 'r') as f:
					listings = json.load(f)
			
			# Add sample users if no listings exist
			if not listings:
				sample_listings = [
					{
						"id": 1001,
						"seller": "SolarMax_House",
						"amount": 2.3,
						"price_per_token": 0.12,
						"total_price": 2.3 * 0.12,
						"created_at": time.time() - 3600,
						"status": "active",
						"note": "Excess solar from 5kW system"
					},
					{
						"id": 1002,
						"seller": "GreenEnergy_Co",
						"amount": 5.0,
						"price_per_token": 0.18,
						"total_price": 5.0 * 0.18,
						"created_at": time.time() - 1800,
						"status": "active",
						"note": "Bulk tokens available"
					},
					{
						"id": 1003,
						"seller": "EcoHome_42",
						"amount": 1.1,
						"price_per_token": 0.14,
						"total_price": 1.1 * 0.14,
						"created_at": time.time() - 900,
						"status": "active",
						"note": "Battery overflow export"
					}
				]
				listings = sample_listings
				with open(listings_file, 'w') as f:
					json.dump(listings, f)
			
			return Response({
				"status": "ok", 
				"user_balance": user_balance,
				"listings": listings,
				"can_list": user_balance > 0,
				"market_stats": {
					"total_listings": len(listings),
					"total_tokens_available": sum(l["amount"] for l in listings),
					"avg_price": sum(l["price_per_token"] for l in listings) / len(listings) if listings else 0
				}
			})
		except Exception as e:
			return Response({"error": str(e)}, status=500)
	
	elif request.method == "POST":
		# Create new listing
		try:
			data = request.data
			amount = float(data.get('amount', 0))
			price_per_token = float(data.get('price_per_token', 1.0))
			
			if amount <= 0:
				return Response({"error": "Invalid amount"}, status=400)
			
			# Check user has enough tokens
			balance_file = "/tmp/token_balance.json"
			user_balance = 0
			if os.path.exists(balance_file):
				with open(balance_file, 'r') as f:
					balance_data = json.load(f)
				user_balance = balance_data.get("balance", 0)
			
			if amount > user_balance:
				return Response({"error": "Insufficient tokens"}, status=400)
			
			# Create listing
			listing = {
				"id": int(time.time() * 1000),  # Simple ID
				"seller": data.get('seller', 'anonymous'),
				"amount": amount,
				"price_per_token": price_per_token,
				"total_price": amount * price_per_token,
				"created_at": time.time(),
				"status": "active"
			}
			
			# Save listing
			listings_file = "/tmp/marketplace_listings.json"
			listings = []
			if os.path.exists(listings_file):
				with open(listings_file, 'r') as f:
					listings = json.load(f)
			
			listings.append(listing)
			with open(listings_file, 'w') as f:
				json.dump(listings, f)
			
			# Deduct tokens from balance (hold in escrow)
			new_balance = user_balance - amount
			with open(balance_file, 'w') as f:
				json.dump({"balance": new_balance, "last_updated": time.time()}, f)
			
			# Record transaction
			_record_transaction(
				"sell",
				amount,
				price_per_token=price_per_token,
				total_cost=amount * price_per_token,
				listing_id=listing["id"],
				description=f"Listed {amount} tokens for sale at ${price_per_token:.2f} each"
			)
			
			return Response({
				"status": "success",
				"listing": listing,
				"new_balance": new_balance,
				"message": f"Listed {amount} tokens for sale at {price_per_token} each"
			})
			
		except Exception as e:
			return Response({"error": str(e)}, status=500)


@api_view(["POST"]) 
@permission_classes([AllowAny])
def buy_listing(request):
	"""Buy tokens from marketplace listing"""
	try:
		data = request.data
		listing_id = int(data.get('listing_id', 0))
		amount_to_buy = float(data.get('amount', 0))
		
		if amount_to_buy <= 0:
			return Response({"error": "Invalid amount"}, status=400)
		
		# Read current listings
		listings_file = "/tmp/marketplace_listings.json"
		listings = []
		if os.path.exists(listings_file):
			with open(listings_file, 'r') as f:
				listings = json.load(f)
		
		# Find the listing
		listing = None
		listing_index = None
		for i, l in enumerate(listings):
			if l["id"] == listing_id:
				listing = l
				listing_index = i
				break
		
		if not listing:
			return Response({"error": "Listing not found"}, status=404)
		
		if amount_to_buy > listing["amount"]:
			return Response({"error": "Not enough tokens available"}, status=400)
		
		# Calculate cost
		total_cost = amount_to_buy * listing["price_per_token"]
		
		# Update listing (reduce amount or remove if fully bought)
		if amount_to_buy == listing["amount"]:
			listings.pop(listing_index)
		else:
			listings[listing_index]["amount"] -= amount_to_buy
			listings[listing_index]["total_price"] = listings[listing_index]["amount"] * listings[listing_index]["price_per_token"]
		
		# Save updated listings
		with open(listings_file, 'w') as f:
			json.dump(listings, f)
		
		# Update buyer's token balance
		balance_file = "/tmp/token_balance.json"
		current_balance = 0
		if os.path.exists(balance_file):
			with open(balance_file, 'r') as f:
				balance_data = json.load(f)
			current_balance = balance_data.get("balance", 0)
		
		new_balance = current_balance + amount_to_buy
		with open(balance_file, 'w') as f:
			json.dump({"balance": new_balance, "last_updated": time.time()}, f)
		
		# Record transaction
		_record_transaction(
			"buy",
			amount_to_buy,
			seller=listing["seller"],
			price_per_token=listing["price_per_token"],
			total_cost=total_cost,
			description=f"Bought {amount_to_buy} tokens from {listing['seller']}"
		)
		
		return Response({
			"status": "success",
			"tokens_purchased": amount_to_buy,
			"total_cost": total_cost,
			"seller": listing["seller"],
			"new_balance": new_balance,
			"message": f"Purchased {amount_to_buy} tokens from {listing['seller']} for ${total_cost:.2f}"
		})
		
	except Exception as e:
		return Response({"error": str(e)}, status=500)


@api_view(["GET"]) 
@permission_classes([AllowAny])
def account_balance(request):
	"""Get account token balance"""
	try:
		# Simple file-based token storage for demo
		balance_file = "/tmp/token_balance.json"
		
		if os.path.exists(balance_file):
			with open(balance_file, 'r') as f:
				data = json.load(f)
				balance = data.get("balance", 0)
		else:
			balance = 0
			
		return Response({
			"status": "ok", 
			"token_balance": balance,
			"balance": balance  # Legacy field
		})
	except Exception as e:
		return Response({"status": "ok", "token_balance": 0, "balance": 0})


@api_view(["POST"]) 
@permission_classes([AllowAny])
def mpesa_stk_push(request):
	return Response({"status": "ok", "endpoint": "mpesa_stk_push"})


@api_view(["POST"]) 
@permission_classes([AllowAny])
def mpesa_callback(request):
	return Response({"status": "ok", "endpoint": "mpesa_callback"})


@api_view(["GET"]) 
@permission_classes([AllowAny])
def mpesa_status(request):
	return Response({"status": "ok", "endpoint": "mpesa_status"})


@api_view(["POST"]) 
@permission_classes([AllowAny])
def iotcentral_ingest(request):
	return Response({"status": "ok", "endpoint": "iotcentral_ingest"})


@api_view(["GET"]) 
@permission_classes([AllowAny])
def iotcentral_latest(request):
	device = request.GET.get("device", "household-1")
	component = request.GET.get("component", "pv_array")
	fname = f"/tmp/p2p_iot_latest_{device}_{component}.json"
	if os.path.exists(fname):
		try:
			with open(fname) as f:
				data = json.load(f)
			return Response(data)
		except Exception:
			pass
	return Response({"device": device, "component": component, "timestamp": int(time.time()), "data": {}}, status=200)


@api_view(["GET"]) 
@permission_classes([AllowAny])
def iotcentral_last_seen(request):
	"""Return the most recently seen device and component identifiers (best-effort).

	Telemetry bridge writes pointer files in /tmp on every accepted packet. This endpoint
	surfaces those so the frontend can auto-select the correct device/component.
	"""
	device = None
	component = None
	try:
		p = "/tmp/p2p_iot_latest_device.txt"
		if os.path.exists(p):
			with open(p) as f:
				device = f.read().strip() or None
	except Exception:
		pass
	try:
		p = "/tmp/p2p_iot_latest_component.txt"
		if os.path.exists(p):
			with open(p) as f:
				component = f.read().strip() or None
	except Exception:
		pass
	return Response({"device": device, "component": component})


@api_view(["GET"]) 
@permission_classes([AllowAny])
def iotcentral_simulate(request):
	"""Simulate a latest reading for quick UI nudges.

	GET params: device, component, power (float kW)
	Writes to the 'latest' snapshot and returns it.
	"""
	device = request.GET.get("device", "sim-1")
	component = request.GET.get("component", "pv_array")
	try:
		power = float(request.GET.get("power", "1.0"))
	except Exception:
		power = 1.0
	_write_latest(device, component, {"power": power})
	_append_timeseries_point(device, component, float(power))
	return Response({
		"device": device,
		"component": component,
		"latest": {
			"timestamp": int(time.time()),
			"data": {"power": power},
		},
	})


@api_view(["GET"]) 
@permission_classes([AllowAny])
def iotcentral_daily_exported(request):
	device = request.GET.get("device", "household-1")
	component = request.GET.get("component", "grid_export")
	obj = _read_daily(device, component)
	# normalize key name for frontend
	return Response({"device": obj["device"], "component": obj["component"], "date": obj["date"], "energy_kwh": obj["energy_kwh"]})


@api_view(["POST"]) 
@permission_classes([AllowAny])
def iotcentral_increment_energy(request):
	"""Increment daily exported energy counter.

	Body JSON: { device, component, kwh }
	"""
	try:
		data = json.loads(request.body.decode("utf-8") or "{}")
	except Exception:
		data = {}
	device = str(data.get("device") or request.GET.get("device") or "household-1")
	component = str(data.get("component") or request.GET.get("component") or "grid_export")
	try:
		kwh = float(data.get("kwh") or data.get("energy_kwh") or 0)
	except Exception:
		kwh = 0.0
	current = _read_daily(device, component)
	new_total = float(current.get("energy_kwh", 0.0)) + max(0.0, kwh)
	obj = _write_daily(device, component, new_total)
	return Response({"ok": True, "device": obj["device"], "component": obj["component"], "date": obj["date"], "energy_kwh": obj["energy_kwh"]})


@api_view(["GET"]) 
@permission_classes([AllowAny])
def iotcentral_timeseries(request):
	"""Return recent timeseries for one or more components.

	Query params:
	  - device: required
	  - components: comma-separated list (default: pv_array,house_load)
	  - minutes: window size in minutes (default: 30)
	  - limit: max points per component (default: 600)
	Response:
	  { "series": { "pv_array": [{t,kw},...], "house_load": [{t,kw},...] } }
	"""
	device = request.GET.get("device") or "sim-1"
	comps = (request.GET.get("components") or "pv_array,house_load").split(",")
	comps = [c.strip() for c in comps if c.strip()]
	try:
		minutes = int(request.GET.get("minutes", "30"))
	except Exception:
		minutes = 30
	try:
		limit = int(request.GET.get("limit", "600"))
	except Exception:
		limit = 600
	since_ms = int((time.time() - max(1, minutes) * 60) * 1000)

	out: Dict[str, List[Dict[str, Any]]] = {}
	for c in comps:
		out[c] = _read_timeseries(device, c, since_ms=since_ms, limit=limit)

	return Response({"device": device, "series": out})


@api_view(["GET"]) 
@permission_classes([AllowAny])
def iotcentral_surplus_state(request):
	return Response({"status": "ok", "endpoint": "iotcentral_surplus_state"})


@api_view(["POST"]) 
@permission_classes([AllowAny])
def devices_claim(request):
	return Response({"status": "ok", "endpoint": "devices_claim"})


@api_view(["GET"]) 
@permission_classes([AllowAny])
def transactions_history(request):
	"""Get transaction history"""
	try:
		# Read transaction history from file
		transactions_file = "/tmp/transaction_history.json"
		transactions = []
		
		if os.path.exists(transactions_file):
			with open(transactions_file, 'r') as f:
				transactions = json.load(f)
		
		# Sort by timestamp (newest first)
		transactions.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
		
		# Calculate summary stats
		token_mints = [t for t in transactions if t.get('type') == 'mint']
		marketplace_buys = [t for t in transactions if t.get('type') == 'buy']
		marketplace_sells = [t for t in transactions if t.get('type') == 'sell']
		
		total_minted = sum(t.get('amount', 0) for t in token_mints)
		total_bought = sum(t.get('amount', 0) for t in marketplace_buys)
		total_sold = sum(t.get('amount', 0) for t in marketplace_sells)
		total_spent = sum(t.get('total_cost', 0) for t in marketplace_buys)
		total_earned = sum(t.get('total_cost', 0) for t in marketplace_sells)
		
		return Response({
			"status": "success",
			"transactions": transactions,
			"summary": {
				"total_minted": total_minted,
				"total_bought": total_bought,
				"total_sold": total_sold,
				"total_spent": total_spent,
				"total_earned": total_earned,
				"transaction_count": len(transactions)
			}
		})
		
	except Exception as e:
		return Response({
			"error": str(e),
			"transactions": [],
			"summary": {
				"total_minted": 0,
				"total_bought": 0,
				"total_sold": 0,
				"total_spent": 0,
				"total_earned": 0,
				"transaction_count": 0
			}
		}, status=500)


def _record_transaction(tx_type: str, amount: float, **kwargs):
	"""Helper to record transaction in history file"""
	try:
		transactions_file = "/tmp/transaction_history.json"
		transactions = []
		
		if os.path.exists(transactions_file):
			with open(transactions_file, 'r') as f:
				transactions = json.load(f)
		
		# Create transaction record
		transaction = {
			"id": f"TX{int(time.time()*1000)}",
			"type": tx_type,
			"amount": amount,
			"timestamp": time.time(),
			"date": datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %H:%M:%S"),
			"status": "completed",
			**kwargs
		}
		
		transactions.append(transaction)
		
		# Keep only last 100 transactions
		if len(transactions) > 100:
			transactions = transactions[-100:]
		
		with open(transactions_file, 'w') as f:
			json.dump(transactions, f)
			
	except Exception as e:
		print(f"Error recording transaction: {e}")


@api_view(["GET"]) 
@permission_classes([AllowAny])
def devices_mine(request):
	return Response({"status": "ok", "devices": []})


@api_view(["GET", "POST"]) 
@permission_classes([AllowAny])
def sim_set_targets(request):
	return Response({"status": "ok", "endpoint": "sim_set_targets"})


@api_view(["GET"]) 
@permission_classes([AllowAny])
def sim_get_targets(request):
	return Response({"status": "ok", "endpoint": "sim_get_targets"})

