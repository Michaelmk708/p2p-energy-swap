from django.db import models
from django.utils import timezone
from django.conf import settings


class Balance(models.Model):
    """Per-household token balance (PoC until full migration)."""
    household_id = models.CharField(max_length=128, unique=True)
    token_balance = models.DecimalField(max_digits=20, decimal_places=6, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.household_id}: {self.token_balance}"


class IdempotentResponse(models.Model):
    """Store idempotent responses for buy/listing operations."""
    key = models.CharField(max_length=128, unique=True)
    response = models.JSONField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Idemp {self.key} @ {self.created_at.isoformat()}"


class Device(models.Model):
    """Persist mapping of IoT Central device → owning user and target wallet.
    Optional component names help classification and daily counters.
    """
    device_id = models.CharField(max_length=128, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="devices")
    wallet_address = models.CharField(max_length=128, help_text="Target SPL wallet (base58) for mints")
    pv_component = models.CharField(max_length=128, blank=True, default="")
    load_component = models.CharField(max_length=128, blank=True, default="")
    export_component = models.CharField(max_length=128, blank=True, default="export")
    time_drift_sec = models.IntegerField(default=120, help_text="Allowed clock skew in seconds")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Device({self.device_id}→{self.user_id})"
