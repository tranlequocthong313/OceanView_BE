from typing import Any

from django.contrib import admin
from django.contrib.auth import logout
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import redirect
from django.template.response import TemplateResponse

from app import settings
from firebase import topic
from notification.models import FCMToken
from utils import get_logger

log = get_logger(__name__)


class MyAdminSite(admin.AdminSite):
    site_header = settings.COMPANY_NAME

    def index(
        self, request: WSGIRequest, extra_context: dict[str, Any] | None = ...
    ) -> TemplateResponse:
        extra_context = {"HOST": settings.HOST}
        return super().index(request, extra_context)


class MyBaseModelAdmin(admin.ModelAdmin):
    list_per_page = 10
    empty_value_display = "-- empty --"


admin_site = MyAdminSite(name=settings.COMPANY_NAME)


def logout_view(request):
    user = request.user
    logout(request)
    response = redirect("/admin/")
    fcm_token = request.COOKIES.get("fcm_token")
    print(fcm_token)
    FCMToken.objects.filter(
        token=fcm_token, user=user, device_type=FCMToken.DeviceType.WEB
    ).delete()
    response.delete_cookie("fcm_token")
    topic.unsubscribe_from_topic(fcm_tokens=fcm_token, topic="admin")

    return response
