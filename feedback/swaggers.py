from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiParameter

from utils import format

from . import models, serializers

INVOICE = {
    "request": serializers.FeedbackSerializer,
    "responses": {200: serializers.FeedbackSerializer},
    "examples": [
        OpenApiExample(
            "Example",
            value={
                "title": "Không có nước",
                "content": "Phòng A101 không có nước",
                "type": "COMPALIN | QUESTION | SUPPORT | OTHER",
                "image": "string",
            },
        )
    ],
}
