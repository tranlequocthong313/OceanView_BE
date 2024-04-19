from cloudinary.models import CloudinaryField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db.models import (
    CASCADE,
    SET_NULL,
    CharField,
    DateField,
    DecimalField,
    ForeignKey,
    OneToOneField,
    TextChoices,
)
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from app.models import MyBaseModel
from utils import format


class InvoiceType(MyBaseModel):
    name = CharField(_("Tên loại hóa đơn"), max_length=50)
    description = CharField(_("Mô tả"), max_length=50, null=True, blank=True)

    class Meta:
        verbose_name = _("Loại hóa đơn")
        verbose_name_plural = _("Loại hóa đơn")

    def __str__(self) -> str:
        return self.name


class Invoice(MyBaseModel):
    class PAYMENT_STATUS(TextChoices):
        PENDING = "PENDING", _("Chờ thanh toán")
        PAID = "PAID", _("Đã thanh toán")
        OVERDUE = "OVERDUE", _("Quá hạn")

    id = CharField(_("Mã hóa đơn"), max_length=10, primary_key=True)
    resident = ForeignKey(
        to=get_user_model(), verbose_name=_("Cư dân"), on_delete=CASCADE
    )
    amount = DecimalField(
        _("Số tiền"), max_digits=11, decimal_places=2, validators=[MinValueValidator(0)]
    )
    due_date = DateField(_("Ngày đáo hạn"))
    payment_status = CharField(
        _("Trạng thái thanh toán"),
        max_length=10,
        choices=PAYMENT_STATUS.choices,
        default="PENDING",
    )
    invoice_type = ForeignKey(
        verbose_name=_("Loại hóa đơn"), to=InvoiceType, on_delete=SET_NULL, null=True
    )

    class Meta:
        verbose_name = _("Hóa đơn")
        verbose_name_plural = _("Hóa đơn")

    def __str__(self):
        return f"{self.id}"


class InvoiceDetail(MyBaseModel):
    class PAYMENT_METHODS(TextChoices):
        E_WALLET = "E_WALLET", _("Ví điện tử")
        ACCREDITATIVE = "ACCREDITATIVE", _("Ủy nhiệm chi")

    payment_method = CharField(
        _("Phương thức thanh toán"), max_length=15, choices=PAYMENT_METHODS.choices
    )
    transaction_code = CharField(
        _("Mã giao dịch"), max_length=49, null=True, blank=True
    )
    payment_proof = CloudinaryField(_("Ảnh chứng từ thanh toán"), null=True, blank=True)
    invoice = OneToOneField(
        verbose_name=_("Hóa đơn"),
        to=Invoice,
        on_delete=CASCADE,
    )

    class Meta:
        verbose_name = _("Chi tiết hóa đơn")
        verbose_name_plural = _("Chi tiết hóa đơn")

    def __str__(self):
        return f"{self.id}"


@receiver(pre_save, sender=Invoice)
def generate_invoice_id(sender, instance, **kwargs):
    if not instance.id:
        latest_invoice = Invoice.objects.order_by("-id").first()
        if latest_invoice:
            last_invoice_number = int(latest_invoice.id[3:])
            new_invoice_number = last_invoice_number + 1
        else:
            new_invoice_number = 1
        instance.id = f"INV{new_invoice_number:06d}"
