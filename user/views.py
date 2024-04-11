import hashlib
import logging
import traceback

import requests
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.template.response import TemplateResponse
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from app import settings
from user.models import User
from utils import email, http, sms, token

from .permissions import IsOwner
from .serializers import (
    ActiveUserSerializer,
    ForgotPasswordSerializer,
    LoginSerializer,
    LogonUserSerializer,
    ResetPasswordMethodSerializer,
    ResetPasswordSerializer,
    TokenResetPasswordSerializer,
    UserSerializer,
    VerifyOTPSerializer,
)

log = logging.getLogger(__name__)


class UserView(ViewSet, GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.all()

    @extend_schema(
        request=ActiveUserSerializer,
        responses={200: UserSerializer},
    )
    @action(
        methods=["patch"],
        url_path="active",
        detail=True,
        serializer_class=ActiveUserSerializer,
        permission_classes=[IsOwner],
    )
    def active(self, request, pk):
        try:
            user = self.get_queryset().get(pk=pk)
            self.check_object_permissions(self.request, user)
            if user.is_active_user:
                return Response(
                    {"message": "User has already actived"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = self.serializer_class(user, data=request.data, partial=True)
            if serializer.is_valid():
                user = serializer.save()
                return Response(UserSerializer(user).data)
            else:
                log.error("Not provide enough data for active user")
                return Response(
                    serializer.error_messages, status=status.HTTP_400_BAD_REQUEST
                )
        except ObjectDoesNotExist:
            log.error("User does not exist for active user")
            return Response(
                {"message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND
            )

    @extend_schema(
        request=None,
        responses={200: UserSerializer},
    )
    @action(
        methods=["get"],
        url_path="current",
        detail=False,
        serializer_class=UserSerializer,
    )
    def current_user(self, request):
        return Response(self.serializer_class(request.user).data)

    @extend_schema(
        request=LoginSerializer,
        responses={200: LogonUserSerializer},
    )
    @action(
        methods=["post"],
        url_path="login",
        detail=False,
        permission_classes=[AllowAny],
        serializer_class=LoginSerializer,
    )
    def login(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            log.error("User login without resident id or password")
            return Response(
                {"message": "Resident ID and Password must not be empty"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payload = {
            **request.data,
            "grant_type": "password",
            "client_id": settings.CLIENT_ID,
            "client_secret": settings.CLIENT_SECRET,
        }

        r = requests.post(url="http://localhost:8000/o/token/", data=payload)

        if r.status_code == status.HTTP_200_OK:
            user = self.get_queryset().get(pk=serializer.validated_data["username"])
            data = {
                **UserSerializer(user).data,
                "token": r.json(),
            }
            log.info("User login successfully")
            return Response(data, status=status.HTTP_200_OK)
        elif r.status_code == status.HTTP_401_UNAUTHORIZED:
            log.error("User login failed")
            return Response(
                {"message": "Resident ID or Password is invalid"}, r.status_code
            )
        else:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        request=ForgotPasswordSerializer,
        responses={200: ResetPasswordMethodSerializer},
    )
    @action(
        methods=["post"],
        url_path="forgot-password",
        detail=False,
        permission_classes=[AllowAny],
        serializer_class=ForgotPasswordSerializer,
    )
    def forgot_password(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            resident_id = serializer.validated_data["resident_id"]
            try:
                user = self.get_queryset().get(pk=resident_id)

                methods = ["sms"]
                if user.personal_information.email is not None:
                    methods.append("email")

                log.info(f"User reset password method: {methods}")
                return Response(
                    {"methods": methods},
                    status=status.HTTP_200_OK,
                )
            except ObjectDoesNotExist:
                log.error(f"User does not exist for reset password")
                return Response(
                    {"message": "User does not exist"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            log.error(f"User does not provide resident id for reseting password")
            return Response(
                {"message": "Resident ID must not be empty"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @extend_schema(
        request=ForgotPasswordSerializer,
        responses=None,
    )
    @action(
        methods=["post"],
        url_path="send-reset-password-link",
        detail=False,
        permission_classes=[AllowAny],
        serializer_class=ForgotPasswordSerializer,
    )
    def send_reset_password_link(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            resident_id = serializer.validated_data["resident_id"]
            try:
                user = self.get_queryset().get(pk=resident_id)

                if user.personal_information.email is None:
                    log.error(f"User are not allowed for using this method")
                    return Response(
                        {"message": "User cannot use this method"},
                        status=status.HTTP_405_METHOD_NOT_ALLOWED,
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
                    {"message": "Sent reset password link"},
                    status=status.HTTP_200_OK,
                )
            except ObjectDoesNotExist:
                log.error(f"User does not exist for sending reset password link")
                return Response(
                    {"message": "User does not exist"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            except Exception:
                log.error(traceback.format_exc())
                return Response(
                    {"message": "Something went wrong"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        else:
            return http.respond_serializer_error(serializer)

    @extend_schema(
        request=ForgotPasswordSerializer,
        responses=None,
    )
    @action(
        methods=["post"],
        url_path="send-otp",
        detail=False,
        permission_classes=[AllowAny],
        serializer_class=ForgotPasswordSerializer,
    )
    def send_otp(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            resident_id = serializer.validated_data["resident_id"]
            try:
                user = self.get_queryset().get(pk=resident_id)

                sms.send_otp(
                    to=user.personal_information.phone_number,
                )

                log.info(f"Sent reset password otp")
                return Response(
                    {"message": "Sent reset password otp"},
                    status=status.HTTP_200_OK,
                )
            except ObjectDoesNotExist:
                log.error(f"User does not exist for sending otp")
                return Response(
                    {"message": "User does not exist"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            except Exception:
                log.error(traceback.format_exc())
                return Response(
                    {"message": "Something went wrong"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        else:
            return http.respond_serializer_error(serializer)

    @extend_schema(
        request=VerifyOTPSerializer,
        responses={200: TokenResetPasswordSerializer},
    )
    @action(
        methods=["post"],
        url_path="verify-otp",
        detail=False,
        permission_classes=[AllowAny],
        serializer_class=VerifyOTPSerializer,
    )
    def verify_otp(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            resident_id = serializer.validated_data["resident_id"]
            otp = serializer.validated_data["otp"]
            try:
                user = self.get_queryset().get(pk=resident_id)

                verified = sms.verify_otp(
                    to=user.personal_information.phone_number,
                    otp=otp,
                )
                if verified is False:
                    log.error(f"User does not exist for sending otp")
                    return Response(status=status.HTTP_401_UNAUTHORIZED)

                reset_password_token = token.generate_token(str(resident_id))
                cache.set(
                    f"{str(resident_id)}",
                    hashlib.md5(str(reset_password_token).encode()).hexdigest(),
                    settings.RESET_PASSWORD_TOKEN_EXPIRE_TIME,
                )

                return Response(
                    {"token": reset_password_token},
                    status=status.HTTP_200_OK,
                )
            except ObjectDoesNotExist:
                return Response(
                    {"message": "User does not exist"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            except Exception:
                log.error(traceback.format_exc())
                return Response(
                    {"message": "Something went wrong"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        else:
            return http.respond_serializer_error(serializer)

    def validate_reset_password_token(self, reset_password_token):
        if not reset_password_token:
            log.error(f"User does not provide token")
            return False, Response(status=status.HTTP_400_BAD_REQUEST)

        payload = token.verify_token(
            reset_password_token,
            max_age=settings.RESET_PASSWORD_TOKEN_EXPIRE_TIME,
        )
        if not payload:
            log.error(f"Token is invalid")
            return False, Response(status=status.HTTP_401_UNAUTHORIZED)

        cached_token = cache.get(f"{payload}")
        if cached_token is False:
            log.error(f"Token is expired")
            return False, Response(status=status.HTTP_401_UNAUTHORIZED)

        hashed_token = hashlib.md5(str(reset_password_token).encode()).hexdigest()
        if hashed_token != cached_token:
            log.error(f"Token in cache not same as user token")
            return False, Response(status=status.HTTP_401_UNAUTHORIZED)

        return True, payload

    @extend_schema(request=None, responses=None, methods=["GET"])
    @extend_schema(request=ResetPasswordSerializer, responses=None, methods=["POST"])
    @action(
        methods=["get", "post"],
        detail=False,
        url_path="reset-password",
        permission_classes=[AllowAny],
    )
    def reset_password(self, request):
        if request.method == "GET":
            return self.get_reset_password_form(request)
        elif request.method == "POST":
            return self.post_reset_password(request)

    def get_reset_password_form(self, request):
        reset_password_token = request.GET.get("token")
        is_valid, payload_or_response = self.validate_reset_password_token(
            reset_password_token
        )
        if not is_valid:
            return payload_or_response

        return self.render_reset_password_form(request, reset_password_token)

    def render_reset_password_form(self, request, reset_password_token):
        return TemplateResponse(
            request,
            "account/reset_password.html",
            {"token": reset_password_token},
        )

    def post_reset_password(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            reset_password_token = request.GET.get("token")
            is_valid, payload_or_response = self.validate_reset_password_token(
                reset_password_token
            )
            if not is_valid:
                return payload_or_response

            return self.process_reset_password(
                serializer.validated_data["password"], payload_or_response
            )
        else:
            return http.respond_serializer_error(serializer)

    def process_reset_password(self, password, resident_id):
        user = self.get_queryset().get(pk=resident_id)
        user.change_password(password)
        cache.delete(f"{resident_id}")
        self.send_reset_password_confirm_mail(user)
        log.info(f"Reset password successfully")
        return Response(status=status.HTTP_200_OK)

    def send_reset_password_confirm_mail(self, user):
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
