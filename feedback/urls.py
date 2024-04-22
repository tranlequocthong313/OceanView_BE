from django.urls import include, path
from rest_framework import routers

from .views import FeedbackView

r = routers.DefaultRouter()
r.register("feedbacks", FeedbackView, basename="feedback")

urlpatterns = [
    path("", include(r.urls)),
]
