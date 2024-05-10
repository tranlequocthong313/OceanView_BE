from django.db.models.base import pre_save
from django.dispatch import receiver

from app import settings
from invoice.models import Invoice
from notification.manager import NotificationManager
from notification.types import EntityType
from user.models import User


@receiver(pre_save, sender=Invoice)
def notifiy_to_resident(sender, instance, **kwargs):
    if instance._state.adding:
        NotificationManager.create_notification(
            entity=instance,
            entity_type=EntityType.INVOICE_CREATE,
            sender=User.objects.filter(is_staff=True).first(),
            image=settings.LOGO,
        )
