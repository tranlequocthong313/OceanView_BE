from rest_framework import mixins
from rest_framework.generics import (
    CreateAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet

from utils import get_logger

from .models import ServiceRegistration
from .serializers import (
    AccessCardServiceRegistrationSerializer,
    ParkingCardServiceRegistrationSerializer,
)

log = get_logger(__name__)


class AccessServiceRegistrationView(CreateAPIView, ViewSet):
    serializer_class = AccessCardServiceRegistrationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ServiceRegistration.objects.all()


class ParkingCardServiceRegistrationView(AccessServiceRegistrationView):
    serializer_class = ParkingCardServiceRegistrationSerializer
