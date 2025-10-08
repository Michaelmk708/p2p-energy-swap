# users/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics, status
from django.contrib.auth import get_user_model
from django.conf import settings
import os
from .serializers import UserSerializer, RegisterSerializer


class MeView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class RegisterView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


class DevResetPasswordView(APIView):
    """Dev-only endpoint to reset a user's password by email.

    Protects with a shared secret header: X-Dev-Secret must match DEV_ADMIN_SECRET env var.
    This should NEVER be enabled in production. Intended for local demos only.
    """

    permission_classes = (AllowAny,)

    def post(self, request):
        # Verify shared secret
        secret = request.headers.get("X-Dev-Secret", "").strip()
        expected = os.getenv("DEV_ADMIN_SECRET", "") or getattr(settings, "DEV_ADMIN_SECRET", "")
        if not expected or secret != expected:
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        email = (request.data or {}).get("email", "").strip().lower()
        password = (request.data or {}).get("password", "")
        if not email or not password:
            return Response({"detail": "email and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        User = get_user_model()
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        user.set_password(password)
        user.save(update_fields=["password"]) 
        return Response({"ok": True, "message": f"Password updated for {email}"})