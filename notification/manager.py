import json

from firebase import message
from notification.models import (
    FCMToken,
    Notification,
    NotificationContent,
    NotificationSender,
)
from notification.serializers import LINK_MAPPING, NotificationContentSerializer
from user.models import User
from utils import get_logger

log = get_logger(__name__)


# TODO: Refactor this code
class AdminNotificationManager:
    @staticmethod
    def create_notification_for_feedback(request, feedback):
        notification_content = NotificationContent.objects.create(
            entity_id=feedback.pk,
            entity_type=NotificationContent.EntityType.FEEDBACK_POST,
        )
        NotificationSender.objects.create(
            sender=request.user, content=notification_content
        )
        for user in User.objects.filter(
            is_staff=True, fcmtoken__device_type=FCMToken.DeviceType.WEB
        ).distinct():
            log.debug(user)
            Notification.objects.create(recipient=user, content=notification_content)
        message.send_notification_to_admin(
            title=f'{request.user.__str__()} {notification_content.get_entity_type_display().lower()}: "{feedback.__str__()}".',
            link=LINK_MAPPING[notification_content.entity_type](feedback.pk),
            request=request,
            data={
                "content": json.dumps(
                    NotificationContentSerializer(notification_content).data
                ),
            },
        )

    @staticmethod
    def create_notification_for_service_registration(request, service_registration):
        notification_content = NotificationContent.objects.create(
            entity_id=service_registration.pk,
            entity_type=NotificationContent.EntityType.SERVICE_REGISTER,
        )
        NotificationSender.objects.create(
            sender=request.user, content=notification_content
        )
        for user in User.objects.filter(
            is_staff=True, fcmtoken__device_type=FCMToken.DeviceType.WEB
        ).distinct():
            log.debug(user)
            Notification.objects.create(recipient=user, content=notification_content)
        message.send_notification_to_admin(
            title=f"{request.user.__str__()} {notification_content.get_entity_type_display().lower()} {service_registration.service.get_service_id_display().lower()}.",
            link=LINK_MAPPING[notification_content.entity_type](
                service_registration.pk
            ),
            request=request,
            data={
                "content": json.dumps(
                    NotificationContentSerializer(notification_content).data
                ),
            },
        )

    @staticmethod
    def create_notification_for_service_reissue(request, reissue):
        notification_content = NotificationContent.objects.create(
            entity_id=reissue.pk,
            entity_type=NotificationContent.EntityType.SERVICE_REISSUE,
        )
        NotificationSender.objects.create(
            sender=request.user, content=notification_content
        )
        for user in User.objects.filter(
            is_staff=True, fcmtoken__device_type=FCMToken.DeviceType.WEB
        ).distinct():
            log.debug(user)
            Notification.objects.create(recipient=user, content=notification_content)
        message.send_notification_to_admin(
            title=f"{request.user.__str__()} {notification_content.get_entity_type_display().lower()} {reissue.service_registration.service.get_service_id_display()}.",
            link=LINK_MAPPING[notification_content.entity_type](reissue.pk),
            request=request,
            data={
                "content": json.dumps(
                    NotificationContentSerializer(notification_content).data
                ),
            },
        )
