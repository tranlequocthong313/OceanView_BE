from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms

from app.admin import MyBaseModelAdmin, admin_site
from guide.models import Guide, GuideCategory


class GuideCategoryAdmin(MyBaseModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    list_filter = ("name",)


class GuideForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget)

    class Meta:
        model = Guide
        fields = "__all__"


class GuideAdmin(MyBaseModelAdmin):
    list_display = ("id", "title", "category")
    search_fields = ("title", "category__name")
    list_filter = ("category__name",)
    form = GuideForm


admin_site.register(Guide, GuideAdmin)
admin_site.register(GuideCategory, GuideCategoryAdmin)
