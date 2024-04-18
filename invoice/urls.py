from django.urls import include, path
from rest_framework import routers

from .views import InvoiceView

r = routers.DefaultRouter()
r.register("", InvoiceView, basename="invoice")

urlpatterns = [
    path("", include(r.urls)),
]
