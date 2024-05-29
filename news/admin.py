from django import forms
from django.contrib import admin
from django.db.models.base import post_save
from django.dispatch import receiver
from django.utils.html import mark_safe
from django_ckeditor_5.widgets import CKEditor5Widget

from app import settings
from app.admin import MyBaseModelAdmin, admin_site
from news.models import News, NewsCategory
from notification.manager import NotificationManager
from notification.types import EntityType


class NewsCategoryAdmin(MyBaseModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    list_filter = ("name",)


class NewsForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditor5Widget)

    class Meta:
        model = News
        fields = "__all__"


class NewsAdmin(MyBaseModelAdmin):
    list_display = ("id", "title", "category")
    search_fields = ("title", "category__name")
    list_filter = ("category__name",)
    form = NewsForm
    readonly_fields = ("_thumbnail",)

    @admin.display(description="Ảnh")
    def _thumbnail(self, obj):
        return mark_safe(f'<img width="500" src="{obj.thumbnail_url}" />')


@receiver(post_save, sender=News)
def send_broadcast(sender, instance, created, **kwargs):
    if created and instance.is_broadcast:
        NotificationManager.create_notification(
            entity=instance, entity_type=EntityType.NEWS_POST, image=settings.LOGO
        )


admin_site.register(News, NewsAdmin)
admin_site.register(NewsCategory, NewsCategoryAdmin)
