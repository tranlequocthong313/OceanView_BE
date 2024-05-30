from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiParameter

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

NOTIFICATION_LIST = {
    "request": ReadNotificationSerializer,
    "responses": {200: OpenApiTypes.STR},
    "parameters": [
        OpenApiParameter(
            name="source",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Notification for",
            examples=[
                OpenApiExample(
                    "Example",
                    value="admin",
                ),
            ],
        ),
    ],
    "examples": [
        OpenApiExample(
            "Example",
            value={
                "results": [
                    {
                        "id": 0,
                        "has_been_read": True,
                        "message": "string",
                        "content": {
                            "id": 0,
                            "entity_type": "SERVICE_REGISTER",
                            "entity_id": "string",
                            "image": "string",
                        },
                        "created_date": "2024-05-30T12:44:30.105Z",
                        "updated_date": "2024-05-30T12:44:30.105Z",
                    }
                ],
                "badge": 0,
            },
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
