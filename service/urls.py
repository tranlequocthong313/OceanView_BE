from django.urls import include, path
from rest_framework import routers

from .views import AccessServiceRegistrationView, ParkingCardServiceRegistrationView

r = routers.DefaultRouter()
r.register("access-cards", AccessServiceRegistrationView, basename="access-card")
r.register("parking-cards", ParkingCardServiceRegistrationView, basename="parking-card")

urlpatterns = [
    path("", include(r.urls)),
]
