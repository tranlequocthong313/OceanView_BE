from rest_framework import serializers

from user.serializers import PersonalInformationSerializer

from . import models


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Service
        fields = ["service_id", "name", "price"]
        read_only_fields = ["service_id", "name", "price"]


class VehicleInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.VehicleInformation
        fields = ["license_plate", "vehicle_type"]

    def validate(self, attrs):
        vehicle_type = attrs.get("vehicle_type")
        license_plate = attrs.get("license_plate")

        if (
            vehicle_type == models.VehicleInformation.VehicleType.BYCYCLE
            and license_plate
        ):
            raise serializers.ValidationError(
                {"license_plate": "Bicycles do not have license plates"}
            )

        if (
            vehicle_type != models.VehicleInformation.VehicleType.BYCYCLE
            and not license_plate
        ):
            raise serializers.ValidationError(
                {
                    "license_plate": f"{models.VehicleInformation.get_vehicle_type_label(vehicle_type)} need license plates"
                }
            )

        return attrs


class RelativeSerializer(serializers.ModelSerializer):
    personal_information = PersonalInformationSerializer()

    class Meta:
        model = models.Relative
        fields = ["relationship", "personal_information"]


class AccessCardServiceRegistrationSerializer(serializers.ModelSerializer):
    service = ServiceSerializer(read_only=True)
    relative = RelativeSerializer(required=True, write_only=True)
    status = serializers.CharField(read_only=True)

    class Meta:
        model = models.ServiceRegistration
        fields = ["service", "relative", "status"]


class ParkingCardServiceRegistrationSerializer(AccessCardServiceRegistrationSerializer):
    vehicle_information = VehicleInformationSerializer(write_only=True)
    room_number = serializers.CharField(write_only=True)

    class Meta:
        model = models.VehicleInformation
        fields = AccessCardServiceRegistrationSerializer.Meta.fields + [
            "room_number",
            "vehicle_information",
        ]


class HistoryServiceRegistrationSerializer(serializers.ModelSerializer):
    service = ServiceSerializer()

    class Meta:
        model = models.ServiceRegistration
        fields = ["id", "service", "status", "created_date", "updated_date"]
        read_only_fields = ["id", "service", "status", "created_date", "updated_date"]


class DetailHistoryServiceRegistrationSerializer(
    HistoryServiceRegistrationSerializer, ParkingCardServiceRegistrationSerializer
):
    relative = RelativeSerializer(read_only=True, required=False)
    vehicle_information = VehicleInformationSerializer(read_only=True, required=False)
    room_number = serializers.CharField(read_only=True, required=False)

    class Meta:
        model = models.ServiceRegistration
        fields = (
            ParkingCardServiceRegistrationSerializer.Meta.fields
            + HistoryServiceRegistrationSerializer.Meta.fields
        )

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        relative = models.Relative.objects.filter(
            personal_information=instance.personal_information
        ).first()
        if relative:
            rep["relative"] = RelativeSerializer(relative).data
        vehicle_information = models.VehicleInformation.objects.filter(
            service_registration=instance
        ).first()
        if vehicle_information:
            rep["vehicle_information"] = VehicleInformationSerializer(
                vehicle_information
            ).data
        return rep
