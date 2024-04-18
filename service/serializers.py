from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from rest_framework.serializers import (
    CharField,
    ModelSerializer,
    Serializer,
    ValidationError,
)

from user.models import PersonalInformation
from user.serializers import PersonalInformationSerializer

from .models import Relative, Service, ServiceRegistration, VehicleInformation


class ServiceSerializer(ModelSerializer):
    class Meta:
        model = Service
        fields = ["service_id", "name", "price"]
        read_only_fields = ["service_id", "name", "price"]


class RelativeSerializer(ModelSerializer):
    personal_information = PersonalInformationSerializer()

    class Meta:
        model = Relative
        fields = ["relationship", "personal_information"]


class VehicleInformationSerializer(ModelSerializer):
    class Meta:
        model = VehicleInformation
        fields = ["license_plate", "vehicle_type"]


class AccessCardServiceRegistrationSerializer(ModelSerializer):
    service = ServiceSerializer(read_only=True)
    relative = RelativeSerializer(required=True)
    resident_id = CharField(write_only=True)

    class Meta:
        model = ServiceRegistration
        fields = ["service", "relative", "resident_id"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["status"] = instance.get_status_label()
        return representation

    def _get_personal_information(self, personal_information):
        return PersonalInformation.objects.filter(
            Q(citizen_id=personal_information["citizen_id"])
            | Q(phone_number=personal_information["phone_number"])
            | Q(email=personal_information["email"])
        ).first()

    def validate_relative(self, value):
        if self._get_personal_information(value["personal_information"]) is not None:
            raise ValidationError("This person has registered for an access card")
        return value

    @transaction.atomic
    def create(self, validated_data):
        relative_data = validated_data["relative"]
        personal_information = PersonalInformation.objects.create(
            **relative_data["personal_information"]
        )
        relative = Relative.objects.create(
            relationship=relative_data["relationship"],
            personal_information=personal_information,
        )
        relative.residents.add(validated_data["resident_id"])
        return ServiceRegistration.objects.create(
            service_id=Service.ServiceType.ACCESS_CARD,
            personal_information=personal_information,
            resident_id=validated_data["resident_id"],
        )


class ParkingCardServiceRegistrationSerializer(AccessCardServiceRegistrationSerializer):
    vehicle_information = VehicleInformationSerializer(write_only=True)

    class Meta:
        model = VehicleInformation
        fields = AccessCardServiceRegistrationSerializer.Meta.fields + [
            "vehicle_information"
        ]

    def validate_relative(self, value):
        return value

    @transaction.atomic
    def create(self, validated_data):
        relative_data = validated_data["relative"]
        personal_information = self._get_personal_information(
            relative_data["personal_information"]
        )
        if personal_information is None:
            personal_information = PersonalInformation.objects.create(
                **relative_data["personal_information"]
            )
            personal_information = Relative.objects.create(
                relationship=relative_data["relationship"],
                personal_information=personal_information,
            )
        elif personal_information.user.resident_id != validated_data["resident_id"]:
            relative = Relative.objects.create(
                relationship=relative_data["relationship"],
                personal_information=personal_information,
            )
            relative.residents.add(validated_data["resident_id"])
        vehicle_information = validated_data["vehicle_information"]
        registration = ServiceRegistration.objects.create(
            service_id=VehicleInformation.get_service_id(
                vehicle_information["vehicle_type"]
            ),
            personal_information=personal_information,
            resident_id=validated_data["resident_id"],
        )
        VehicleInformation.objects.create(
            service_registration=registration, **vehicle_information
        )
        return registration
