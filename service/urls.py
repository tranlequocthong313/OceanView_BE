from django.urls import include, path
from rest_framework import routers

from .views import ServiceRegistrationView

r = routers.DefaultRouter()
r.register("services", ServiceRegistrationView, basename="service")

urlpatterns = [
    path("", include(r.urls)),
]
