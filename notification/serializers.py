from rest_framework import serializers

from app import settings
from feedback.models import Feedback
from service.models import ServiceRegistration

from .models import FCMToken, Notification, NotificationContent


class FCMTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = FCMToken
        fields = ["token", "device_type"]
        extra_kwargs = {
            "token": {
                "write_only": True,
                "validators": [],
            },
            "device_type": {
                "write_only": True,
            },
        }

    def create(self, validated_data):
        obj, created = FCMToken.objects.update_or_create(
            token=validated_data["token"],
            defaults={},  # * only update timestamp
            create_defaults={
                "token": validated_data["token"],
                "device_type": validated_data["device_type"],
                "user": validated_data["user"],
            },
        )
        return obj, created


ENTITY_TYPE_MODEL_MAPPING = {
    "SERVICE_REGISTER": ServiceRegistration,
    "FEEDBACK_POST": Feedback,
}

ACTION_MESSAGE_MAPPING = {
    "FEEDBACK_POST": lambda entity, notification_content: entity.message_feedback_post(
        notification_content.get_entity_type_display().lower()
    ),
    "SERVICE_REGISTER": lambda entity,
    notification_content: entity.message_service_register(
        notification_content.get_entity_type_display().lower()
    ),
}


class ReadNotificationSerializer(serializers.ModelSerializer):
    content_id = serializers.IntegerField()

    class Meta:
        model = Notification
        fields = ["content_id"]


class NotificationContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationContent
        fields = ["id", "entity_type", "entity_id"]
        read_only_fields = ["id", "entity_type", "entity_id"]


class ClientNotificationSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField(read_only=True)
    message = serializers.SerializerMethodField(read_only=True)
    content = NotificationContentSerializer(read_only=True)

    def get_image(self, instance):
        return instance.recipient.avatar_url

    def get_message(self, instance):
        entity = ENTITY_TYPE_MODEL_MAPPING[instance.content.entity_type].objects.get(
            pk=instance.content.entity_id
        )
        return ACTION_MESSAGE_MAPPING[instance.content.entity_type](
            entity, instance.content
        )

    class Meta:
        model = Notification
        fields = [
            "id",
            "has_been_read",
            "message",
            "content",
            "image",
            "created_date",
            "updated_date",
        ]
        read_only_fields = [
            "id",
            "has_been_read",
            "message",
            "content",
            "image",
            "created_date",
            "updated_date",
        ]


LINK_MAPPING = {
    "SERVICE_REGISTER": lambda entity_id: f"{settings.HOST}/admin/service/serviceregistration/{entity_id}/change/",
    "FEEDBACK_POST": lambda entity_id: f"{settings.HOST}/admin/feedback/feedback/{entity_id}/change/",
}


class AdminNotificationSerializer(ClientNotificationSerializer):
    link = serializers.SerializerMethodField()

    def get_link(self, instance):
        return LINK_MAPPING[instance.content.entity_type](instance.content.entity_id)

    class Meta:
        model = ClientNotificationSerializer.Meta.model
        fields = ClientNotificationSerializer.Meta.fields + ["link"]
        read_only_fields = ClientNotificationSerializer.Meta.fields + ["link"]
