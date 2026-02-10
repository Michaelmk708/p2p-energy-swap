from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
# IMPORT ALL VIEWS HERE
from trade_engine.views import (
    MarketStatusView, 
    RecordTradeView, 
    RegisterView, 
    MeterUpdateView, 
    MeterStatusView
)

# --- Quick "Me" View for User Profile ---
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "id": request.user.id,
            "username": request.user.username,
            "email": request.user.email,
            "first_name": "Michael",
            "last_name": "Kinuthia",
            "token_balance": 450.00
        })

urlpatterns = [
    path('admin/', admin.site.urls),

    # --- AUTH ENDPOINTS ---
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/me/', UserProfileView.as_view(), name='user_profile'),
    path('api/register/', RegisterView.as_view(), name='register'),

    # --- TRADING & METER ENDPOINTS ---
    path('api/trade/status/', MarketStatusView.as_view()),
    path('api/trade/record/', RecordTradeView.as_view()),
    
    # NEW METER URLS
    path('api/meter/update/', MeterUpdateView.as_view()),
    path('api/meter/status/', MeterStatusView.as_view()),
]