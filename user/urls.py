from django.urls import include, path
from rest_framework import routers

from .views import UserView

r = routers.DefaultRouter()
r.register("users", UserView, basename="user")

urlpatterns = [
    path("", include(r.urls)),
]
