from datetime import datetime
from typing import Any

from django.contrib import admin
from django.db.models import Count, IntegerField
from django.db.models.functions import ExtractMonth, ExtractYear
from django.http import HttpRequest
from django.utils.html import mark_safe
from django.utils.translation import gettext_lazy as _

from app.admin import admin_site
from utils import get_logger

from .models import Feedback, StatsFeedback

log = get_logger(__name__)


class FeedbackAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "type",
        "author",
        "deleted",
        "created_date",
        "updated_date",
    ]
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
    exclude = ("delete",)

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(
        self, request: HttpRequest, obj: Any | None = ...
    ) -> bool:
        return False

    @admin.display(description="Ảnh")
    def _image(self, obj):
        return mark_safe(f'<img width="500" src="{obj.image_url}" />')


# TODO: Implement pick date
class StatsFeedbackAdmin(admin.ModelAdmin):
    change_list_template = "admin/stats/feedback_change_list.html"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["title"] = "Thống kê phản ánh"
        extra_context["chart_data"] = self.get_feedback_stats(request)
        return super().changelist_view(request, extra_context=extra_context)

    def get_feedback_stats(self, request):
        month_year = (
            request.GET.get("month-year")
            if "month-year" in request.GET
            else datetime.now().strftime("%Y-%m")
        )
        year, month = map(int, month_year.split("-"))
        feedback_stats = (
            Feedback.objects.filter(created_date__month=month, created_date__year=year)
            .annotate(
                month=ExtractMonth("created_date"),
                year=ExtractYear("created_date"),
            )
            .values("month", "year", "type")
            .annotate(
                count=Count("id", output_field=IntegerField()),
            )
        )
        data = {}
        for feedback in feedback_stats:
            month_year = f"{feedback['month']}-{feedback['year']}"
            if month_year not in data:
                data[month_year] = {
                    ftype[0]: 0 for ftype in Feedback.FeedbackType.choices
                }
            data[month_year][feedback["type"]] = feedback["count"]

        return data

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(
        self, request: HttpRequest, obj: Any | None = ...
    ) -> bool:
        return False

    def has_change_permission(self, request, obj=None):
        return False


admin_site.register(Feedback, FeedbackAdmin)
admin_site.register(StatsFeedback, StatsFeedbackAdmin)
