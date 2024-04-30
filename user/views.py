import hashlib
import traceback

import requests
from django.core.cache import cache
from django.db.models import Q
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
from notification.models import FCMToken
from user.models import User
from utils import email, get_logger, http, sms, token

from . import serializers, swaggers
from .permissions import IsOwner

log = get_logger(__name__)


class UserView(ViewSet, GenericAPIView):
    serializer_class = serializers.UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.all()

    @extend_schema(**swaggers.USER_ACTIVE)
    @action(
        methods=["patch"],
        url_path="active",
        detail=False,
        serializer_class=serializers.ActiveUserSerializer,
        permission_classes=[IsAuthenticated, IsOwner],
    )
    def active(self, request):
        self.check_object_permissions(request=request, obj=request.user)
        if request.user.is_active_user:
            return Response(
                "User has already active",
                status=status.HTTP_400_BAD_REQUEST,
            )
        log.info("{request.user} can active account")

        serializer = self.serializer_class(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = serializer.save()
            log.info("Active {request.user} account")
            return Response(serializers.UserSerializer(user).data)
        except Exception:
            log.error("Server error", traceback.format_exc())
            return Response(
                "Something went wrong", status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(**swaggers.USER_CURRENT)
    @action(
        methods=["get"],
        url_path="current",
        detail=False,
        serializer_class=serializers.UserSerializer,
    )
    def current_user(self, request):
        return Response(self.serializer_class(request.user).data)

    @extend_schema(**swaggers.USER_LOGIN)
    @action(
        methods=["post"],
        url_path="login",
        detail=False,
        permission_classes=[AllowAny],
        serializer_class=serializers.LoginSerializer,
    )
    def login(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        payload = {
            **request.data,
            "grant_type": "password",
            "client_id": settings.CLIENT_ID,
            "client_secret": settings.CLIENT_SECRET,
        }

        r = requests.post(url=f"{settings.HOST}/o/token/", data=payload)
        log.info("Requested to Oauth2 successfully")

        if r.ok:
            user = self.get_queryset().get(pk=serializer.validated_data["username"])
            log.info("User login successfully")
            return Response(
                {
                    **serializers.UserSerializer(user).data,
                    "token": r.json(),
                },
                status=status.HTTP_200_OK,
            )
        elif r.status_code != status.HTTP_500_INTERNAL_SERVER_ERROR:
            log.error("User login failed", r.json())
            return Response("Resident ID or Password is wrong", r.status_code)
        else:
            log.error(traceback.format_exc())
            return Response(
                "Something went wrong", status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(**swaggers.USER_REFRESH_TOKEN)
    @action(
        methods=["post"],
        url_path="refresh-token",
        detail=False,
        permission_classes=[AllowAny],
        serializer_class=serializers.RefreshTokenSerializer,
    )
    def refresh_token(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        payload = {
            **request.data,
            "grant_type": "refresh_token",
            "client_id": settings.CLIENT_ID,
            "client_secret": settings.CLIENT_SECRET,
        }
        r = requests.post(url=f"{settings.HOST}/o/token/", data=payload)
        log.info("Requested to Oauth2 successfully")

        if r.ok:
            log.info("Refresh token successfully")
            return Response(
                r.json(),
                status=status.HTTP_200_OK,
            )
        elif r.status_code != status.HTTP_500_INTERNAL_SERVER_ERROR:
            log.error("Refresh token failed", r.json())
            return Response("Refresh token failed", r.status_code)
        else:
            log.error(traceback.format_exc())

            return Response(
                "Something went wrong", status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(**swaggers.USER_FORGOT_PASSWORD)
    @action(
        methods=["post"],
        url_path="forgot-password",
        detail=False,
        permission_classes=[AllowAny],
        serializer_class=serializers.ForgotPasswordSerializer,
    )
    def forgot_password(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user_identifier = serializer.validated_data["user_identifier"]
            user = (
                self.get_queryset()
                .filter(
                    Q(personal_information__phone_number=user_identifier)
                    | Q(personal_information__email=user_identifier)
                )
                .first()
            )
            if user is None:
                log.error("User does not exist for reset password")
                return Response(
                    "User does not exist", status=status.HTTP_404_NOT_FOUNDe
                )

            log.info(f"Resetting password for {user}")
            return Response(
                serializers.MethodForResetPasswordSerializer(
                    user.personal_information
                ).data,
                status=status.HTTP_200_OK,
            )
        except Exception:
            log.error(traceback.format_exc())
            return Response(
                "Something went wrong",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(**swaggers.USER_SEND_RESET_PASSWORD_LINK)
    @action(
        methods=["post"],
        url_path="email",
        detail=False,
        permission_classes=[AllowAny],
        serializer_class=serializers.SendResetPasswordLinkSerializer,
    )
    def send_reset_password_link(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = (
            self.get_queryset()
            .filter(personal_information__email=serializer.validated_data["email"])
            .first()
        )

        if user is None:
            log.error("User does not exist for sending reset password link")
            return Response(
                "User does not exist",
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            reset_password_token = token.generate_token(str(user.resident_id))
            log.info("Generated token")
            cache.set(
                f"{str(user.resident_id)}",
                hashlib.md5(str(reset_password_token).encode()).hexdigest(),
                settings.RESET_PASSWORD_TOKEN_EXPIRE_TIME,
            )
            log.info("Saved token to redis")
            email.send_mail(
                subject="Quên mật khẩu",
                template="account/email/forgot_password",
                recipient_list=[user.personal_information.email],
                user=user,
                link=f"{settings.HOST}/users/password/?token={reset_password_token}",
            )
            log.info("Sent reset password link")
            return Response(
                "Sent reset password link",
                status=status.HTTP_200_OK,
            )
        except Exception:
            log.error(traceback.format_exc())
            return Response(
                "Something went wrong",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(**swaggers.USER_SEND_OTP)
    @action(
        methods=["post"],
        url_path="otp",
        detail=False,
        permission_classes=[AllowAny],
        serializer_class=serializers.SendOTPSerializer,
    )
    def send_otp(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = (
                self.get_queryset()
                .filter(
                    personal_information__phone_number=serializer.validated_data[
                        "phone_number"
                    ]
                )
                .first()
            )

            if user is None:
                log.error("User does not exist for sending otp")
                return Response(
                    "User does not exist",
                    status=status.HTTP_404_NOT_FOUND,
                )

            verification = sms.send_otp(
                to=user.personal_information.phone_number,
            )
            ip = str(http.get_client_ip(request))
            cache.set(ip, 1, timeout=settings.RATE_LIMIT_EXPIRE_TIME)

            log.info(f"Verification {verification}")
            log.info(f"Sent reset password otp to {user}")
            return Response(
                "Sent reset password otp",
                status=status.HTTP_200_OK,
            )
        except Exception:
            log.error(traceback.format_exc())
            return Response(
                "Something went wrong",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(**swaggers.USER_VERIFY_OTP)
    @action(
        methods=["post"],
        url_path="otp-verification",
        detail=False,
        permission_classes=[AllowAny],
        serializer_class=serializers.VerifyOTPSerializer,
    )
    def verify_otp(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data["phone_number"]
        otp = serializer.validated_data["otp"]
        try:
            user = (
                self.get_queryset()
                .filter(personal_information__phone_number=phone_number)
                .first()
            )
            if user is None:
                log.error("User does not exist")
                return Response(
                    "User does not exist",
                    status=status.HTTP_404_NOT_FOUND,
                )

            verified = sms.verify_otp(
                to=phone_number,
                otp=otp,
            )
            if verified is False:
                log.error(f"Verify OTP failed {user}")
                return Response("OTP is invalid", status=status.HTTP_401_UNAUTHORIZED)

            reset_password_token = token.generate_token(str(user.resident_id))
            log.info("Generated token")
            cache.set(
                f"{str(user.resident_id)}",
                hashlib.md5(str(reset_password_token).encode()).hexdigest(),
                settings.RESET_PASSWORD_TOKEN_EXPIRE_TIME,
            )
            log.info("Saved token to redis")
            log.info("Verified OTP successfully")

            return Response(
                {"token": reset_password_token},
                status=status.HTTP_200_OK,
            )
        except Exception:
            log.error(traceback.format_exc())
            return Response(
                "Something went wrong",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def validate_reset_password_token(self, reset_password_token):
        if not reset_password_token:
            log.error("User does not provide token")
            return False, Response(status=status.HTTP_400_BAD_REQUEST)

        payload = token.verify_token(
            reset_password_token,
            max_age=settings.RESET_PASSWORD_TOKEN_EXPIRE_TIME,
        )
        if not payload:
            log.error("Token is invalid or expired")
            return False, Response(status=status.HTTP_401_UNAUTHORIZED)

        cached_token = cache.get(f"{payload}")
        if cached_token is False:
            log.error("Token does not exist in cache")
            return False, Response(status=status.HTTP_401_UNAUTHORIZED)

        hashed_token = hashlib.md5(str(reset_password_token).encode()).hexdigest()
        if hashed_token != cached_token:
            log.error("Token in cache not same as user token")
            return False, Response(status=status.HTTP_401_UNAUTHORIZED)

        log.info("Token is valid")
        return True, payload

    @extend_schema(**swaggers.USER_RESET_PASSWORD_GET)
    @extend_schema(**swaggers.USER_RESET_PASSWORD_POST)
    @action(
        methods=["get", "post"],
        detail=False,
        url_path="password",
        permission_classes=[AllowAny],
        serializer_class=serializers.ResetPasswordSerializer,
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
            {"link": f"{settings.HOST}/users/password/?token={reset_password_token}"},
        )

    def post_reset_password(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            reset_password_token = request.GET.get("token")
            is_valid, payload_or_response = self.validate_reset_password_token(
                reset_password_token
            )
            if not is_valid:
                return payload_or_response

            return self.process_reset_password(
                serializer.validated_data["password"], payload_or_response
            )
        except Exception:
            log.error(traceback.format_exc())
            return Response(
                "Something went wrong",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def process_reset_password(self, password, resident_id):
        user = self.get_queryset().get(pk=resident_id)
        user.change_password(password)
        cache.delete(f"{resident_id}")
        log.info("Updated password")
        self.send_reset_password_confirm_mail(user)
        log.info("Reset password successfully")
        return Response("Reset password successfully", status=status.HTTP_200_OK)

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

    @extend_schema(**swaggers.USER_LOGOUT)
    @action(
        methods=["post"],
        url_path="logout",
        detail=False,
        permission_classes=[IsAuthenticated],
        serializer_class=serializers.LogoutSerializer,
    )
    def logout(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        log.debug(
            f"logout token {http.get_bearer_token(request.META['HTTP_AUTHORIZATION'])}"
        )
        payload = {
            "token": http.get_bearer_token(request.META["HTTP_AUTHORIZATION"]),
            "client_id": settings.CLIENT_ID,
            "client_secret": settings.CLIENT_SECRET,
        }

        r = requests.post(
            url=f"{settings.HOST}/o/revoke_token/",
            data=payload,
        )
        log.info("Requested to Oauth2 successfully")

        if r.ok:
            print(serializer.validated_data)
            if (
                "fcm_token" in serializer.validated_data
                and serializer.validated_data["fcm_token"] is not None
            ):
                FCMToken.objects.filter(
                    token=serializer.validated_data["fcm_token"],
                    user=request.user,
                    device_type=serializer.validated_data["device_type"],
                ).delete()
            response = Response(
                status=status.HTTP_204_NO_CONTENT,
            )
            log.info("User logout successfully")
            return response
        else:
            log.error(traceback.format_exc())
            return Response(
                "Something went wrong", status.HTTP_500_INTERNAL_SERVER_ERROR
            )
