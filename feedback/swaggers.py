from drf_spectacular.utils import OpenApiExample

from . import serializers

INVOICE = {
    "request": serializers.FeedbackSerializer,
    "responses": {200: serializers.FeedbackSerializer},
    "examples": [
        OpenApiExample(
            "Example",
            value={
                "title": "Không có nước",
                "content": "Phòng A101 không có nước",
                "type": "COMPLAIN | QUESTION | SUPPORT | OTHER",
            },
        )
    ],
}
