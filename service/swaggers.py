from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiParameter

from service import serializers
from service.models import MyBaseServiceStatus, Service, Vehicle
from utils import format

SERVICE_HISTORY = {
    "description": "History of service registration",
    "request": None,
    "responses": {200: serializers.HistoryServiceRegistrationSerializer},
    "parameters": [
        OpenApiParameter(
            name="category",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Include services belong to a specific category",
            examples=[
                OpenApiExample(
                    "Example",
                    value="access | parking | resident",
                ),
            ],
        ),
        OpenApiParameter(
            name="status",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Include services with required status",
            examples=[
                OpenApiExample(
                    "Example",
                    value=format.format_enum_values(MyBaseServiceStatus.Status),
                ),
            ],
        ),
        OpenApiParameter(
            name="_status",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Exclude services with required status",
            examples=[
                OpenApiExample(
                    "Example",
                    value=format.format_enum_values(MyBaseServiceStatus.Status),
                ),
            ],
        ),
    ],
}

SERVICE_ACCESS_CARD = {
    "description": "Register access card service",
    "request": serializers.AccessCardServiceRegistrationSerializer,
    "responses": {200: serializers.AccessCardServiceRegistrationSerializer},
    "examples": [
        OpenApiExample(
            "Example",
            value={
                "relative": {
                    "relationship": "Vợ",
                    "personal_information": {
                        "citizen_id": "073256843212",
                        "phone_number": "0953253675",
                        "full_name": "Nguyen Thi B",
                        "date_of_birth": "2024-04-19",
                        "hometown": "TP.HCM",
                        "gender": "Nữ",
                    },
                }
            },
            request_only=True,
        ),
        OpenApiExample(
            "Example",
            value={
                "service": {
                    "id": format.format_enum_values(Service.ServiceType),
                    "name": "Thẻ ra vào",
                    "price": "55000",
                },
                "status": format.format_enum_values(MyBaseServiceStatus.Status),
            },
            response_only=True,
        ),
    ],
}

SERVICE_RESIDENT_CARD = {
    "description": "Register resident card service",
    "request": serializers.ResidentCardServiceRegistrationSerializer,
    "responses": {200: serializers.ResidentCardServiceRegistrationSerializer},
    "examples": [
        OpenApiExample(
            "Example",
            value={
                "relative": {
                    "relationship": "Vợ",
                    "personal_information": {
                        "citizen_id": "073256843212",
                        "phone_number": "0953253675",
                        "full_name": "Nguyen Thi B",
                        "date_of_birth": "2024-04-19",
                        "hometown": "TP.HCM",
                        "gender": "Nữ",
                    },
                },
                "room_number": "A-303",
            },
            request_only=True,
        ),
        OpenApiExample(
            "Example",
            value={
                "service": {
                    "id": format.format_enum_values(Service.ServiceType),
                    "name": "Thẻ cư dân",
                    "price": "55000",
                },
                "status": format.format_enum_values(MyBaseServiceStatus.Status),
            },
            response_only=True,
        ),
    ],
}

SERVICE_PARKING_CARD = {
    "description": "Register parking card service",
    "request": serializers.ParkingCardServiceRegistrationSerializer,
    "responses": {200: serializers.ParkingCardServiceRegistrationSerializer},
    "examples": [
        OpenApiExample(
            "Example",
            value={
                "relative": {
                    "relationship": "Vợ",
                    "personal_information": {
                        "citizen_id": "073256843212",
                        "phone_number": "0953253675",
                        "full_name": "Nguyen Thi B",
                        "date_of_birth": "2024-04-19",
                        "hometown": "TP.HCM",
                        "gender": "Nữ",
                    },
                },
                "room_number": "A-303",
                "vehicle": {
                    "license_plate": "30A91632",
                    "vehicle_type": format.format_enum_values(Vehicle.VehicleType),
                },
            },
            request_only=True,
        ),
        OpenApiExample(
            "Example",
            value={
                "service": {
                    "id": format.format_enum_values(Service.ServiceType),
                    "name": "Thẻ gửi xe",
                    "price": "250000",
                },
                "status": format.format_enum_values(MyBaseServiceStatus.Status),
            },
            response_only=True,
        ),
    ],
}

SERVICE_REISSUE = {
    "description": "Reissue service cards",
    "request": None,
    "responses": {200: OpenApiTypes.STR},
}
