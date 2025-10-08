from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from trading.models import Device, Balance


class Command(BaseCommand):
    help = "Assign an IoT Central device to an existing user (by email or username)."

    def add_arguments(self, parser):
        parser.add_argument("--device", required=True, help="IoT Central device id, e.g. sim-1")
        parser.add_argument("--user", required=True, help="User email or username to assign the device to")
        parser.add_argument("--wallet", default="", help="Optional wallet address to set")
        parser.add_argument("--pv", default="pv_array", help="PV component name")
        parser.add_argument("--load", default="house_load", help="Load component name")
        parser.add_argument("--export", default="grid_export", help="Export component name")

    def handle(self, *args, **opts):
        User = get_user_model()
        ident = opts["user"]
        # Try find by email first
        u = User.objects.filter(email=ident).first()
        if not u:
            u = User.objects.filter(username=ident).first()
        if not u:
            raise CommandError(f"User not found by email or username: {ident}")

        dev_id = opts["device"]
        obj, created = Device.objects.update_or_create(
            device_id=dev_id,
            defaults={
                "user": u,
                "wallet_address": opts["wallet"],
                "pv_component": opts["pv"],
                "load_component": opts["load"],
                "export_component": opts["export"],
            },
        )
        Balance.objects.get_or_create(household_id=u.email)
        self.stdout.write(self.style.SUCCESS(
            f"Assigned {dev_id} to {u.email} (created={created})"
        ))
