from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from notification.manager import NotificationManager
from notification.types import EntityType

from . import models, serializers, swaggers


class FeedbackView(ModelViewSet):
    serializer_class = serializers.FeedbackSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "patch", "delete"]

    def get_queryset(self):
        queries = models.Feedback.objects.filter(deleted=False)
        if q := self.request.query_params.get("q"):
            queries = queries.filter(title__icontains=q)

        return queries.order_by("-id")

    def get_serializer(self, *args, **kwargs):
        kwargs["context"] = {"user": self.request.user}
        return super().get_serializer(*args, **kwargs)

    @extend_schema(**swaggers.FEEDBACK)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(**swaggers.FEEDBACK)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

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

    @extend_schema(**swaggers.FEEDBACK)
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
