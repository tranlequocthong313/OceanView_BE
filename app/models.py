from django.db import models
from django.utils.translation import gettext_lazy as _


class MyBaseModel(models.Model):
    created_date = models.DateTimeField(_("Ngày tạo"), auto_now_add=True)
    updated_date = models.DateTimeField(_("Ngày cập nhật"), auto_now=True)

    class Meta:
        abstract = True
