from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms

from app.admin import MyBaseModelAdmin, admin_site
from news.models import News, NewsCategory


class NewsCategoryAdmin(MyBaseModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    list_filter = ("name",)


class NewsForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget)

    class Meta:
        model = News
        fields = "__all__"


class NewsAdmin(MyBaseModelAdmin):
    list_display = ("id", "title", "category")
    search_fields = ("title", "category__name")
    list_filter = ("category__name",)
    form = NewsForm


admin_site.register(News, NewsAdmin)
admin_site.register(NewsCategory, NewsCategoryAdmin)
