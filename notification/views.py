import traceback

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from firebase import topic
from user.permissions import NonAccessTokenPermissionMixin
from utils import get_logger

from . import models, serializers, swaggers

log = get_logger(__name__)


class FCMTokenView(NonAccessTokenPermissionMixin, CreateAPIView, ViewSet):
    queryset = models.FCMToken.objects.all()
    serializer_class = serializers.FCMTokenSerializer
    permission_classes = [IsAuthenticated]

    # TODO: validate tokens by sending tokens to a topic
    @extend_schema(**swaggers.NOTIFICATION_POST_FCM_TOKEN)
    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            fcm_token, created = serializer.save(user=request.user)
            # NOTE: Avoid sending too much information about tokens to clients
            if created:
                log.info(
                    f"Saved fcm token {fcm_token.token} of {self.request.user} successfully"
                )
            else:
                log.info(
                    f"Updated fcm token {fcm_token.token} of {self.request.user} successfully"
                )
            if (
                request.user.is_staff
                and serializer.validated_data["device_type"] == "WEB"
            ):
                topic.subscribe_to_topic(fcm_tokens=fcm_token.token, topic="admin")
            else:
                topic.subscribe_to_topic(fcm_tokens=fcm_token.token, topic="resident")
            response = Response("Saved fcm token successfully", status.HTTP_201_CREATED)
            response.set_cookie("fcm_token", fcm_token.token)
            return response
        except Exception:
            log.error(traceback.format_exc())
            return Response(
                "Internal server error :(", status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class NotificationView(NonAccessTokenPermissionMixin, ListAPIView, ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.ClientNotificationSerializer

    def get_queryset(self):
        return (
            models.Notification.objects.filter(recipient=self.request.user)
            .order_by("-id")
            .all()
        )

    def get_serializer_class(self):
        if self.request.GET.get("source") == "admin":
            return serializers.AdminNotificationSerializer
        return super().get_serializer_class()

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data["badge"] = request.user.number_of_unread_notifications
        return response

    @extend_schema(**swaggers.NOTIFICATION_READ)
    @action(
        detail=False,
        methods=["POST"],
        serializer_class=serializers.ReadNotificationSerializer,
    )
    def read(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.get_queryset().filter(
            content_id=serializer.validated_data["content_id"]
        ).first().read()
        log.info(f"{request.user} read notification successfully")
        return Response("Read successfully", status.HTTP_201_CREATED)
