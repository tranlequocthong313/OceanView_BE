from drf_spectacular.utils import OpenApiExample

from service.models import Service, ServiceRegistration, VehicleInformation
from service.serializers import (
    AccessCardServiceRegistrationSerializer,
    ParkingCardServiceRegistrationSerializer,
)

SERVICE_ACCESS_CARD = {
    "description": "Register access card service",
    "request": AccessCardServiceRegistrationSerializer,
    "responses": {200: AccessCardServiceRegistrationSerializer},
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
                        "gender": "FEMALE",
                    },
                }
            },
            request_only=True,
        ),
        OpenApiExample(
            "Example",
            value={
                "service": {
                    "service_id": Service.ServiceType.ACCESS_CARD,
                    "name": "Thẻ ra vào",
                    "price": "55000",
                },
                "status": ServiceRegistration.Status.WAITING_FOR_APPROVAL,
            },
            response_only=True,
        ),
    ],
}

SERVICE_PARKING_CARD = {
    "description": "Register parking card service",
    "request": ParkingCardServiceRegistrationSerializer,
    "responses": {200: ParkingCardServiceRegistrationSerializer},
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
                        "gender": "FEMALE",
                    },
                },
                "room_number": "A-303",
                "vehicle_information": {
                    "license_plate": "30A91632",
                    "vehicle_type": VehicleInformation.VehicleType.MOTORBIKE,
                },
            },
            request_only=True,
        ),
        OpenApiExample(
            "Example",
            value={
                "service": {
                    "service_id": Service.ServiceType.MOTOR_PARKING_CARD,
                    "name": "Thẻ gửi xe",
                    "price": "250000",
                },
                "status": ServiceRegistration.Status.WAITING_FOR_APPROVAL,
            },
            response_only=True,
        ),
    ],
}
