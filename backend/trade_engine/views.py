import json
import os
import time
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .services import PricingService, MeterService

# --- MODERN WEB3 IMPORTS ---
from solana.rpc.api import Client
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.instruction import Instruction
from solders.message import MessageV0
from solders.transaction import VersionedTransaction

# --- GLOBALS ---
# Prevent spamming the blockchain (Wait 15 seconds between trades)
LAST_TRADE_TIME = 0
TRADE_COOLDOWN = 15 

class MarketStatusView(APIView):
    def get(self, request):
        return Response(PricingService.get_market_status())

class MeterUpdateView(APIView):
    """
    POST /api/meter/update/
    Receives telemetry from Wokwi ESP32 via Wi-Fi. 
    Acts as the Web3 Hardware Oracle to trigger Solana trades automatically.
    """
    def post(self, request):
        global LAST_TRADE_TIME
        
        # 1. Safely extract data from the Wokwi ESP32
        solar = float(request.data.get('solar', 0))
        load = float(request.data.get('load', 0))
        seller = "Estate_House_A"
        
        # 2. Update React Dashboard Telemetry (This makes the dials move)
        state = MeterService.update_readings(solar, load)
        
        # 3. THE HARDWARE ORACLE LOGIC (Web3 Settlement)
        if solar > load:
            current_time = time.time()
            # Check cooldown so we don't drain devnet SOL
            if current_time - LAST_TRADE_TIME > TRADE_COOLDOWN:
                LAST_TRADE_TIME = current_time
                surplus = round(solar - load, 2)
                price = round(surplus * 15, 2)
                
                print(f"\n⚠️  [SOLAR GLUT DETECTED] {surplus}kW excess verified by Wokwi IoT.")
                print(f"🔗  [WEB3] Triggering Solana Settlement...")
                
                # --- SOLANA BLOCKCHAIN LOGIC ---
                try:
                    # Load Wallet
                    wallet_path = os.path.expanduser("~/.config/solana/id.json")
                    with open(wallet_path, 'r') as f:
                        keypair_data = json.load(f)
                    payer = Keypair.from_bytes(bytes(keypair_data))

                    # Connect to Devnet
                    client = Client("https://api.devnet.solana.com")
                    live_blockhash = client.get_latest_blockhash().value.blockhash
                    
                    # Create Immutable Ledger Entry
                    MEMO_PROGRAM_ID = Pubkey.from_string("MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr")
                    trade_details = f"[P2P Energy Swap] ORACLE VERIFIED: {surplus} kWh delivered from {seller}. Value: KES {price}."
                    
                    # Build and Sign Transaction
                    ix = Instruction(program_id=MEMO_PROGRAM_ID, accounts=[], data=trade_details.encode("utf-8"))
                    msg = MessageV0.try_compile(
                        payer=payer.pubkey(), 
                        instructions=[ix], 
                        address_lookup_table_accounts=[], 
                        recent_blockhash=live_blockhash
                    )
                    tx = VersionedTransaction(msg, [payer])

                    # Broadcast to Blockchain
                    result = client.send_transaction(tx)
                    tx_hash = str(result.value)
                    print(f"✅  [SOLANA DEVNET] Trade Anchored! TxHash: {tx_hash}\n")
                    
                except Exception as e:
                    print(f"❌  [WEB3 ERROR] Blockchain settlement failed: {e}")

        # Always return the updated state to the React Dashboard
        return Response({"status": "updated", "state": state})

class RecordTradeView(APIView):
    """
    POST /api/trade/record/
    Legacy endpoint. Left here so frontend API calls don't crash.
    """
    def post(self, request):
        return Response({
            "status": "Handled automatically by MeterUpdateView now",
            "message": "Check the backend terminal for live Solana TxHashes"
        })

class RegisterView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email', '')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')

        if not username or not password:
            return Response({'error': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already taken.'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name)
        return Response({'message': 'User registered successfully!'}, status=status.HTTP_201_CREATED)

class MeterStatusView(APIView):
    def get(self, request):
        return Response(MeterService.get_readings())