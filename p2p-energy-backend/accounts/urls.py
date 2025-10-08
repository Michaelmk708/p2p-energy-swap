# users/urls.py
from django.urls import path
from .views import MeView, RegisterView, DevResetPasswordView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from django.conf import settings

# For local dev, provide non-throttled wrappers for auth endpoints to avoid 429
def _maybe_no_throttle(view_cls):
    if settings.DEBUG:
        @permission_classes([AllowAny])
        @throttle_classes([])
        class _Wrapped(view_cls):
            pass
        return _Wrapped.as_view()
    return view_cls.as_view()

urlpatterns = [
    # JWT token endpoints expected by the frontend (dev: no throttle)
    path("token/", _maybe_no_throttle(TokenObtainPairView), name="token_obtain_pair"),
    path("token/refresh/", _maybe_no_throttle(TokenRefreshView), name="token_refresh"),

    # Auth related endpoints
    path("me/", MeView.as_view(), name="me"),
    path("register/", RegisterView.as_view(), name="register"),
    # Dev-only helper: reset a user password by email (guarded by DEV_ADMIN_SECRET)
    path("dev/reset_password/", DevResetPasswordView.as_view(), name="dev_reset_password"),
]