from django.apps import apps
from django.contrib import admin
from django.utils.html import mark_safe

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
    readonly_fields = [
        "author",
        "type",
        "title",
        "content",
        "_image",
        "image",
        "deleted",
    ]

    def has_add_permission(self, request, obj=None):
        return False

    @admin.display(description="Ảnh")
    def _image(self, obj):
        return mark_safe(f'<img width="500" src="{obj.image_url}" />')


admin_site.register(models.Feedback, FeedbackAdmin)
