from django.urls import include, path
from rest_framework import routers

from .views import FCMTokenView, NotificationView

r = routers.DefaultRouter()
r.register("fcm-tokens", FCMTokenView, basename="fcm-token")
r.register("notifications", NotificationView, basename="notification")

urlpatterns = [path("", include(r.urls))]
