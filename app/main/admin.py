from django.contrib import admin
from .models import Drone, Medication


class InlineMedication(admin.TabularInline):
    model = Medication
    extra = 1


@admin.register(Drone)
class DroneAdmin(admin.ModelAdmin):
    list_display = ['serial_number', 'model', 'weight_limit', 'battery_capacity']
    search_fields = ['serial_number']
    list_filter = ['model', 'state']
    inlines = [InlineMedication]


@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = ['name', 'weight', 'code', 'drone']
    search_fields = ['name', 'code']
    list_filter = ['drone']
