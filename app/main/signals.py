from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import Medication


@receiver(post_delete, sender=Medication)
def post_delete_medication(sender, instance, *args, **kwargs):
    instance.image.delete(save=False)
