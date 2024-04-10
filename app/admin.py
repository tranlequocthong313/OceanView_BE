from django.contrib import admin
from django.template.response import TemplateResponse
from django.urls import URLResolver, path

from app import settings


class MyAdminSite(admin.AdminSite):
    site_header = settings.COMPANY_NAME


class MyBaseModelAdmin(admin.ModelAdmin):
    list_per_page = 10


admin_site = MyAdminSite(name=settings.COMPANY_NAME)
