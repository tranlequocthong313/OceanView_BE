from ckeditor.fields import RichTextField
from django.db import models
from django.utils.translation import gettext_lazy as _

from app.models import MyBaseModel


class GuideCategory(MyBaseModel):
    name = models.CharField(verbose_name=_("Tên"), max_length=50)

    class Meta:
        verbose_name = _("Danh mục cẩm nang")
        verbose_name_plural = _("Danh mục cẩm nang")

    def __str__(self):
        return self.name


class Guide(MyBaseModel):
    title = models.CharField(verbose_name=_("Tiêu đề"), max_length=50)
    content = RichTextField(verbose_name=_("Nội dung"))
    category = models.ForeignKey(
        verbose_name=_("Danh mục"),
        to=GuideCategory,
        on_delete=models.SET_NULL,
        null=True,
    )

    class Meta:
        verbose_name = _("Cẩm nang")
        verbose_name_plural = _("Cẩm nang")

    def __str__(self):
        return self.title
