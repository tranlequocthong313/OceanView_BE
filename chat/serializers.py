from rest_framework import serializers

from firebase import firestore
from notification.manager import NotificationManager
from notification.types import EntityType
from user.models import User

from .models import Inbox, Message


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="personal_information.full_name")
    avatar = serializers.ImageField()

    class Meta:
        model = User
        fields = ["resident_id", "full_name", "avatar"]


class InboxSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        user = obj.user_1 if obj.user_1 != self.context["user"] else obj.user_2
        return UserSerializer(user).data

    def validate(self, attrs):
        user_1 = attrs.get("user_1")
        user_2 = attrs.get("user_2")
        if user_1 == user_2:
            raise serializers.ValidationError(
                {"user": "user_1 and user_2 must not be equal"}
            )
        return super().validate(attrs)

    class Meta:
        model = Inbox
        fields = ["id", "last_message", "user", "user_1", "user_2"]
        read_only_fields = ["id", "last_message", "user"]


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = "__all__"

    def create(self, validated_data):
        instance = super().create(validated_data)
        request = self.context["request"]
        inbox = instance.inbox
        inbox.last_message = instance.content
        inbox.save()
        receiver = inbox.user_1 if inbox.user_1 != request.user else inbox.user_2
        firestore_data = {
            "id": inbox.id,
            "created_date": inbox.created_date,
            "updated_date": inbox.updated_date,
            "last_message": instance.content,
            "user_1_id": request.user.resident_id,
            "user_2_id": receiver.resident_id,
            "user_1": {
                "resident_id": request.user.resident_id,
                "full_name": request.user.personal_information.full_name,
                "avatar": request.user.avatar_url,
            },
            "user_2": {
                "resident_id": receiver.resident_id,
                "full_name": receiver.personal_information.full_name,
                "avatar": receiver.avatar_url,
            },
        }
        firestore.db.collection("inboxes").document(document_id=str(inbox.id)).set(
            firestore_data
        )

        firestore_data = {
            "id": instance.id,
            "created_date": instance.created_date,
            "updated_date": instance.updated_date,
            "content": instance.content,
            "inbox": inbox.id,
            "sender": {
                "resident_id": request.user.resident_id,
                "full_name": request.user.personal_information.full_name,
                "avatar": request.user.avatar_url,
            },
        }
        firestore.db.collection("messages").document(document_id=str(instance.id)).set(
            firestore_data
        )
        NotificationManager.create_notification(
            entity=inbox,
            entity_type=EntityType.CHAT_SEND_MESSAGE,
            sender=request.user,
            image=request.user.avatar_url,
            filters={
                "resident_id": (
                    inbox.user_2.resident_id
                    if inbox.user_1 == request.user
                    else inbox.user_1.resident_id
                )
            },
        )
        return instance
