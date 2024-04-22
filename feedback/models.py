from cloudinary.models import CloudinaryField
from django.db import models
from django.utils.translation import gettext_lazy as _

from user.models import User


class Feedback(models.Model):
    class FeedbackType(models.TextChoices):
        QUESTION = "QUESTION", _("Thắc mắc")
        COMPLAIN = "COMPLAIN", _("Phàn nàn")
        SUPPORT = "SUPPORT", _("Hỗ trợ")
        OTHER = "OTHER", _("Khác")

    title = models.CharField(verbose_name=_("Tiêu đề"), max_length=100)
    content = models.TextField(verbose_name=_("Nội dung"), max_length=500)
    type = models.CharField(
        verbose_name=_("Loại"), max_length=10, choices=FeedbackType.choices
    )
    image = CloudinaryField(_("Ảnh"), null=True, blank=True)
    deleted = models.BooleanField(verbose_name=_("Đã xóa"), default=False)
    author = models.ForeignKey(
        verbose_name=_("Tác giả"), to=User, on_delete=models.CASCADE
    )

    def unsoft_delete(self):
        self.deleted = False
        self.save()

    def soft_delete(self):
        self.deleted = True
        self.save()

    def __str__(self) -> str:
        return f"{self.get_type_display()} - {self.title}"
