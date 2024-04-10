from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator
from django.db.models import (
    SET_NULL,
    CharField,
    DecimalField,
    ForeignKey,
    TextChoices,
)
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from app.models import MyBaseModel


class InvoiceType(MyBaseModel):
    name = CharField(_("Tên loại hóa đơn"), max_length=50)

    def __str__(self) -> str:
        return self.name


class Invoice(MyBaseModel):
    class PaymentMethod(TextChoices):
        E_WALLET = "E", _("Ví điện tử")
        ACCREDITATIVE = "A", _("Ủy nhiệm chi")

    id = CharField(_("Mã hóa đơn"), max_length=10, primary_key=True)
    payment_method = CharField(
        _("Phương thức thanh toán"), max_length=1, choices=PaymentMethod
    )
    total = DecimalField(
        _("Tổng cộng"),
        max_digits=11,
        decimal_places=2,
        validators=[MinLengthValidator(0)],
    )
    paid = DecimalField(
        _("Đã trả"), max_digits=11, decimal_places=2, validators=[MinLengthValidator(0)]
    )
    trading_code = CharField(_("Mã giao dịch"), max_length=50, null=True)
    invoice_type = ForeignKey(
        verbose_name=_("Loại hóa đơn"),
        to=InvoiceType,
        on_delete=SET_NULL,
        null=True,
    )
    payer = ForeignKey(
        verbose_name=_("Giao dịch bởi"),
        to=get_user_model(),
        on_delete=SET_NULL,
        null=True,
    )

    def __str__(self) -> str:
        return self.id


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
