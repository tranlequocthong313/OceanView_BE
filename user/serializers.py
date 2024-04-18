from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.forms import IntegerField
from rest_framework.fields import empty
from rest_framework.serializers import (
    CharField,
    ImageField,
    ListField,
    ModelSerializer,
    Serializer,
    SerializerMethodField,
    ValidationError,
)

from .models import PersonalInformation


class PersonalInformationSerializer(ModelSerializer):
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["gender"] = instance.get_gender_label()

        return rep

    class Meta:
        model = PersonalInformation
        fields = "__all__"

    def validate(self, attrs):
        print("PERSONAL")
        return super().validate(attrs)


class UserSerializer(ModelSerializer):
    personal_information = PersonalInformationSerializer(read_only=True)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["avatar"] = instance.avatar.url if instance.avatar else None
        rep["status"] = instance.get_status_label()

        return rep

    class Meta:
        model = get_user_model()
        fields = (
            "personal_information",
            "password",
            "avatar",
            "resident_id",
            "is_staff",
            "is_superuser",
            "status",
            "issued_by",
        )
        read_only_fields = []
        extra_kwargs = {"password": {"write_only": "true"}}


class TokenSerializer(Serializer):
    access_token = CharField()
    refresh_token = CharField()
    expires_in = IntegerField()
    token_type = CharField()
    scope = CharField()


class LogonUserSerializer(UserSerializer):
    token = TokenSerializer()

    class Meta:
        model = UserSerializer.Meta.model
        fields = UserSerializer.Meta.fields + ("token",)


class ActiveUserSerializer(Serializer):
    avatar = ImageField()
    password = CharField(write_only=True, validators=[validate_password])

    def update(self, instance, validated_data):
        instance.avatar = validated_data["avatar"]
        instance.set_password(validated_data["password"])
        instance.active()
        instance.save()

        return instance


class LoginSerializer(Serializer):
    username = CharField()
    password = CharField(write_only=True, validators=[validate_password])


class ResetPasswordMethodSerializer(Serializer):
    methods = ListField()


class TokenResetPasswordSerializer(Serializer):
    token = CharField()


class VerifyOTPSerializer(Serializer):
    resident_id = CharField()
    otp = CharField()


class ResetPasswordSerializer(Serializer):
    password = CharField(validators=[validate_password])
    confirm_password = CharField(validators=[validate_password])

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise ValidationError({"password": "Password fields didn't match."})

        return super().validate(attrs)
