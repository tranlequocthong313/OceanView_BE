from cloudinary.models import CloudinaryField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.base import post_save
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from vnpay.models import Billing

from app.models import MyBaseModel, MyBaseModelWithDeletedState
from service.models import ServiceRegistration


class Invoice(MyBaseModelWithDeletedState):
    class InvoiceStatus(models.TextChoices):
        PENDING = "PENDING", _("Chờ thanh toán")
        PAID = "PAID", _("Đã thanh toán")
        OVERDUE = "OVERDUE", _("Quá hạn")

    id = models.CharField(_("Mã hóa đơn"), max_length=10, primary_key=True)
    resident = models.ForeignKey(
        to=get_user_model(), verbose_name=_("Cư dân"), on_delete=models.CASCADE
    )
    total_amount = models.DecimalField(
        _("Số tiền"),
        max_digits=11,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0,
    )
    due_date = models.DateField(_("Ngày đáo hạn"))
    status = models.CharField(
        _("Trạng thái thanh toán"),
        max_length=10,
        choices=InvoiceStatus.choices,
        default=InvoiceStatus.PENDING,
    )

    class Meta(MyBaseModel.Meta):
        verbose_name = _("Hóa đơn")
        verbose_name_plural = _("Hóa đơn")

    def pay(self):
        self.status = Invoice.InvoiceStatus.PAID
        self.save()

    def message_invoice_create(self, action):
        return f"{action} ({self.created_date.strftime('%d/%m/%Y')})"

    def __str__(self):
        return str(self.id)


class InvoiceDetail(MyBaseModelWithDeletedState):
    invoice = models.ForeignKey(
        verbose_name=_("Hóa đơn"),
        to=Invoice,
        on_delete=models.CASCADE,
    )
    service_registration = models.ForeignKey(
        verbose_name=_("Đăng ký dịch vụ"),
        to=ServiceRegistration,
        on_delete=models.DO_NOTHING,
    )
    amount = models.DecimalField(
        _("Số tiền"), max_digits=11, decimal_places=2, validators=[MinValueValidator(0)]
    )

    class Meta(MyBaseModel.Meta):
        verbose_name = _("Chi tiết hóa đơn")
        verbose_name_plural = _("Chi tiết hóa đơn")

    def __str__(self):
        return str(self.pk)


class Payment(MyBaseModelWithDeletedState):
    class PaymentStatus(models.TextChoices):
        SUCCESS = "SUCCESS", _("Thành công")
        CONFIRMING = "CONFIRMING", _("Đang xác nhận")
        INVALID = "INVALID", _("Không hợp lệ")

    class PaymentMethod(models.TextChoices):
        ONLINE_WALLET = "E_WALLET", _("Ví điện tử")
        PROOF_IMAGE = "PROOF_IMAGE", _("Ủy nhiệm chi")

    method = models.CharField(
        _("Phương thức thanh toán"), max_length=15, choices=PaymentMethod.choices
    )
    total_amount = models.DecimalField(
        _("Số tiền"), max_digits=11, decimal_places=2, validators=[MinValueValidator(0)]
    )
    invoice = models.ForeignKey(
        verbose_name=_("Hóa đơn"), to=Invoice, on_delete=models.DO_NOTHING
    )
    status = models.CharField(
        verbose_name=_("Trạng thái"),
        choices=PaymentStatus.choices,
        default=PaymentStatus.CONFIRMING,
        max_length=20,
    )

    @property
    def is_success(self):
        return self.status == Payment.PaymentStatus.SUCCESS

    def pay(self):
        self.status = Payment.PaymentStatus.SUCCESS
        self.save()
        return True

    class Meta(MyBaseModel.Meta):
        verbose_name = _("Thanh toán")
        verbose_name_plural = _("Thanh toán")

    def __str__(self):
        return f"[{self.get_status_display()}] {self.get_method_display()}"


class ProofImage(MyBaseModelWithDeletedState):
    image = CloudinaryField(_("Ảnh chứng từ thanh toán"))
    payment = models.ForeignKey(
        verbose_name=_("Thanh toán"), to=Payment, on_delete=models.CASCADE
    )

    class Meta(MyBaseModel.Meta):
        verbose_name = _("Ảnh chứng minh")
        verbose_name_plural = _("Ảnh chứng minh")

    def message_proof_image_created(self, action):
        return f"{self.payment.invoice.resident} {action}: {self.payment.get_method_display()}"

    @property
    def image_url(self):
        if self.image:
            self.image.url_options.update({"secure": True})
            return self.image.url
        return None

    def __str__(self):
        return self.payment.__str__()


class OnlineWallet(MyBaseModelWithDeletedState):
    payment = models.ForeignKey(
        verbose_name=_("Thanh toán"), to=Payment, on_delete=models.CASCADE
    )
    vnpay_billing = models.OneToOneField(
        verbose_name=_("Thanh toán vnpay"),
        to=Billing,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta(MyBaseModel.Meta):
        verbose_name = _("Thanh toán qua ví điện tử")
        verbose_name_plural = _("Thanh toán qua ví điện tử")

    def __str__(self):
        return self.payment


class StatsRevenue(Invoice):
    class Meta:
        proxy = True
        verbose_name = _("Thống kê doanh thu")
        verbose_name_plural = _("Thống kê doanh thu")


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


@receiver(post_save, sender=Payment)
def update_invoice_status(sender, instance, **kwargs):
    if instance.is_success:
        instance.invoice.pay()
