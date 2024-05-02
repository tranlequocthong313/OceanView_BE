from django.db import models
from django.utils.translation import gettext_lazy as _


class MyBaseModel(models.Model):
    created_date = models.DateTimeField(_("Ngày tạo"), auto_now_add=True)
    updated_date = models.DateTimeField(_("Ngày cập nhật"), auto_now=True)

    class Meta:
        abstract = True


class MyBaseModelWithDeletedState(MyBaseModel):
    deleted = models.BooleanField(_("Đã bị xóa"), default=False)

    def unsoft_delete(self):
        self.deleted = False
        self.save()

    def soft_delete(self):
        self.deleted = True
        self.save()

    class Meta:
        abstract = True
