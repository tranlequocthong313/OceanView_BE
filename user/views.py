import hashlib
import logging
import traceback

import requests
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.template.response import TemplateResponse
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_405_METHOD_NOT_ALLOWED,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from rest_framework.viewsets import ViewSet

from app import settings
from utils import email, sms, token

from .permissions import IsOwner
from .serializers import (
    ActiveUserSerializer,
    ForgotPasswordSerializer,
    LoginSerializer,
    ResetPasswordSerializer,
    UserSerializer,
)

log = logging.getLogger(__name__)


class UserView(ViewSet, GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = [
        IsAuthenticated,
        IsOwner,
    ]

    def get_queryset(self):
        return get_user_model().objects.all()

    """
    PATCH /users/<resdient_id>/active/
    """

    @action(
        methods=["patch"],
        url_path="active",
        detail=True,
        serializer_class=ActiveUserSerializer,
    )
    def active(self, request, pk):
        try:
            user = self.get_queryset().get(pk=pk)
            self.check_object_permissions(self.request, user)
            if user.is_active_user:
                return Response(
                    {"message": "User has already actived"}, status=HTTP_400_BAD_REQUEST
                )

            serializer = ActiveUserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                user = serializer.save()
                return Response(UserSerializer(user).data)
            else:
                log.error("Not provide enough data for active user")
                return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            log.error("User does not exist for active user")
            return Response(
                {"message": "User does not exist"}, status=HTTP_404_NOT_FOUND
            )

    """
    GET /users/current-user/
    """

    @action(methods=["get"], url_path="current", detail=False)
    def current_user(self, request):
        return Response(UserSerializer(request.user).data)

    """
    POST /users/login/
    """

    @action(
        methods=["post"],
        url_path="login",
        detail=False,
        permission_classes=[AllowAny],
        serializer_class=LoginSerializer,
    )
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid() is False:
            log.error("User login without resident id or password")
            return Response(
                {"message": "Resident ID and Password must not be empty"},
                HTTP_400_BAD_REQUEST,
            )

        payload = {
            **request.data,
            "grant_type": "password",
            "client_id": settings.CLIENT_ID,
            "client_secret": settings.CLIENT_SECRET,
        }

        r = requests.post(url="http://localhost:8000/o/token/", data=payload)

        if r.status_code == HTTP_200_OK:
            user = get_user_model().objects.get(pk=request.data.get("username"))
            data = {
                **UserSerializer(user).data,
                "token": r.json(),
            }
            log.info("User login successfully")
            return Response(data, HTTP_200_OK)
        elif r.status_code == HTTP_401_UNAUTHORIZED:
            log.error("User login failed")
            return Response(
                {"message": "Resident ID or Password is invalid"}, r.status_code
            )
        else:
            return Response(HTTP_500_INTERNAL_SERVER_ERROR)

    """
    POST /users/forgot-password/
    """

    @action(
        methods=["post"],
        url_path="forgot-password",
        detail=False,
        permission_classes=[AllowAny],
        serializer_class=ForgotPasswordSerializer,
    )
    def forgot_password(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = get_user_model().objects.get(pk=request.data.get("resident_id"))

                methods = ["sms"]
                if user.personal_information.email is not None:
                    methods.append("email")

                log.info(f"User reset password method: {methods}")
                return Response(
                    {"methods": methods},
                    HTTP_200_OK,
                )
            except ObjectDoesNotExist:
                log.error(f"User does not exist for reset password")
                return Response(
                    {"message": "User does not exist"},
                    HTTP_404_NOT_FOUND,
                )
        else:
            log.error(f"User does not provide resident id for reseting password")
            return Response(
                {"message": "Resident ID must not be empty"},
                HTTP_400_BAD_REQUEST,
            )

    """
    POST /users/send-reset-password/
    """

    @action(
        methods=["post"],
        url_path="send-reset-password",
        detail=False,
        permission_classes=[AllowAny],
    )
    def send_reset_password_link(self, request):
        try:
            resident_id = request.data.get("resident_id")
            user = get_user_model().objects.get(pk=resident_id)

            if user.personal_information.email is None:
                log.error(f"User are not allowed for using this method")
                return Response(
                    {"message": "User cannot use this method"},
                    HTTP_405_METHOD_NOT_ALLOWED,
                )
            else:
                reset_password_token = token.generate_token(str(resident_id))
                cache.set(
                    f"{str(resident_id)}",
                    hashlib.md5(str(reset_password_token).encode()).hexdigest(),
                    settings.RESET_PASSWORD_TOKEN_EXPIRE_TIME,
                )
                email.send_mail(
                    subject="Quên mật khẩu",
                    template="account/email/forgot_password",
                    recipient_list=[user.personal_information.email],
                    user=user,
                    token=reset_password_token,
                )
            log.info(f"Sent reset password link")
            return Response(
                {"token": "Sent reset password link"},
                HTTP_200_OK,
            )
        except ObjectDoesNotExist:
            log.error(f"User does not exist for sending reset password link")
            return Response(
                {"message": "User does not exist"},
                HTTP_404_NOT_FOUND,
            )
        except Exception:
            log.error(traceback.format_exc())
            return Response(
                {"message": "Something went wrong"},
                HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(
        methods=["post"],
        url_path="send-otp",
        detail=False,
        permission_classes=[AllowAny],
    )
    def send_otp(self, request):
        try:
            resident_id = request.data.get("resident_id")
            user = get_user_model().objects.get(pk=resident_id)

            sms.send_otp(
                to=user.personal_information.phone_number,
            )
            log.info(f"Sent reset password otp")
            return Response(
                {"message": "Sent reset password otp"},
                HTTP_200_OK,
            )
        except ObjectDoesNotExist:
            log.error(f"User does not exist for sending otp")
            return Response(
                {"message": "User does not exist"},
                HTTP_404_NOT_FOUND,
            )
        except Exception:
            log.error(traceback.format_exc())
            return Response(
                {"message": "Something went wrong"},
                HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(
        methods=["post"],
        url_path="verify-otp",
        detail=False,
        permission_classes=[AllowAny],
    )
    def verify_otp(self, request):
        try:
            resident_id = request.data.get("resident_id")
            otp = request.data.get("otp")
            user = get_user_model().objects.get(pk=resident_id)

            verified = sms.verify_otp(
                to=user.personal_information.phone_number,
                otp=otp,
            )
            if verified is False:
                log.error(f"User does not exist for sending otp")
                return Response(HTTP_401_UNAUTHORIZED)

            reset_password_token = token.generate_token(str(resident_id))
            cache.set(
                f"{str(resident_id)}",
                hashlib.md5(str(reset_password_token).encode()).hexdigest(),
                settings.RESET_PASSWORD_TOKEN_EXPIRE_TIME,
            )

            return Response(
                {"token": reset_password_token},
                HTTP_200_OK,
            )
        except ObjectDoesNotExist:
            return Response(
                {"message": "User does not exist"},
                HTTP_404_NOT_FOUND,
            )
        except Exception:
            log.error(traceback.format_exc())
            return Response(
                {"message": "Something went wrong"},
                HTTP_500_INTERNAL_SERVER_ERROR,
            )

    """
    GET /users/reset-password/
    POST /users/reset-password/
    """

    @action(
        methods=["post", "get"],
        detail=False,
        url_path="reset-password",
        serializer_class=ResetPasswordSerializer,
        permission_classes=[
            AllowAny,
        ],
    )
    def reset_password(self, request):
        reset_password_token = request.GET.get("token")
        if not reset_password_token:
            log.error(f"User does not provide token")
            return Response(status=HTTP_404_NOT_FOUND)

        payload = token.verify_token(
            reset_password_token,
            max_age=settings.RESET_PASSWORD_TOKEN_EXPIRE_TIME,
        )
        if not payload:
            log.error(f"Token is invalid")
            return Response(status=HTTP_401_UNAUTHORIZED)

        cached_token = cache.get(f"{payload}")
        if cached_token is False:
            log.error(f"Token is expired")
            return Response(status=HTTP_401_UNAUTHORIZED)

        hashed_token = hashlib.md5(str(reset_password_token).encode()).hexdigest()
        if hashed_token != cached_token:
            log.error(f"Token in cache not same as user token")
            return Response(status=HTTP_401_UNAUTHORIZED)

        if request.method == "GET":
            return self.render_reset_password_form(request, reset_password_token)

        return self.process_reset_password(request, payload)

    def render_reset_password_form(self, request, reset_password_token):
        return TemplateResponse(
            request,
            "account/reset_password.html",
            {"token": reset_password_token},
        )

    def process_reset_password(self, request, payload):
        new_password = request.data.get("password")
        confirm_new_password = request.data.get("confirm_password")

        if new_password != confirm_new_password:
            log.error(f"Passwords are not equal")
            return Response(
                {"error": "Passwords do not match"},
                status=HTTP_400_BAD_REQUEST,
            )

        user = get_user_model().objects.get(pk=payload)
        user.change_password(request.data.get("password"))
        cache.delete(f"{payload}")
        if user.personal_information.email is not None:
            current_datetime = timezone.now()
            formatted_date = current_datetime.strftime(
                "Ngày %d tháng %m năm %Y %I:%M:%S %p"
            )
            email.send_mail_async(
                subject="Thay đổi mật khẩu",
                template="account/email/confirm_reset_password",
                recipient_list=[user.personal_information.email],
                user=user,
                reset_at=formatted_date,
            )
        log.info(f"Reset password successfully")
        return Response(HTTP_200_OK)
