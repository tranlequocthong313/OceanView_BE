from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample

from utils import format

from . import serializers
from .models import Feedback

INVOICE = {
    "request": serializers.FeedbackSerializer,
    "responses": {200: serializers.FeedbackSerializer},
    "examples": [
        OpenApiExample(
            "Example",
            value={
                "title": "Không có nước",
                "content": "Phòng A101 không có nước",
                "type": format.format_enum_values(Feedback.FeedbackType),
                "image": str(),
            },
        )
    ],
}
