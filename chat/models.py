from django.db import models
from django.utils.translation import gettext_lazy as _

from app.models import MyBaseModel
from user.models import User


# TODO: Re-design this model to support group chat
class Inbox(MyBaseModel):
    last_message = models.TextField(verbose_name=_("Tin nhắn cuối cùng"))
    user_1 = models.ForeignKey(
        verbose_name=_("Người dùng 1"),
        to=User,
        on_delete=models.CASCADE,
        related_name="inboxes_as_user_1",
    )
    user_2 = models.ForeignKey(
        verbose_name=_("Người dùng 2"),
        to=User,
        on_delete=models.CASCADE,
        related_name="inboxes_as_user_2",
    )

    class Meta:
        verbose_name = _("Hộp thư đến")
        verbose_name_plural = _("Hộp thư đến")
        ordering = ["-updated_date"]

    def get_last_message(self):
        if last_message := self.message_set.order_by("-created_date").first():
            return last_message
        else:
            return None


# TODO: Do we have time for handling image stuff in frontend? If we do, then add that
# feature later
class Message(MyBaseModel):
    inbox = models.ForeignKey(
        verbose_name=_("Hộp thư đến"),
        to=Inbox,
        on_delete=models.CASCADE,
    )
    sender = models.ForeignKey(
        verbose_name=_("Người gửi"),
        to=User,
        on_delete=models.CASCADE,
    )
    content = models.TextField(verbose_name=_("Nội dung"))

    class Meta:
        verbose_name = _("Tin nhắn")
        verbose_name_plural = _("Tin nhắn")
        ordering = ["-created_date"]
