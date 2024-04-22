from django.apps import apps
from django.contrib import admin

from app.admin import admin_site

from . import models


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ["title", "type", "author", "deleted"]
    list_filter = ["type", "deleted"]
    search_fields = [
        "title",
        "author__resident_id",
        "author__personal_information__full_name",
        "author__personal_information__phone_number",
        "author__personal_information__email",
    ]
    readonly_fields = ["image"]


admin_site.register(models.Feedback, FeedbackAdmin)
