from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from . import models, serializers


class FeedbackView(ModelViewSet):
    serializer_class = serializers.FeedbackSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "patch", "delete"]

    def get_queryset(self):
        queries = models.Feedback.objects.filter(deleted=False)
        q = self.request.query_params.get("q")
        if q:
            queries = queries.filter(title__icontains=q)

        return queries.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
