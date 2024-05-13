from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.forms import IntegerField
from rest_framework import serializers

from notification.models import FCMToken

from . import models


class PersonalInformationSerializer(serializers.ModelSerializer):
    citizen_id = serializers.CharField(required=True)
    email = serializers.EmailField()
    phone_number = serializers.CharField(required=True)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["gender"] = instance.get_gender_display()
        return rep

    class Meta:
        model = models.PersonalInformation
        fields = "__all__"
        extra_kwargs = {
            "email": {
                "validators": [],
            },
            "phone_number": {
                "validators": [],
            },
            "citizen_id": {
                "validators": [],
            },
        }


class UserSerializer(serializers.ModelSerializer):
    personal_information = PersonalInformationSerializer(read_only=True)
    apartment_set = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    locker = serializers.PrimaryKeyRelatedField(read_only=True)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["avatar"] = instance.avatar_url

        return rep

    class Meta:
        model = get_user_model()
        fields = (
            "apartment_set",
            "personal_information",
            "password",
            "avatar",
            "resident_id",
            "is_staff",
            "is_superuser",
            "status",
            "issued_by",
            "locker",
        )
        extra_kwargs = {"password": {"write_only": "true"}}


class TokenSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
    expires_in = IntegerField()
    token_type = serializers.CharField()
    scope = serializers.CharField()


class LogonUserSerializer(UserSerializer):
    token = TokenSerializer()

    class Meta:
        model = UserSerializer.Meta.model
        fields = UserSerializer.Meta.fields + ("token",)


class ActiveUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["avatar", "password", "status"]
        read_only_fields = ["status"]
        extra_kwargs = {
            "password": {
                "validators": [validate_password],
            },
        }

    def update(self, instance, validated_data):
        instance.avatar = validated_data["avatar"]
        instance.set_password(validated_data["password"])
        instance.active()
        instance.save()

        return instance


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, validators=[validate_password])


class RefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(required=True, write_only=True)


class ForgotPasswordSerializer(serializers.Serializer):
    user_identifier = serializers.CharField(write_only=True, required=True)


class MethodForResetPasswordSerializer(serializers.ModelSerializer):
    email = serializers.CharField(read_only=True, required=False)
    phone_number = serializers.CharField(read_only=True, required=False)

    class Meta:
        model = models.PersonalInformation
        fields = ["email", "phone_number"]


class SendResetPasswordLinkSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True, required=True)

    class Meta:
        model = models.PersonalInformation
        fields = ["email"]


class SendOTPSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = models.PersonalInformation
        fields = ["phone_number"]


class TokenResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField()


class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(write_only=True, required=True)
    otp = serializers.CharField(write_only=True, required=True)


class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(validators=[validate_password])
    confirm_password = serializers.CharField(validators=[validate_password])

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )

        return super().validate(attrs)


class LogoutSerializer(serializers.Serializer):
    fcm_token = serializers.CharField(write_only=True, required=False)
    device_type = serializers.CharField(
        write_only=True, required=False, default=FCMToken.DeviceType.ANDROID
    )
