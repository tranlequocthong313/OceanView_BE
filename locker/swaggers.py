from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiParameter

from utils import format

from . import serializers
from .models import Item

LOCKER_LIST = {
    "description": "Get lockers",
    "request": None,
    "responses": {200: serializers.LockerSerializer},
    "parameters": [
        OpenApiParameter(
            name="q",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Search lockers by resident id, citizen id, phone number, email",
            examples=[
                OpenApiExample(
                    "Example",
                    value="ngvana@gmail.com",
                ),
            ],
        ),
    ],
}

ITEM_LIST = {
    "description": "Get items from a locker",
    "request": None,
    "responses": {200: serializers.ItemSerializer},
    "parameters": [
        OpenApiParameter(
            name="q",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Search items by their name",
            examples=[
                OpenApiExample(
                    "Example",
                    value="Iphone 15 Pro Max",
                ),
            ],
        ),
        OpenApiParameter(
            name="status",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Include items with required status",
            examples=[
                OpenApiExample(
                    "Example",
                    value=format.format_enum_values(Item.ItemStatus),
                ),
            ],
        ),
        OpenApiParameter(
            name="_status",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Exclude items with required status",
            examples=[
                OpenApiExample(
                    "Example",
                    value=format.format_enum_values(Item.ItemStatus),
                ),
            ],
        ),
    ],
}
