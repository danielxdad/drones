from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    RegexValidator
)

from .exceptions import (
    WeightExceededError,
    DroneInvalidStateError,
    DroneBaterryTooLowError
)

class TimestampModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Drone(TimestampModel):
    """
    Drone model
    """
    
    MODEL_LIGHTWEIGHT = 'LW'
    MODEL_MIDDLEWEIGHT = 'MW'
    MODEL_CRUISERWEIGHT = 'CW'
    MODEL_HEAVYWEIGHT = 'HW'

    MODEL_CHOICES = (
        (MODEL_LIGHTWEIGHT, 'Lightweight'),
        (MODEL_MIDDLEWEIGHT, 'Middleweight'),
        (MODEL_CRUISERWEIGHT, 'Cruiserweight'),
        (MODEL_HEAVYWEIGHT, 'Heavyweight'),
    )

    STATE_IDLE = 'IDLE'
    STATE_LOADING = 'LOADING'
    STATE_LOADED = 'LOADED'
    STATE_DELIVERING = 'DELIVERING'
    STATE_DELIVERED = 'DELIVERED'
    STATE_RETURNING = 'RETURNING'

    STATE_CHOICES = (
        (STATE_IDLE, 'Idle'),
        (STATE_LOADING, 'Loading'),
        (STATE_LOADED, 'Loaded'),
        (STATE_DELIVERING, 'Delivering'),
        (STATE_DELIVERED, 'Delivered'),
        (STATE_RETURNING, 'Returning'),
    )

    serial_number = models.CharField('Serial number', max_length=100)
    model = models.CharField(choices=MODEL_CHOICES, default=MODEL_LIGHTWEIGHT, max_length=2)

    weight_limit = models.FloatField(
        'Weight limit (grams)',
        validators=[
            MinValueValidator(0),
            MaxValueValidator(500)
        ],
        help_text="Maximum value 500 grams"
    )

    battery_capacity = models.FloatField(
        'Battery capacity (percentage)',
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ],
        help_text="Range from 0 to 100"
    )

    state = models.CharField(choices=STATE_CHOICES, default=STATE_IDLE, max_length=10)

    class Meta:
        verbose_name = 'drone'
        verbose_name_plural = 'drones'

    def __str__(self) -> str:
        return self.serial_number
    
    @property
    def current_weight(self):
        return self.medications.aggregate(Sum('weight'))['weight__sum'] or 0

    def set_state(self, new_state: str) -> None:
        """
        Set a valid new state for the drone 
        """
        # Some kind of finite state machine to check the flow state of the drone
        fsm_transition_states = {
            Drone.STATE_IDLE: [Drone.STATE_LOADING],
            Drone.STATE_LOADING: [Drone.STATE_LOADED, Drone.STATE_IDLE],
            Drone.STATE_LOADED: [Drone.STATE_DELIVERING, Drone.STATE_LOADING, Drone.STATE_IDLE],
            Drone.STATE_DELIVERING: [Drone.STATE_DELIVERED, Drone.STATE_RETURNING],
            Drone.STATE_DELIVERED: [Drone.STATE_RETURNING],
            Drone.STATE_RETURNING: [Drone.STATE_IDLE]
        }

        # If the new state is not inside the valid states that can fallow the current state
        if new_state not in fsm_transition_states.get(self.state):
            # Don't let user change the state
            raise DroneInvalidStateError()
        
        # If the new state is LOADING and the drone battery capacity is less than "settings.DRON_BATERRY_THRESHOLD"
        if new_state == Drone.STATE_LOADING and self.battery_capacity < settings.DRON_BATERRY_THRESHOLD:
            # Don't let user change the state
            raise DroneBaterryTooLowError()

        self.state = new_state
        self.save()
    
    def load_medication_item(self, medication_item: 'Medication') -> None:
        """
        Load medication item to the drone, throw an exception in case of error.

            Parameters:
                medication_item (Medication): A medication item to load

            Exceptions:
                WeightExceededError: If the weight of the medication item exceeds the maximum drone's weight
                TypeError: If the medication_item is not an instance of Medication model

            Returns:
                None: Nothing is returned
        """

        if isinstance(medication_item, Medication) is False:
            raise TypeError('medication_item must be an instance of Medication model.')

        if self.current_weight + medication_item.weight > self.weight_limit:
            raise WeightExceededError()

        medication_item.drone = self
        medication_item.save()


class Medication(TimestampModel):
    """
    Medication model
    """

    name = models.TextField(
        validators=[RegexValidator(r'^[a-zA-Z0-9\-\_]*$')],
        help_text='Only alphanumeric characters, dashes and underscores'
    )
    weight = models.FloatField(help_text='In grams')
    code = models.TextField(
        validators=[RegexValidator(r'^[A-Z0-9\_]*$')],
        help_text='Only uppercase alphanumeric characters and underscores'
    )
    image = models.ImageField(upload_to='uploads/medications/%Y/%m/%d/', blank=True)
    drone = models.ForeignKey(Drone, on_delete=models.SET_NULL, null=True, blank=True, related_name='medications')

    class Meta:
        verbose_name = 'medication'
        verbose_name_plural = 'medications'

    def __str__(self) -> str:
        return self.name
