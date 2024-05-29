from cloudinary.models import CloudinaryField
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_ckeditor_5.fields import CKEditor5Field

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
    content = CKEditor5Field(verbose_name=_("Nội dung"), config_name="extends")
    category = models.ForeignKey(
        verbose_name=_("Danh mục"),
        to=NewsCategory,
        on_delete=models.SET_NULL,
        null=True,
    )
    is_broadcast = models.BooleanField(_("Gửi thông báo"), default=False)
    is_banner = models.BooleanField(_("Banner"), default=False)
    thumbnail = CloudinaryField(_("Ảnh"), null=True, blank=True)

    class Meta:
        verbose_name = _("Tin tức")
        verbose_name_plural = _("Tin tức")

    @property
    def thumbnail_url(self):
        if self.thumbnail:
            self.thumbnail.url_options.update({"secure": True})
            return self.thumbnail.url
        return None

    def __str__(self):
        return self.title
