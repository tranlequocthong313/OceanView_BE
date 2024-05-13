from django.db.models import Q
from drf_spectacular.utils import extend_schema
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    UpdateAPIView,
)
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ReadOnlyModelViewSet, ViewSet

from utils import get_logger

from . import serializers, swaggers
from .models import Item, Locker

log = get_logger(__name__)


class LockerView(ListAPIView, ViewSet):
    serializer_class = serializers.LockerSerializer
    permission_classes = [IsAdminUser]
    lookup_url_kwarg = "locker_id"

    def get_queryset(self):
        queryset = Locker.objects.all()
        if self.action == "list":
            if q := self.request.query_params.get("q"):
                queryset = queryset.filter(
                    Q(owner__resident_id=q)
                    | Q(owner__personal_information__citizen_id__icontains=q)
                    | Q(owner__personal_information__phone_number__icontains=q)
                    | Q(owner__personal_information__email__icontains=q)
                )
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.LockerSerializer
        return super().get_serializer_class()

    @extend_schema(**swaggers.LOCKER_LIST)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ItemView(UpdateAPIView, CreateAPIView, ReadOnlyModelViewSet):
    serializer_class = serializers.ItemSerializer
    permission_classes = [IsAdminUser]
    http_method_names = ["get", "post", "patch"]
    lookup_url_kwarg = "item_id"

    def get_queryset(self):
        queryset = Item.objects.filter(locker_id=self.kwargs["locker_id"]).all()

        if self.action == "list":
            q = self.request.query_params.get("q")
            status = self.request.query_params.get("status")
            exclude_status = self.request.query_params.get("_status")

            if q:
                queryset = queryset.filter(name__icontains=q)
            if status:
                queryset = queryset.filter(status=status)
            if exclude_status:
                queryset = queryset.exclude(status=exclude_status)

        return queryset.order_by("-id")

    def perform_create(self, serializer):
        serializer.save(locker_id=self.kwargs["locker_id"])

    @extend_schema(**swaggers.ITEM_LIST)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
