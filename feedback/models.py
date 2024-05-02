from cloudinary.models import CloudinaryField
from django.db import models
from django.utils.translation import gettext_lazy as _

from app.models import MyBaseModelWithDeletedState
from user.models import User


class Feedback(MyBaseModelWithDeletedState):
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
    author = models.ForeignKey(
        verbose_name=_("Tác giả"), to=User, on_delete=models.CASCADE
    )

    def message_feedback_post(self, action):
        return f"{self.author} {action}: {self.__str__()}"

    class Meta:
        verbose_name = _("Phản ánh")
        verbose_name_plural = _("Phản ánh")

    @property
    def image_url(self):
        if self.image:
            self.image.url_options.update({"secure": True})
            return self.image.url
        return None

    def __str__(self) -> str:
        return f"[{self.get_type_display()}] {self.title}"
