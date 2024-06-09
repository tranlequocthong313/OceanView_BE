from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import InboxViewSet, MessageViewSet

router = DefaultRouter()
router.register("inboxes", InboxViewSet, basename="inbox")
router.register(
    "inboxes/(?P<inbox_id>[^/.]+)/messages",
    MessageViewSet,
    basename="message",
)

urlpatterns = [
    path("", include(router.urls)),
]
