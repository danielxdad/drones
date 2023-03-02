from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator


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
    image = models.ImageField(upload_to='uploads/medications/%Y/%m/%d/')
    drone = models.ForeignKey(Drone, on_delete=models.CASCADE, related_name='medications')

    class Meta:
        verbose_name = 'medication'
        verbose_name_plural = 'medications'

    def __str__(self) -> str:
        return self.name
