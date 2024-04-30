from typing import Any

from django.contrib import admin
from django.core.handlers.wsgi import WSGIRequest
from django.template.response import TemplateResponse

from app import settings
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
