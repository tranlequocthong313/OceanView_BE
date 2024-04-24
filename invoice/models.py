from cloudinary.models import CloudinaryField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from app.models import MyBaseModel


class InvoiceType(MyBaseModel):
    name = models.CharField(_("Tên loại hóa đơn"), max_length=50)
    description = models.CharField(_("Mô tả"), max_length=50, null=True, blank=True)

    class Meta:
        verbose_name = _("Loại hóa đơn")
        verbose_name_plural = _("Loại hóa đơn")

    def __str__(self) -> str:
        return self.name


class Invoice(MyBaseModel):
    class PaymentStatus(models.TextChoices):
        PENDING = "PENDING", _("Chờ thanh toán")
        PAID = "PAID", _("Đã thanh toán")
        OVERDUE = "OVERDUE", _("Quá hạn")

    id = models.CharField(_("Mã hóa đơn"), max_length=10, primary_key=True)
    resident = models.ForeignKey(
        to=get_user_model(), verbose_name=_("Cư dân"), on_delete=models.CASCADE
    )
    amount = models.DecimalField(
        _("Số tiền"), max_digits=11, decimal_places=2, validators=[MinValueValidator(0)]
    )
    due_date = models.DateField(_("Ngày đáo hạn"))
    payment_status = models.CharField(
        _("Trạng thái thanh toán"),
        max_length=10,
        choices=PaymentStatus.choices,
        default="PENDING",
    )
    invoice_type = models.ForeignKey(
        verbose_name=_("Loại hóa đơn"),
        to=InvoiceType,
        on_delete=models.SET_NULL,
        null=True,
    )

    class Meta:
        verbose_name = _("Hóa đơn")
        verbose_name_plural = _("Hóa đơn")

    def __str__(self):
        return f"{self.id}"


class InvoiceDetail(MyBaseModel):
    class PAYMENT_METHODS(models.TextChoices):
        E_WALLET = "E_WALLET", _("Ví điện tử")
        PROOF_IMAGE = "PROOF_IMAGE", _("Ủy nhiệm chi")

    payment_method = models.CharField(
        _("Phương thức thanh toán"), max_length=15, choices=PAYMENT_METHODS.choices
    )
    transaction_code = models.CharField(
        _("Mã giao dịch"), max_length=49, null=True, blank=True
    )
    payment_proof = CloudinaryField(_("Ảnh chứng từ thanh toán"), null=True, blank=True)
    invoice = models.OneToOneField(
        verbose_name=_("Hóa đơn"),
        to=Invoice,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = _("Chi tiết hóa đơn")
        verbose_name_plural = _("Chi tiết hóa đơn")

    def __str__(self):
        return f"{self.id}"


"""
A signal receiver function to generate an invoice ID before saving the Invoice instance.

This function listens for the pre-save signal of the Invoice model and generates a unique 
invoice ID if it does not already exist.

Args:
    sender: The sender of the signal.
    instance: The instance of the Invoice model being saved.
    **kwargs: Additional keyword arguments.

Returns:
    None
"""


@receiver(pre_save, sender=Invoice)
def generate_invoice_id(sender, instance, **kwargs):
    if not instance.id:
        if latest_invoice := Invoice.objects.order_by("-id").first():
            last_invoice_number = int(latest_invoice.id[3:])
            new_invoice_number = last_invoice_number + 1
        else:
            new_invoice_number = 1
        instance.id = f"INV{new_invoice_number:06d}"
