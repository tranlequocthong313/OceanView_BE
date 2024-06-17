from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ViewSet

from news.models import News, NewsCategory
from news.serializers import (
    NewsCategorySerializer,
    NewsSerializer,
)


# TODO: filter is banner news
class NewsCategoryView(ListAPIView, RetrieveAPIView, ViewSet):
    queryset = NewsCategory.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = "category_id"
    serializer_class = NewsCategorySerializer


class NewsView(ListAPIView, RetrieveAPIView, ViewSet):
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = "news_id"
    serializer_class = NewsSerializer

    def get_queryset(self):
        return News.objects.filter(category_id=self.kwargs["category_id"]).all()


class DetailNewsView(RetrieveAPIView, ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = NewsSerializer
