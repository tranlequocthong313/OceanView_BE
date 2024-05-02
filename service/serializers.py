from rest_framework import serializers

from user.serializers import PersonalInformationSerializer

from . import models


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Service
        fields = ["service_id", "name", "price"]
        read_only_fields = ["service_id", "name", "price"]


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Vehicle
        fields = ["license_plate", "vehicle_type"]

    def validate(self, attrs):
        vehicle_type = attrs.get("vehicle_type")
        license_plate = attrs.get("license_plate")

        if vehicle_type == models.Vehicle.VehicleType.BICYCLE and license_plate:
            raise serializers.ValidationError(
                {"license_plate": "Bicycles do not have license plates"}
            )

        if vehicle_type != models.Vehicle.VehicleType.BICYCLE and not license_plate:
            raise serializers.ValidationError(
                {
                    "license_plate": f"{models.Vehicle.get_vehicle_type_label(vehicle_type)} need license plates"
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


class ResidentCardServiceRegistrationSerializer(
    AccessCardServiceRegistrationSerializer
):
    room_number = serializers.CharField(write_only=True)

    class Meta:
        model = AccessCardServiceRegistrationSerializer.Meta.model
        fields = AccessCardServiceRegistrationSerializer.Meta.fields + ["room_number"]


class ParkingCardServiceRegistrationSerializer(
    ResidentCardServiceRegistrationSerializer
):
    vehicle = VehicleSerializer(write_only=True)

    class Meta:
        model = models.Vehicle
        fields = ResidentCardServiceRegistrationSerializer.Meta.fields + [
            "vehicle",
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
    vehicle = VehicleSerializer(read_only=True, required=False)

    class Meta:
        model = models.ServiceRegistration
        fields = (
            ParkingCardServiceRegistrationSerializer.Meta.fields
            + HistoryServiceRegistrationSerializer.Meta.fields
        )

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if instance.for_relative:
            rep["relative"] = RelativeSerializer(
                instance.personal_information.relative
            ).data
        if instance.has_vehicle:
            rep["vehicle"] = VehicleSerializer(instance.vehicle).data
        return rep
