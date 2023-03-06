from django.core.management.base import BaseCommand
from django.conf import settings

from main.models import Drone


class Command(BaseCommand):
    help = 'Check drones battery'

    def handle(self, *args, **options):
        # Here we can send a notification to users by an email, sms, a whatsapp message, slack, telegram, etc.
        # For now is only a console output
        for drone in Drone.objects.all():
            if drone.battery_capacity < settings.DRON_BATERRY_THRESHOLD:
                self.stdout.write(self.style.WARNING(f'Drone {drone.serial_number} has low battery'))
            elif drone.battery_capacity < (settings.DRON_BATERRY_THRESHOLD // 3):
                self.stdout.write(self.style.ERROR(f'Drone {drone.serial_number} has critical battery'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Drone {drone.serial_number} has enough battery to fly'))
