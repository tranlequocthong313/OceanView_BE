from rest_framework import serializers

from user.serializers import UserSerializer

from .models import Item, Locker


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ["id", "name", "quantity", "image", "status", "created_date"]
        read_only_fields = ["id"]


class LockerSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Locker
        fields = ["id", "owner", "status"]
