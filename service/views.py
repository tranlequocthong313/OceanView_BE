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

from notification.manager import NotificationManager
from notification.types import EntityType
from user.models import PersonalInformation
from user.permissions import IsOwner
from utils import get_logger

from . import serializers, swaggers
from .models import (
    MyBaseServiceStatus,
    ReissueCard,
    Relative,
    Service,
    ServiceRegistration,
    Vehicle,
)

log = get_logger(__name__)


# TODO: Refactor this code
class ServiceRegistrationView(DestroyAPIView, ReadOnlyModelViewSet):
    serializer_class = serializers.AccessCardServiceRegistrationSerializer
    permission_classes = [IsAuthenticated]
    # NOTE: Able to save the policy on the number of vehicles for each apartment in the database with a separate model
    max_vehicle_counts = {
        Vehicle.VehicleType.BICYCLE: 2,
        Vehicle.VehicleType.MOTORBIKE: 2,
        Vehicle.VehicleType.CAR: 1,
    }
    MAXIMUM_RESIDENT_CARDS_PER_APARTMENT = 4

    def get_queryset(self):
        queryset = ServiceRegistration.objects.filter(
            resident=self.request.user, deleted=False
        ).all()

        if self.action == "list":
            category = self.request.query_params.get("category")
            status = self.request.query_params.get("status")
            exclude_status = self.request.query_params.get("_status")

            categories = {
                "access": queryset.filter(service__id=Service.ServiceType.ACCESS_CARD),
                "parking": queryset.filter(service__id__in=Service.parking_services()),
                "resident": queryset.filter(
                    service__id=Service.ServiceType.RESIDENT_CARD
                ),
            }

            if category and category in categories:
                queryset = categories[category]
            if status:
                queryset = queryset.filter(status=status)
            if exclude_status:
                queryset = queryset.exclude(status=exclude_status)

        return queryset.order_by("-id")

    def registered_service(self, service_id, personal_information):
        return ServiceRegistration.objects.filter(
            service_id=service_id,
            personal_information=personal_information,
            status__in=[
                MyBaseServiceStatus.Status.WAITING_FOR_APPROVAL,
                MyBaseServiceStatus.Status.APPROVED,
            ],
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
        elif instance.is_approved or instance.is_waiting_for_approval:
            instance.cancel()
            if instance.has_vehicle:
                instance.vehicle.delete()
            log.info(f"{instance} is canceled successfully")
            return Response(status=status.HTTP_204_NO_CONTENT)
        log.error(f"{instance} can't be canceled")
        return Response(
            "This service registration is rejected. Therefore it can't be canceled",
            status=status.HTTP_400_BAD_REQUEST,
        )

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
                | Q(email=personal_information_data["email"])
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
                personal_information=personal_information,
            ):
                log.error(
                    f"{relative} has registered for an access card or it's waiting for approval"
                )
                return Response(
                    "This person has registered for an access card or it's waiting for approval",
                    status.HTTP_400_BAD_REQUEST,
                )

            service_registration = ServiceRegistration.objects.create(
                service_id=Service.ServiceType.ACCESS_CARD,
                personal_information=personal_information,
                resident=request.user,
                payment=ServiceRegistration.Payment.IMMEDIATELY,
            )
            NotificationManager.create_notification(
                entity=service_registration,
                entity_type=EntityType.SERVICE_REGISTER,
                sender=request.user,
            )
            log.info(f"{relative} registered successfully")
            return Response(self.serializer_class(service_registration).data)
        except Exception:
            log.error("Server error", traceback.format_exc())
            return Response(
                "Something went wrong", status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(**swaggers.SERVICE_RESIDENT_CARD)
    @action(
        methods=["post"],
        url_path="resident-cards",
        detail=False,
        serializer_class=serializers.ResidentCardServiceRegistrationSerializer,
    )
    @transaction.atomic
    def resident_card(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        relative_data = serializer.validated_data.get("relative")
        personal_information_data = relative_data.get("personal_information")

        try:
            room_number = serializer.validated_data["room_number"]
            if not request.user.apartment_set.filter(room_number=room_number).exists():
                log.error(f"{request.user} doesn't live in {room_number} room")
                return Response(
                    "This apartment does not belong to you, so you cannot register for a resident card",
                    status=status.HTTP_403_FORBIDDEN,
                )

            personal_information = PersonalInformation.objects.filter(
                Q(citizen_id=personal_information_data["citizen_id"])
                | Q(phone_number=personal_information_data["phone_number"])
                | Q(email=personal_information_data["email"])
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

            if (
                ServiceRegistration.objects.filter(
                    apartment_id=room_number,
                    service__pk=Service.ServiceType.RESIDENT_CARD,
                    status__in=[
                        MyBaseServiceStatus.Status.WAITING_FOR_APPROVAL,
                        MyBaseServiceStatus.Status.APPROVED,
                    ],
                ).count()
                >= self.MAXIMUM_RESIDENT_CARDS_PER_APARTMENT
            ):
                log.error(
                    "The apartment has been registered with a maximum of 4 resident cards"
                )
                return Response(
                    "The apartment has been registered with a maximum of 4 resident cards",
                    status.HTTP_400_BAD_REQUEST,
                )

            if self.registered_service(
                service_id=Service.ServiceType.RESIDENT_CARD,
                personal_information=personal_information,
            ):
                log.error(
                    f"{relative} has registered for a resident card or it's waiting for approval"
                )
                return Response(
                    "This person has registered for a resident card or it's waiting for approval",
                    status.HTTP_400_BAD_REQUEST,
                )

            service_registration = ServiceRegistration.objects.create(
                service_id=Service.ServiceType.RESIDENT_CARD,
                personal_information=personal_information,
                resident=request.user,
                apartment_id=room_number,
                payment=ServiceRegistration.Payment.IMMEDIATELY,
            )
            NotificationManager.create_notification(
                entity=service_registration,
                entity_type=EntityType.SERVICE_REGISTER,
                sender=request.user,
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
            service_registration__apartment_id=apartment_id,
            vehicle_type=vehicle_type,
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
                )
                log.info(f"Registered {request.user} successfully")
            else:
                log.debug("Register for relatives...")
                personal_information = PersonalInformation.objects.filter(
                    Q(citizen_id=personal_information_data["citizen_id"])
                    | Q(phone_number=personal_information_data["phone_number"])
                    | Q(email=personal_information_data["email"])
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
                    apartment_id=room_number,
                    payment=ServiceRegistration.Payment.MONTHLY,
                )
                Vehicle.objects.create(
                    license_plate=vehicle["license_plate"],
                    vehicle_type=vehicle["vehicle_type"],
                    service_registration=service_registration,
                )
                log.info(f"Registered for {relative} successfully")
            NotificationManager.create_notification(
                entity=service_registration,
                entity_type=EntityType.SERVICE_REGISTER,
                sender=request.user,
            )
            return Response(self.serializer_class(service_registration).data)
        except Exception:
            log.error("Server error", traceback.format_exc())
            return Response(
                "Something went wrong", status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(**swaggers.SERVICE_REISSUE)
    @action(
        methods=["post"],
        url_path="reissue",
        detail=True,
        permission_classes=[IsOwner],
    )
    @transaction.atomic
    def reissue(self, request, pk=None):
        if self.get_object().service.pk.find("CARD") == -1:
            log.error("This service does not support physical card")
            return Response(
                "This service does not support physical card",
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not self.get_object().is_approved:
            log.error("This service registration is not being approved")
            return Response(
                "This service registration is not being approved",
                status=status.HTTP_400_BAD_REQUEST,
            )
        obj, created = ReissueCard.objects.get_or_create(
            service_registration=self.get_object(),
            status=MyBaseServiceStatus.Status.WAITING_FOR_APPROVAL,
        )
        if not created:
            log.error("This person requested a card reissue and it is being processed")
            return Response(
                "You have requested a card reissue and it is being processed",
                status=status.HTTP_400_BAD_REQUEST,
            )
        NotificationManager.create_notification(
            entity=obj, entity_type=EntityType.SERVICE_REISSUE, sender=request.user
        )
        log.info(f"Make reissue request for {request.user.__str__()} successfully")
        return Response(
            "Requested successfully. Waiting for approval", status.HTTP_201_CREATED
        )
