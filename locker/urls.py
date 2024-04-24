from django.urls import include, path
from rest_framework import routers

from .views import ItemView, LockerView

r = routers.DefaultRouter()
r.register("lockers", LockerView, basename="locker")
r.register(
    "lockers/(?P<locker_id>[^/.]+)/items",
    ItemView,
    basename="item",
)

urlpatterns = [
    path("", include(r.urls)),
]
