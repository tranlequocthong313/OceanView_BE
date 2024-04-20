from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiParameter

from user.models import User
from user.serializers import (
    ActiveUserSerializer,
    LoginSerializer,
    LogonUserSerializer,
    MethodForResetPasswordSerializer,
    ResetPasswordSerializer,
    TokenResetPasswordSerializer,
    UserSerializer,
    VerifyOTPSerializer,
)
from utils import format

user_response_example = {
    "apartment_set": ["A-101", "B-202"],
    "personal_information": {
        "citizen_id": "072953212436",
        "email": "nguyenvana@gmail.com",
        "phone_number": "0938295384",
        "created_date": "2024-04-19T15:40:18.222Z",
        "updated_date": "2024-04-19T15:40:18.222Z",
        "full_name": "Nguyen Van A",
        "date_of_birth": "2024-04-19",
        "hometown": "TP.HCM",
        "gender": "Nam",
    },
    "avatar": "https://res.cloudinary.com/diojasks1/image/upload/v1713417878/wgbqdyjfedr2mu8fgkoq.jpg",
    "resident_id": "240269",
    "is_staff": False,
    "is_superuser": False,
    "status": format.format_enum_values(User.Status),
    "issued_by": "240001",
}

USER_ACTIVE = {
    "description": "Activate resident account by uploading avatar and new password",
    "request": ActiveUserSerializer,
    "responses": {200: ActiveUserSerializer},
    "examples": [
        OpenApiExample(
            "Example",
            value={
                "avatar": "https://res.cloudinary.com/diojasks1/image/upload/v1713417878/wgbqdyjfedr2mu8fgkoq.jpg",
                "status": User.Status.ACTIVE,
            },
            response_only=True,
        )
    ],
}

USER_CURRENT = {
    "description": "Get current authenticated user",
    "request": None,
    "responses": {200: UserSerializer},
    "examples": [
        OpenApiExample(
            "Example",
            value=user_response_example,
            response_only=True,
        )
    ],
}

USER_LOGIN = {
    "description": "Login",
    "request": LoginSerializer,
    "responses": {200: LogonUserSerializer},
    "examples": [
        OpenApiExample(
            "Example",
            value={"username": "240265", "password": "mypassword123"},
            request_only=True,
        ),
        OpenApiExample(
            "Example",
            value={
                **user_response_example,
                "token": {
                    "access_token": "233tBiWpUQ8W9O5FwHJ1mGH85RVRCI",
                    "expires_in": 36000,
                    "token_type": "Bearer",
                    "scope": "read write",
                    "refresh_token": "GsiUVpcAVe0MuRf9HFlYYT9DMPuqq1",
                },
            },
            response_only=True,
        ),
    ],
}

USER_FORGOT_PASSWORD = {
    "description": "Checks if the user exists and returns possible methods to reset the password",
    "responses": {200: MethodForResetPasswordSerializer},
    "examples": [OpenApiExample("Example", value=["sms", "email"])],
}

USER_SEND_RESET_PASSWORD_LINK = {
    "description": "Send reset link to email to reset password",
    "request": None,
    "responses": {200: OpenApiTypes.STR},
    "examples": [OpenApiExample("Example", value="Sent reset password link")],
}

USER_SEND_OTP = {
    "description": "Send otp to sms to reset password",
    "request": None,
    "responses": {200: OpenApiTypes.STR},
    "examples": [OpenApiExample("Example", value="Sent reset password otp")],
}

USER_VERIFY_OTP = {
    "description": "Verify otp",
    "request": VerifyOTPSerializer,
    "responses": {200: TokenResetPasswordSerializer},
    "examples": [
        OpenApiExample(
            "Example",
            value={"resident_id": "240269", "otp": "943245"},
            request_only=True,
        ),
        OpenApiExample(
            "Example",
            value={"token": "GsiUVpcAVe0MuRf9HFlYYT9DMPuqq1"},
            response_only=True,
        ),
    ],
}

user_reset_password_params = [
    OpenApiParameter(
        name="token",
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        description="Token to verify reset password session",
        examples=[
            OpenApiExample("Example", value="233tBiWpUQ8W9O5FwHJ1mGH85RVRCI"),
        ],
    ),
]


USER_RESET_PASSWORD_GET = {
    "methods": ["GET"],
    "request": None,
    "responses": None,
    "parameters": user_reset_password_params,
}

USER_RESET_PASSWORD_POST = {
    "methods": ["POST"],
    "description": "Reset password",
    "request": ResetPasswordSerializer,
    "responses": {200: OpenApiTypes.STR},
    "parameters": user_reset_password_params,
    "examples": [
        OpenApiExample(
            "Example", value="Reset password successfully", response_only=True
        ),
        OpenApiExample(
            "Example",
            value={
                "password": "mynewpassword123",
                "confirm_password": "mynewpassword123",
            },
            request_only=True,
        ),
    ],
}
