from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ViewSet

from guide.models import Guide, GuideCategory
from guide.serializers import (
    GuideCategorySerializer,
    GuideSerializer,
)


class GuideCategoryView(ListAPIView, RetrieveAPIView, ViewSet):
    queryset = GuideCategory.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = "category_id"
    serializer_class = GuideCategorySerializer


class GuideView(ListAPIView, RetrieveAPIView, ViewSet):
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = "guide_id"
    serializer_class = GuideSerializer

    def get_queryset(self):
        return Guide.objects.filter(category_id=self.kwargs["category_id"]).all()
