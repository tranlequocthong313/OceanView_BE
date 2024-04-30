import traceback

from django.db import transaction
from django.db.models.query import Q
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import (
    DestroyAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from firebase.notification_manager import AdminNotificationManager
from user.models import PersonalInformation
from utils import get_logger

from . import serializers, swaggers
from .models import Relative, Service, ServiceRegistration, Vehicle

log = get_logger(__name__)


class ServiceRegistrationView(DestroyAPIView, ReadOnlyModelViewSet):
    serializer_class = serializers.AccessCardServiceRegistrationSerializer
    permission_classes = [IsAuthenticated]
    # ? Save the policy on the number of vehicles for each apartment in the database with a separate model
    max_vehicle_counts = {
        Vehicle.VehicleType.BICYCLE: 2,
        Vehicle.VehicleType.MOTORBIKE: 2,
        Vehicle.VehicleType.CAR: 1,
    }

    def get_queryset(self):
        queryset = ServiceRegistration.objects.filter(resident=self.request.user).all()

        if self.action == "list":
            category = self.request.query_params.get("category")
            status = self.request.query_params.get("status")
            exclude_status = self.request.query_params.get("_status")

            categories = {
                "access": queryset.filter(
                    service__service_id=Service.ServiceType.ACCESS_CARD
                ),
                "parking": queryset.filter(
                    service__service_id__in=Service.parking_services()
                ),
            }

            if category and category in categories:
                queryset = categories[category]
            if status:
                queryset = queryset.filter(status=status)
            if exclude_status:
                queryset = queryset.exclude(status=exclude_status)

        return queryset

    def registered_service(self, service_id, citizen_id):
        return ServiceRegistration.objects.filter(
            service_id=service_id, personal_information__citizen_id=citizen_id
        ).exists()

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.HistoryServiceRegistrationSerializer
        elif self.action == "retrieve":
            return serializers.DetailHistoryServiceRegistrationSerializer
        return super().get_serializer_class()

    @extend_schema(**swaggers.SERVICE_HISTORY)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_canceled:
            log.error(f"{instance} has been canceled already")
            return Response(
                "This service has been canceled already",
                status=status.HTTP_400_BAD_REQUEST,
            )
        instance.cancel()
        log.info(f"{instance} is canceled successfully")
        return Response(status=status.HTTP_204_NO_CONTENT)

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

        try:
            if request.user.is_same_person(personal_information_data):
                log.error(f"{request.user} do not need an access card")
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
                log.info("Created new personal information")
            elif personal_information.has_account():
                log.error(f"{personal_information} do not need an access card")
                return Response(
                    "This person does not need an access card",
                    status.HTTP_400_BAD_REQUEST,
                )

            relative = Relative.objects.filter(
                personal_information__citizen_id=personal_information.citizen_id,
            ).first()
            if relative is None:
                relative = Relative.objects.create(
                    relationship=relative_data.get("relationship", None),
                    personal_information=personal_information,
                )
                log.info("Created new relative")
            relative.residents.add(request.user)
            log.info(f"Added {request.user} to {relative}'s relatives")
            if self.registered_service(
                service_id=Service.ServiceType.ACCESS_CARD,
                citizen_id=personal_information.citizen_id,
            ):
                log.error(f"{relative} has registered for an access card")
                return Response(
                    "This person has registered for an access card",
                    status.HTTP_400_BAD_REQUEST,
                )

            service_registration = ServiceRegistration.objects.create(
                service_id=Service.ServiceType.ACCESS_CARD,
                personal_information=personal_information,
                resident=request.user,
            )
            AdminNotificationManager.create_notification_for_service_registration(
                request, service_registration
            )
            log.info(f"{relative} registered successfully")
            return Response(self.serializer_class(service_registration).data)
        except Exception:
            log.error("Server error", traceback.format_exc())
            return Response(
                "Something went wrong", status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def is_valid_vehicle_limit(self, apartment_id, vehicle_type):
        vehicle_count = Vehicle.objects.filter(
            apartment_id=apartment_id, vehicle_type=vehicle_type
        ).count()

        return vehicle_count < self.max_vehicle_counts[vehicle_type]

    @extend_schema(**swaggers.SERVICE_PARKING_CARD)
    @action(
        methods=["post"],
        url_path="parking-cards",
        detail=False,
    )
    @transaction.atomic
    def parking_card(self, request):
        if request.user.apartment_set.count() == 0:
            log.error(f"{request.user} doesn't live in an apartment")
            return Response(
                "You don't live in an apartment, so you don't have the right to register for a parking card",
                status.HTTP_403_FORBIDDEN,
            )
        serializer = serializers.ParkingCardServiceRegistrationSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        try:
            room_number = serializer.validated_data["room_number"]
            if not request.user.apartment_set.filter(room_number=room_number).exists():
                log.error(f"{request.user} doesn't live in {room_number} room")
                return Response(
                    "This apartment does not belong to you, so you cannot register for a parking card",
                    status=status.HTTP_403_FORBIDDEN,
                )

            log.info(f"{request.user}'s room is {room_number}")
            # 2 motors, 2 bikes and 1 car per apartment
            vehicle = serializer.validated_data["vehicle"]
            if not self.is_valid_vehicle_limit(
                apartment_id=room_number,
                vehicle_type=vehicle["vehicle_type"],
            ):
                log.error(
                    f"{room_number} can't have more {Vehicle.get_vehicle_type_label(vehicle['vehicle_type'])}"
                )
                return Response(
                    f"The apartment's limit of {self.max_vehicle_counts[vehicle['vehicle_type']]} {Vehicle.get_vehicle_type_label(vehicle['vehicle_type'])} has been reached",
                    status.HTTP_403_FORBIDDEN,
                )

            relative_data = serializer.validated_data["relative"]
            personal_information_data = relative_data.get("personal_information")

            if request.user.is_same_person(personal_information_data):
                log.debug(f"Registering for current resident {request.user}...")
                service_id = Vehicle.get_service_id(vehicle["vehicle_type"])
                service_registration = ServiceRegistration.objects.create(
                    service_id=service_id,
                    personal_information=request.user.personal_information,
                    resident=request.user,
                )
                Vehicle.objects.create(
                    license_plate=vehicle["license_plate"],
                    vehicle_type=vehicle["vehicle_type"],
                    service_registration=service_registration,
                    apartment_id=room_number,
                )
                log.info(f"Registered {request.user} successfully")
            else:
                log.debug("Register for relatives...")
                personal_information = PersonalInformation.objects.filter(
                    Q(citizen_id=personal_information_data["citizen_id"])
                    | Q(phone_number=personal_information_data["phone_number"])
                ).first()
                if personal_information is None:
                    personal_information = PersonalInformation.objects.create(
                        **personal_information_data
                    )
                    log.info("Created new personal information")

                relative = Relative.objects.filter(
                    personal_information__citizen_id=personal_information.citizen_id,
                ).first()
                if relative is None:
                    relative = Relative.objects.create(
                        relationship=relative_data.get("relationship", None),
                        personal_information=personal_information,
                    )
                    log.info("Created new relative")
                relative.residents.add(request.user)
                log.info(f"Added {request.user} to {relative}'s relatives")

                service_id = Vehicle.get_service_id(vehicle["vehicle_type"])
                service_registration = ServiceRegistration.objects.create(
                    service_id=service_id,
                    personal_information=personal_information,
                    resident=request.user,
                )
                Vehicle.objects.create(
                    license_plate=vehicle["license_plate"],
                    vehicle_type=vehicle["vehicle_type"],
                    service_registration=service_registration,
                    apartment_id=room_number,
                )
                log.info(f"Registered for {relative} successfully")
            AdminNotificationManager.create_notification_for_service_registration(
                request, service_registration
            )
            return Response(self.serializer_class(service_registration).data)
        except Exception:
            log.error("Server error", traceback.format_exc())
            return Response(
                "Something went wrong", status.HTTP_500_INTERNAL_SERVER_ERROR
            )
