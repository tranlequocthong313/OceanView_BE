from django.urls import include, path
from rest_framework import routers

from .views import GuideCategoryView, GuideView

r = routers.DefaultRouter()
r.register("guide-categories", GuideCategoryView, basename="guide-category")
r.register(
    "guide-categories/(?P<category_id>[^/.]+)/guides",
    GuideView,
    basename="guide",
)

urlpatterns = [
    path("", include(r.urls)),
]
