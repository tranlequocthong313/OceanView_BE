from ckeditor.fields import RichTextField
from django.db import models
from django.utils.translation import gettext_lazy as _

from app.models import MyBaseModel


class NewsCategory(MyBaseModel):
    name = models.CharField(verbose_name=_("Tên"), max_length=50)

    class Meta:
        verbose_name = _("Danh mục tin tức")
        verbose_name_plural = _("Danh mục tin tức")

    def __str__(self):
        return self.name


class News(MyBaseModel):
    title = models.CharField(verbose_name=_("Tiêu đề"), max_length=50)
    content = RichTextField(verbose_name=_("Nội dung"))
    category = models.ForeignKey(
        verbose_name=_("Danh mục"),
        to=NewsCategory,
        on_delete=models.SET_NULL,
        null=True,
    )

    class Meta:
        verbose_name = _("Tin tức")
        verbose_name_plural = _("Tin tức")

    def __str__(self):
        return self.title
