from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .services import PricingService, MeterService

class MarketStatusView(APIView):
    """
    GET /api/trade/status/
    Used by Frontend to show Red/Green lights.
    """
    def get(self, request):
        return Response(PricingService.get_market_status())

class RecordTradeView(APIView):
    """
    POST /api/trade/record/
    Used by the Python Script (Simulated Meter) to log a sale.
    """
    def post(self, request):
        # In a real app, save to DB. For demo, just echo it back.
        data = request.data
        # Use .get() to avoid errors if keys are missing
        amount = data.get('amount', 0)
        price = data.get('price', 0)
        print(f"💰 LIVE TRADE RECEIVED: {amount}kWh at KES {price}")
        return Response({"status": "Trade Confirmed", "tx_hash": "0x123...abc"})

class RegisterView(APIView):
    """
    POST /api/register/
    Creates a new user for the frontend.
    """
    def post(self, request):
        print("📨 REGISTER REQUEST RECEIVED:", request.data) 

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
        
        print(f"✅ SUCCESS: Created user {username}")
        return Response({'message': 'User registered successfully!'}, status=status.HTTP_201_CREATED)

class MeterUpdateView(APIView):
    """
    POST /api/meter/update/
    Received from Python Script (Wokwi Bridge).
    """
    def post(self, request):
        solar = request.data.get('solar', 0)
        load = request.data.get('load', 0)
        state = MeterService.update_readings(solar, load)
        return Response({"status": "updated", "state": state})

class MeterStatusView(APIView):
    """
    GET /api/meter/status/
    Used by React Dashboard to show the dials.
    """
    def get(self, request):
        return Response(MeterService.get_readings())