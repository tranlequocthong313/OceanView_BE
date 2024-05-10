from rest_framework import serializers

from notification.types import (
    ACTION_MESSAGE_MAPPING,
    ENTITY_TYPE_MODEL_MAPPING,
    LINK_MAPPING,
)

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


class ReadNotificationSerializer(serializers.ModelSerializer):
    content_id = serializers.IntegerField()

    class Meta:
        model = Notification
        fields = ["content_id"]


class NotificationContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationContent
        fields = ["id", "entity_type", "entity_id", "image"]
        read_only_fields = ["id", "entity_type", "entity_id", "image"]


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


class AdminNotificationSerializer(ClientNotificationSerializer):
    link = serializers.SerializerMethodField()

    def get_link(self, instance):
        return (
            LINK_MAPPING[instance.content.entity_type](instance.content.entity_id)
            if instance.content.entity_type in LINK_MAPPING
            else ""
        )

    class Meta:
        model = ClientNotificationSerializer.Meta.model
        fields = ClientNotificationSerializer.Meta.fields + ["link"]
        read_only_fields = ClientNotificationSerializer.Meta.fields + ["link"]
