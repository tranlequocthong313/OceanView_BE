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
            image=request.user.avatar_url,
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
            image=notification_content.image,
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
            image=request.user.avatar_url,
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
            title=f"{request.user.__str__()} {notification_content.get_entity_type_display().lower()} {service_registration.service.get_id_display().lower()}.",
            link=LINK_MAPPING[notification_content.entity_type](
                service_registration.pk
            ),
            image=notification_content.image,
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
            image=request.user.avatar_url,
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
            title=f"{request.user.__str__()} {notification_content.get_entity_type_display().lower()} {reissue.service_registration.service.get_id_display()}.",
            link=LINK_MAPPING[notification_content.entity_type](reissue.pk),
            image=notification_content.image,
            data={
                "content": json.dumps(
                    NotificationContentSerializer(notification_content).data
                ),
            },
        )

    @staticmethod
    def create_notification_for_proof_image(request, proof_image):
        notification_content = NotificationContent.objects.create(
            entity_id=proof_image.pk,
            entity_type=NotificationContent.EntityType.INVOICE_PROOF_IMAGE_PAYMENT,
            image=request.user.avatar_url,
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
            title=f"{request.user.__str__()} {notification_content.get_entity_type_display().lower()} {proof_image.payment.get_method_display()}.",
            link=LINK_MAPPING[notification_content.entity_type](proof_image.pk),
            image=notification_content.image,
            data={
                "content": json.dumps(
                    NotificationContentSerializer(notification_content).data
                ),
            },
        )

    @staticmethod
    def create_notification_for_news(news):
        notification_content = NotificationContent.objects.create(
            entity_id=news.pk,
            entity_type=NotificationContent.EntityType.NEWS_POST,
        )
        NotificationSender.objects.create(
            sender=User.objects.filter(is_staff=True).first(),
            content=notification_content,
        )
        for user in User.objects.filter(
            fcmtoken__device_type=FCMToken.DeviceType.ANDROID
        ).distinct():
            log.debug(user)
            Notification.objects.create(recipient=user, content=notification_content)
        message.send_notification(
            title=f"Ban quản trị {notification_content.get_entity_type_display().lower()} {news.message_news_post(notification_content.get_entity_type_display().lower())}.",
            image=settings.LOGO,
            data={
                "content": json.dumps(
                    NotificationContentSerializer(notification_content).data
                ),
            },
        )


@receiver(post_save, sender=News)
def send_broadcast(sender, instance, created, **kwargs):
    if created:
        AdminNotificationManager.create_notification_for_news(instance)
