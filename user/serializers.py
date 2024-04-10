from django.contrib.auth import get_user_model
from django.forms import IntegerField
from rest_framework.serializers import (
    CharField,
    ImageField,
    ModelSerializer,
    Serializer,
    SerializerMethodField,
)

from .models import PersonalInformation


class PersonalInformationSerializer(ModelSerializer):
    gender = SerializerMethodField()

    def get_gender(self, personal_information):
        return personal_information.get_gender_label()

    class Meta:
        model = PersonalInformation
        fields = [
            "citizen_id",
            "full_name",
            "date_of_birth",
            "phone_number",
            "email",
            "hometown",
            "gender",
        ]


class UserSerializer(ModelSerializer):
    avatar = SerializerMethodField()
    status = SerializerMethodField()
    personal_information = PersonalInformationSerializer()

    def get_avatar(self, user):
        return user.avatar.url if user.avatar else None

    def get_status(self, user):
        return user.get_status_label()

    class Meta:
        model = get_user_model()
        fields = [
            "resident_id",
            "personal_information",
            "password",
            "avatar",
            "is_staff",
            "is_superuser",
            "status",
            "issued_by",
        ]
        extra_kwargs = {"password": {"write_only": "true"}}


class TokenSerializer(Serializer):
    access_token = CharField()
    refresh_token = CharField()
    expires_in = IntegerField()
    token_type = CharField()
    scope = CharField()


class ActiveUserSerializer(ModelSerializer):
    avatar = ImageField()
    password = CharField(write_only=True, required=True)

    class Meta:
        model = get_user_model()
        fields = (
            "avatar",
            "password",
        )

    def update(self, instance, validated_data):
        instance.avatar = validated_data["avatar"]
        instance.set_password(validated_data["password"])
        instance.active()
        instance.save()

        return instance


class LoginSerializer(Serializer):
    username = CharField(required=True)
    password = CharField(write_only=True, required=True)

    class Meta:
        fields = (
            "username",
            "password",
        )


class ForgotPasswordSerializer(Serializer):
    resident_id = CharField(required=True)

    class Meta:
        fields = ("resident_id",)


class SendOTPSerializer(Serializer):
    resident_id = CharField(required=True)
    method = CharField(required=True)


class VerifyOTPSerializer(Serializer):
    resident_id = CharField(required=True)
    method = CharField(required=True)
    otp = CharField(required=True)


class ResetPasswordSerializer(Serializer):
    password = CharField(required=True)
    confirm_password = CharField(required=True)
