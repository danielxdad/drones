from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import action

from .models import Drone, Medication
from .serializers import (
    DroneSerializer,
    MedicationSerializer,
    IDMedicationSerializer,
    DronStateSerializer,
    DronBatterySerializer
)
from .exceptions import (
    WeightExceededError,
    DroneInvalidStateError,
    DroneBatteryTooLowError
)


class DroneViewset(viewsets.ModelViewSet):
    queryset = Drone.objects.all()
    serializer_class = DroneSerializer

    @action(detail=True, methods=['post'], serializer_class=DronStateSerializer)
    def set_state(self, request: Request, *args, **kwargs):
        drone: Drone = self.get_object()
        serializer_class = self.get_serializer_class()

        serializer = serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        try:
            drone.set_state(serializer.validated_data['state'])
        except (DroneInvalidStateError, DroneBatteryTooLowError) as err:
            return Response(
                {'detail': err.message},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


    @action(detail=True, methods=['post'], serializer_class=IDMedicationSerializer)
    def load_medication_item(self, request, *args, **kwargs):
        """
        Load medication item to the drone

            Parameters on request:
                medication_item_id (int): An ID of existing medication item
            
            Returns:
                Response: JSON response object 
        """

        drone: Drone = self.get_object()

        # Before load a item to the drone the state must be "LOADING"
        if drone.state != Drone.STATE_LOADING:
            return Response(
                {'detail': 'The drone state is invalid for this operation.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        try:
            medication_item = Medication.objects.get(pk=serializer.validated_data['medication_item_id'])
        except Medication.DoesNotExist:
            return Response(
                {'detail': 'Medication item does not exist.'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            drone.load_medication_item(medication_item)
        except (WeightExceededError, TypeError) as err:
            return Response(
                {'detail': err.message},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        return Response(
            {'detail': 'The item has been loaded successfully.'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['get'], serializer_class=MedicationSerializer)
    def get_loaded_medication_items(self, request, *args, **kwargs):
        """
        Get loaded medication items of a drone

            Returns:
                Response: List of medication items
        """
        drone: Drone = self.get_object()
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(drone.medications.all(), many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def get_available_drones_for_load(self, request, *args, **kwargs):
        """
        Get available drones for load

            Returns:
                Response: List of drones
        """
        available_drones = filter(
            lambda drone: drone.state in [Drone.STATE_IDLE, Drone.STATE_LOADING] 
                and drone.battery_capacity >= settings.DRON_BATTERY_THRESHOLD
                and drone.current_weight < drone.weight_limit,
            self.get_queryset()
        )

        serializer_class = self.get_serializer_class()
        serializer = serializer_class(available_drones, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'], serializer_class=DronBatterySerializer)
    def get_battery(self, request, *args, **kwargs):
        """
        Get batterry lavel of the drone

            Returns:
                Response: Battery lavel of the drone
        """
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(self.get_object(), context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class MedicationViewset(viewsets.ModelViewSet):
    queryset = Medication.objects.all()
    serializer_class = MedicationSerializer
