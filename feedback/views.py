from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from notification.manager import NotificationManager
from notification.types import EntityType

from . import models, serializers, swaggers


class FeedbackView(CreateAPIView, ViewSet):
    serializer_class = serializers.FeedbackSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queries = models.Feedback.objects.filter(deleted=False)
        if q := self.request.query_params.get("q"):
            queries = queries.filter(title__icontains=q)

        return queries.order_by("-id")

    def get_serializer(self, *args, **kwargs):
        kwargs["context"] = {"user": self.request.user}
        return super().get_serializer(*args, **kwargs)

    def perform_create(self, serializer):
        return serializer.save()

    @extend_schema(**swaggers.FEEDBACK)
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        feedback = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        NotificationManager.create_notification(
            entity=feedback, entity_type=EntityType.FEEDBACK_POST, sender=request.user
        )
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )
