from rest_framework import serializers

from app import settings
from notification.manager import NotificationManager
from notification.types import EntityType
from user.serializers import UserSerializer

from .models import Item, Locker


class ItemSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["image"] = instance.image_url

        return rep

    class Meta:
        model = Item
        fields = ["id", "name", "quantity", "image", "status", "created_date"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        instance = super().create(validated_data)
        NotificationManager.create_notification(
            entity=instance,
            entity_type=EntityType.LOCKER_ITEM_ADD,
            filters={"resident_id": instance.locker.owner.resident_id},
            image=settings.LOGO,
        )
        return instance


class LockerSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Locker
        fields = ["id", "owner", "status"]
