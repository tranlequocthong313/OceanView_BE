from django.db import transaction
from django.db.models.query import Q
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from user.models import PersonalInformation
from utils import get_logger

from . import swaggers
from .models import Relative, Service, ServiceRegistration, VehicleInformation
from .serializers import (
    AccessCardServiceRegistrationSerializer,
    ParkingCardServiceRegistrationSerializer,
)

log = get_logger(__name__)


class ServiceRegistrationView(ViewSet):
    serializer_class = AccessCardServiceRegistrationSerializer
    permission_classes = [IsAuthenticated]

    # You can save the policy on the number of vehicles for each
    # apartment in the database with a separate model
    max_vehicle_counts = {
        VehicleInformation.VehicleType.BYCYCLE: 2,
        VehicleInformation.VehicleType.MOTORBIKE: 2,
        VehicleInformation.VehicleType.CAR: 1,
    }

    def get_queryset(self):
        return ServiceRegistration.objects.all()

    def registered_service(self, service_id, citizen_id):
        return ServiceRegistration.objects.filter(
            service_id=service_id, personal_information__citizen_id=citizen_id
        ).exists()

    @extend_schema(**swaggers.SERVICE_ACCESS_CARD)
    @action(
        methods=["post"],
        url_path="access-cards",
        detail=False,
    )
    @transaction.atomic
    def access_card(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        relative_data = serializer.validated_data.get("relative")
        personal_information_data = relative_data.get("personal_information")

        if request.user.is_same_person(personal_information_data):
            return Response(
                "You do not need an access card",
                status.HTTP_400_BAD_REQUEST,
            )

        personal_information = PersonalInformation.objects.filter(
            Q(citizen_id=personal_information_data["citizen_id"])
            | Q(phone_number=personal_information_data["phone_number"])
        ).first()

        if personal_information is None:
            personal_information = PersonalInformation.objects.create(
                **personal_information_data
            )
        relative = Relative.objects.filter(
            personal_information__citizen_id=personal_information.citizen_id,
        ).first()
        if relative is None:
            relative = Relative.objects.create(
                relationship=relative_data.get("relationship", None),
                personal_information=personal_information,
            )
        relative.residents.add(request.user)
        if self.registered_service(
            service_id=Service.ServiceType.ACCESS_CARD,
            citizen_id=personal_information.citizen_id,
        ):
            return Response(
                "This person has registered for an access card",
                status.HTTP_400_BAD_REQUEST,
            )

        service_registration = ServiceRegistration.objects.create(
            service_id=Service.ServiceType.ACCESS_CARD,
            personal_information=personal_information,
            resident=request.user,
        )
        return Response(self.serializer_class(service_registration).data)

    def is_valid_vehicle_limit(self, apartment_id, vehicle_type):
        vehicle_count = VehicleInformation.objects.filter(
            apartment_id=apartment_id, vehicle_type=vehicle_type
        ).count()

        if vehicle_count >= self.max_vehicle_counts[vehicle_type]:
            return False
        else:
            return True

    @extend_schema(**swaggers.SERVICE_PARKING_CARD)
    @action(
        methods=["post"],
        url_path="parking-cards",
        detail=False,
    )
    @transaction.atomic
    def parking_card(self, request):
        if request.user.apartment_set.count() == 0:
            return Response(
                "You don't live in an apartment, so you don't have the right to register for a parking card",
                status.HTTP_403_FORBIDDEN,
            )
        serializer = ParkingCardServiceRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        room_number = serializer.validated_data["room_number"]
        if not request.user.apartment_set.filter(room_number=room_number).exists():
            return Response(
                "This apartment does not belong to you, so you cannot register for a parking card",
                status=status.HTTP_403_FORBIDDEN,
            )

        # 2 motors, 2 bikes and 1 car per apartment
        vehicle_information = serializer.validated_data["vehicle_information"]
        if not self.is_valid_vehicle_limit(
            apartment_id=room_number,
            vehicle_type=vehicle_information["vehicle_type"],
        ):
            return Response(
                f"The apartment's limit of {self.max_vehicle_counts[vehicle_information['vehicle_type']]} {VehicleInformation.get_vehicle_type_label(vehicle_information['vehicle_type'])} has been reached",
                status.HTTP_403_FORBIDDEN,
            )

        relative_data = serializer.validated_data["relative"]
        personal_information_data = relative_data.get("personal_information")

        if request.user.is_same_person(personal_information_data):
            log.info("Register for current resident...")
            service_id = VehicleInformation.get_service_id(
                vehicle_information["vehicle_type"]
            )
            service_registration = ServiceRegistration.objects.create(
                service_id=service_id,
                personal_information=request.user.personal_information,
                resident=request.user,
            )
            VehicleInformation.objects.create(
                license_plate=vehicle_information["license_plate"],
                vehicle_type=vehicle_information["vehicle_type"],
                service_registration=service_registration,
                apartment_id=room_number,
            )
            return Response(self.serializer_class(service_registration).data)
        else:
            log.info("Register for relatives...")
            personal_information = PersonalInformation.objects.filter(
                Q(citizen_id=personal_information_data["citizen_id"])
                | Q(phone_number=personal_information_data["phone_number"])
            ).first()
            if personal_information is None:
                personal_information = PersonalInformation.objects.create(
                    **personal_information_data
                )

            relative = Relative.objects.filter(
                personal_information__citizen_id=personal_information.citizen_id,
            ).first()
            if relative is None:
                relative = Relative.objects.create(
                    relationship=relative_data.get("relationship", None),
                    personal_information=personal_information,
                )
            relative.residents.add(request.user)

            service_id = VehicleInformation.get_service_id(
                vehicle_information["vehicle_type"]
            )
            service_registration = ServiceRegistration.objects.create(
                service_id=service_id,
                personal_information=personal_information,
                resident=request.user,
            )
            VehicleInformation.objects.create(
                license_plate=vehicle_information["license_plate"],
                vehicle_type=vehicle_information["vehicle_type"],
                service_registration=service_registration,
                apartment_id=room_number,
            )
            return Response(self.serializer_class(service_registration).data)
