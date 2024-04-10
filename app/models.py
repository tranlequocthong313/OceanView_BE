from django.db.models import (
    DateTimeField,
    Model,
)
from django.utils.translation import gettext_lazy as _


class MyBaseModel(Model):
    created_date = DateTimeField(_("Ngày tạo"), auto_now_add=True)
    updated_date = DateTimeField(_("Ngày cập nhật"), auto_now=True)

    class Meta:
        abstract = True
