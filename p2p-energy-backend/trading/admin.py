from django.contrib import admin
from .models import Device, Balance, IdempotentResponse


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ("device_id", "user", "wallet_address", "pv_component", "load_component", "export_component", "time_drift_sec")
    search_fields = ("device_id", "user__email", "wallet_address", "pv_component", "load_component", "export_component")
    list_filter = ("time_drift_sec",)


@admin.register(Balance)
class BalanceAdmin(admin.ModelAdmin):
    list_display = ("household_id", "token_balance", "updated_at")
    search_fields = ("household_id",)


@admin.register(IdempotentResponse)
class IdempotentResponseAdmin(admin.ModelAdmin):
    list_display = ("key", "created_at")
    search_fields = ("key",)