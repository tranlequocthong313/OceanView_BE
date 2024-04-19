from rest_framework import serializers

from user.serializers import PersonalInformationSerializer

from .models import Relative, Service, ServiceRegistration, VehicleInformation


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ["service_id", "name", "price"]
        read_only_fields = ["service_id", "name", "price"]


class VehicleInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleInformation
        fields = ["license_plate", "vehicle_type"]

    def validate(self, attrs):
        vehicle_type = attrs.get("vehicle_type")
        license_plate = attrs.get("license_plate")

        if vehicle_type == VehicleInformation.VehicleType.BYCYCLE and license_plate:
            raise serializers.ValidationError(
                {"license_plate": "Bicycles do not have license plates"}
            )

        if vehicle_type != VehicleInformation.VehicleType.BYCYCLE and not license_plate:
            raise serializers.ValidationError(
                {
                    "license_plate": f"{VehicleInformation.get_vehicle_type_label(vehicle_type)} need license plates"
                }
            )

        return attrs


class RelativeSerializer(serializers.ModelSerializer):
    personal_information = PersonalInformationSerializer()

    class Meta:
        model = Relative
        fields = ["relationship", "personal_information"]


class AccessCardServiceRegistrationSerializer(serializers.ModelSerializer):
    service = ServiceSerializer(read_only=True)
    relative = RelativeSerializer(required=True, write_only=True)
    status = serializers.CharField(read_only=True)

    class Meta:
        model = ServiceRegistration
        fields = ["service", "relative", "status"]


class ParkingCardServiceRegistrationSerializer(AccessCardServiceRegistrationSerializer):
    vehicle_information = VehicleInformationSerializer(write_only=True)
    room_number = serializers.CharField(write_only=True)

    class Meta:
        model = VehicleInformation
        fields = AccessCardServiceRegistrationSerializer.Meta.fields + [
            "room_number",
            "vehicle_information",
        ]
