from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from trading.models import Device, Balance


class Command(BaseCommand):
    help = "Bootstrap two demo households with users, wallets, and IoT Central device mappings"

    def add_arguments(self, parser):
        parser.add_argument("--device-a", default="house-1", help="IoT Central device id for Household A")
        parser.add_argument("--device-b", default="house-2", help="IoT Central device id for Household B")
        parser.add_argument("--wallet-a", default="HHAWallet11111111111111111111111111111111", help="SPL wallet for Household A")
        parser.add_argument("--wallet-b", default="HHBWallet22222222222222222222222222222222", help="SPL wallet for Household B")
        parser.add_argument("--pv", default="pv_array", help="PV component name")
        parser.add_argument("--load", default="house_load", help="Load component name")
        parser.add_argument("--export", default="grid_export", help="Export component name")

    def handle(self, *args, **opts):
        User = get_user_model()
        # Create users
        a, _ = User.objects.get_or_create(email="household.a@example.com", defaults={"username": "household.a"})
        if not a.has_usable_password():
            a.set_password("changemeA!")
            a.save()
        b, _ = User.objects.get_or_create(email="household.b@example.com", defaults={"username": "household.b"})
        if not b.has_usable_password():
            b.set_password("changemeB!")
            b.save()

        # Ensure balances exist for visibility
        Balance.objects.get_or_create(household_id=a.email)
        Balance.objects.get_or_create(household_id=b.email)

        # Create device mappings
        dev_a, _ = Device.objects.update_or_create(
            device_id=opts["device_a"],
            defaults={
                "user": a,
                "wallet_address": opts["wallet_a"],
                "pv_component": opts["pv"],
                "load_component": opts["load"],
                "export_component": opts["export"],
            },
        )
        dev_b, _ = Device.objects.update_or_create(
            device_id=opts["device_b"],
            defaults={
                "user": b,
                "wallet_address": opts["wallet_b"],
                "pv_component": opts["pv"],
                "load_component": opts["load"],
                "export_component": opts["export"],
            },
        )

        self.stdout.write(self.style.SUCCESS(
            f"Bootstrapped devices: {dev_a.device_id}→{a.email}, {dev_b.device_id}→{b.email}"
        ))
