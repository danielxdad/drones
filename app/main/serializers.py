from rest_framework import serializers

from .models import Drone, Medication

class DroneSerializer(serializers.ModelSerializer):
    current_weight = serializers.FloatField(read_only=True)

    class Meta:
        model = Drone
        fields = ['id', 'serial_number', 'model', 'weight_limit', 'battery_capacity', 'state', 'current_weight']
        read_only_fields = ['state', 'current_weight']


class MedicationSerializer(serializers.ModelSerializer):
    drone = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Medication
        fields = ['id', 'name', 'weight', 'code', 'image', 'drone']
        read_only_fields = ['drone']


class IDMedicationSerializer(serializers.Serializer):
    medication_item_id = serializers.IntegerField()


class DronStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Drone
        fields = ['state']


class DronBatterySerializer(serializers.ModelSerializer):
    class Meta:
        model = Drone
        fields = ['battery_capacity']
