from django.db import models
from django.utils.translation import gettext_lazy as _

from app import settings
from chat.models import Inbox, Message
from feedback.models import Feedback
from invoice.models import Invoice, ProofImage
from locker.models import Item
from news.models import News
from service.models import ReissueCard, ServiceRegistration


class MessageTarget(models.TextChoices):
    ADMIN = "ADMIN", _("Ban quản trị")
    RESIDENT = "RESIDENT", _("Cư dân")
    RESIDENTS = "RESIDENTS", _("Nhiều cư dân")
    ALL = "ALL", _("Tất cả")


class EntityType(models.TextChoices):
    SERVICE_REGISTER = "SERVICE_REGISTER", _("Đăng ký dịch vụ")
    SERVICE_APPROVED = "SERVICE_APPROVED", _("Đã duyệt đăng ký")
    SERVICE_REJECTED = "SERVICE_REJECTED", _("Đã từ chối đăng ký")
    REISSUE_APPROVED = "REISSUE_APPROVED", _("Đã duyệt cấp lại")
    REISSUE_REJECTED = "REISSUE_REJECTED", _("Đã từ chối cấp lại")
    SERVICE_REISSUE = "SERVICE_REISSUE", _("Cấp lại")
    FEEDBACK_POST = "FEEDBACK_POST", _("Đăng phản ánh")
    INVOICE_PROOF_IMAGE_PAYMENT = "INVOICE_PROOF_IMAGE_PAYMENT", _("Thanh toán")
    INVOICE_PROOF_IMAGE_APPROVED = (
        "INVOICE_PROOF_IMAGE_APPROVED",
        _("Đã duyệt thanh toán"),
    )
    INVOICE_PROOF_IMAGE_REJECTED = (
        "INVOICE_PROOF_IMAGE_REJECTED",
        _("Đã từ chối thanh toán"),
    )
    NEWS_POST = "NEWS_POST", _("Đăng tin tức")
    INVOICE_CREATE = "INVOICE_CREATE", _("Nhận hóa đơn")
    LOCKER_ITEM_ADD = "LOCKER_ITEM_ADD", _("Đã nhận giúp")
    CHAT_SEND_MESSAGE = "CHAT_SEND_MESSAGE", _("")


ENTITY_TARGET = {
    EntityType.SERVICE_REGISTER: MessageTarget.ADMIN,
    EntityType.SERVICE_REISSUE: MessageTarget.ADMIN,
    EntityType.SERVICE_APPROVED: MessageTarget.RESIDENT,
    EntityType.SERVICE_REJECTED: MessageTarget.RESIDENT,
    EntityType.REISSUE_APPROVED: MessageTarget.RESIDENT,
    EntityType.REISSUE_REJECTED: MessageTarget.RESIDENT,
    EntityType.FEEDBACK_POST: MessageTarget.ADMIN,
    EntityType.INVOICE_PROOF_IMAGE_PAYMENT: MessageTarget.ADMIN,
    EntityType.INVOICE_PROOF_IMAGE_APPROVED: MessageTarget.RESIDENT,
    EntityType.INVOICE_PROOF_IMAGE_REJECTED: MessageTarget.RESIDENT,
    EntityType.NEWS_POST: MessageTarget.RESIDENTS,
    EntityType.INVOICE_CREATE: MessageTarget.RESIDENT,
    EntityType.LOCKER_ITEM_ADD: MessageTarget.RESIDENT,
    EntityType.CHAT_SEND_MESSAGE: MessageTarget.RESIDENT,
}

ENTITY_TYPE_MODEL_MAPPING = {
    EntityType.SERVICE_REGISTER: ServiceRegistration,
    EntityType.SERVICE_APPROVED: ServiceRegistration,
    EntityType.SERVICE_REJECTED: ServiceRegistration,
    EntityType.SERVICE_REISSUE: ReissueCard,
    EntityType.REISSUE_APPROVED: ReissueCard,
    EntityType.REISSUE_REJECTED: ReissueCard,
    EntityType.FEEDBACK_POST: Feedback,
    EntityType.INVOICE_PROOF_IMAGE_PAYMENT: ProofImage,
    EntityType.INVOICE_PROOF_IMAGE_APPROVED: ProofImage,
    EntityType.INVOICE_PROOF_IMAGE_REJECTED: ProofImage,
    EntityType.NEWS_POST: News,
    EntityType.INVOICE_CREATE: Invoice,
    EntityType.LOCKER_ITEM_ADD: Item,
    EntityType.CHAT_SEND_MESSAGE: Inbox,
}

ACTION_MESSAGE_MAPPING = {
    EntityType.SERVICE_REGISTER: lambda entity,
    action: f"{entity.resident.__str__()} {action} {entity.service.get_id_display()}",
    EntityType.SERVICE_APPROVED: lambda entity,
    action: f"Ban quản trị {action} {entity.service.get_id_display()}",
    EntityType.SERVICE_REJECTED: lambda entity,
    action: f"Ban quản trị {action} {entity.service.get_id_display()}",
    EntityType.SERVICE_REISSUE: lambda entity,
    action: f"{entity.service_registration.resident.__str__()} {action} {entity.service_registration.service.get_id_display()}",
    EntityType.REISSUE_APPROVED: lambda entity,
    action: f"Ban quản trị {action} {entity.service_registration.service.get_id_display()}",
    EntityType.REISSUE_REJECTED: lambda entity,
    action: f"Ban quản trị {action} {entity.service_registration.service.get_id_display()}",
    EntityType.FEEDBACK_POST: lambda entity,
    action: f"{entity.author} {action}: {entity.__str__()}",
    EntityType.INVOICE_PROOF_IMAGE_PAYMENT: lambda entity,
    action: f"{entity.payment.invoice.resident} {action} {entity.payment.get_method_display()}",
    EntityType.INVOICE_PROOF_IMAGE_APPROVED: lambda entity,
    action: f"Ban quản trị {action} {entity.payment.get_method_display()}",
    EntityType.INVOICE_PROOF_IMAGE_REJECTED: lambda entity,
    action: f"Ban quản trị {action} {entity.payment.get_method_display()}",
    EntityType.NEWS_POST: lambda entity, action: f"{entity.__str__()}",
    EntityType.INVOICE_CREATE: lambda entity,
    action: f"{action.capitalize()} ({entity.created_date.strftime('%d/%m/%Y')})",
    EntityType.LOCKER_ITEM_ADD: lambda entity,
    action: f"Ban quản trị {action} {str(entity.quantity)} {entity.name}",
    EntityType.CHAT_SEND_MESSAGE: lambda entity,
    action: f"{entity.get_last_message().sender.personal_information.full_name}: {str(entity.last_message)}",
}

LINK_MAPPING = {
    EntityType.SERVICE_REGISTER: lambda entity_id: f"{settings.HOST}/admin/service/serviceregistration/{entity_id}/change/",
    EntityType.SERVICE_REISSUE: lambda entity_id: f"{settings.HOST}/admin/service/reissuecard/{entity_id}/change/",
    EntityType.FEEDBACK_POST: lambda entity_id: f"{settings.HOST}/admin/feedback/feedback/{entity_id}/change/",
    EntityType.INVOICE_PROOF_IMAGE_PAYMENT: lambda entity_id: f"{settings.HOST}/admin/invoice/proofimage/{entity_id}/change/",
}
