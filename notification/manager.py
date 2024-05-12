import json

from django.db.models.base import post_save
from django.dispatch import receiver

from app import settings
from firebase import message
from news.models import News
from notification.models import (
    FCMToken,
    Notification,
    NotificationContent,
    NotificationSender,
)
from notification.serializers import LINK_MAPPING, NotificationContentSerializer
from notification.types import (
    ACTION_MESSAGE_MAPPING,
    ENTITY_TARGET,
    EntityType,
    MessageTarget,
)
from user.models import User
from utils import get_logger

log = get_logger(__name__)


def get_users_by_target(target=None, filters=None):
    if filters is None:
        filters = {}
    users = []
    if target == MessageTarget.ADMIN:
        users = User.objects.filter(
            is_staff=True, fcmtoken__device_type=FCMToken.DeviceType.WEB, **filters
        ).distinct()
    elif target in [MessageTarget.RESIDENTS, MessageTarget.RESIDENT]:
        users = User.objects.filter(
            fcmtoken__device_type=FCMToken.DeviceType.ANDROID, **filters
        ).distinct()
    elif target == MessageTarget.ALL:
        users = User.objects.filter(
            fcmtoken__device_type__isnull=False, **filters
        ).distinct()
    return users


class NotificationManager:
    @staticmethod
    def create_notification(
        entity=None, entity_type=None, sender=None, image=None, filters=None
    ):
        if filters is None:
            filters = {}
        if not entity or not entity_type:
            raise ValueError("entity values must not be empty")
        if not image:
            image = sender.avatar_url or settings.LOGO
        target = ENTITY_TARGET[str(entity_type)]
        content = NotificationContent.objects.create(
            entity_id=entity.pk,
            entity_type=entity_type,
            image=image,
        )
        NotificationSender.objects.create(sender=sender, content=content)
        for user in get_users_by_target(target=target, filters=filters):
            Notification.objects.create(recipient=user, content=content)
        message.send_notification(
            title=ACTION_MESSAGE_MAPPING[entity_type](entity=entity, content=content),
            link=(
                LINK_MAPPING[entity_type](entity.pk)
                if entity_type in LINK_MAPPING
                else None
            ),
            image=image,
            data={"content": json.dumps(NotificationContentSerializer(content).data)},
        )


@receiver(post_save, sender=News)
def send_broadcast(sender, instance, created, **kwargs):
    if created:
        NotificationManager.create_notification(
            entity=instance,
            entity_type=EntityType.NEWS_POST,
            sender=User.objects.filter(is_staff=True).first(),
            image=settings.LOGO,
        )
