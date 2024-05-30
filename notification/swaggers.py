from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample

from notification.serializers import FCMTokenSerializer, ReadNotificationSerializer
from utils import format

from .models import FCMToken

NOTIFICATION_POST_FCM_TOKEN = {
    "request": FCMTokenSerializer,
    "responses": {201: OpenApiTypes.STR},
    "examples": [
        OpenApiExample(
            "Example",
            value={
                "token": "string",
                "device_type": format.format_enum_values(FCMToken.DeviceType),
            },
            request_only=True,
        ),
        OpenApiExample(
            "Example",
            value="Created successfully",
            response_only=True,
        ),
    ],
}

NOTIFICATION_READ = {
    "request": ReadNotificationSerializer,
    "responses": {200: OpenApiTypes.STR},
    "examples": [
        OpenApiExample(
            "Example",
            value={
                "content_id": 1,
            },
            request_only=True,
        ),
    ],
}
