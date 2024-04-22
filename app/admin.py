from django.contrib import admin

from app import settings


class MyAdminSite(admin.AdminSite):
    site_header = settings.COMPANY_NAME


class MyBaseModelAdmin(admin.ModelAdmin):
    list_per_page = 10
    empty_value_display = "-- empty --"


admin_site = MyAdminSite(name=settings.COMPANY_NAME)
