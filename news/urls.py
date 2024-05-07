from django.urls import include, path
from rest_framework import routers

from .views import NewsCategoryView, NewsView

r = routers.DefaultRouter()
r.register("news-categories", NewsCategoryView, basename="news-category")
r.register(
    "news-categories/(?P<category_id>[^/.]+)/news",
    NewsView,
    basename="news",
)

urlpatterns = [
    path("", include(r.urls)),
]
