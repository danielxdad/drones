from rest_framework import viewsets

from .models import Drone, Medication
from .serializers import DroneSerializer, MedicationSerializer


class DroneViewset(viewsets.ModelViewSet):
    queryset = Drone.objects.all()
    serializer_class = DroneSerializer


class MedicationViewset(viewsets.ModelViewSet):
    queryset = Medication.objects.all()
    serializer_class = MedicationSerializer
