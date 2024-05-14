from django.db import models
from django.utils.translation import gettext_lazy as _

from app import settings
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
    NEWS_POST = "NEWS_POST", _("Đăng tin tức")
    INVOICE_CREATE = "INVOICE_CREATE", _("Nhận hóa đơn")
    LOCKER_ITEM_ADD = "LOCKER_ITEM_ADD", _("Đã nhận giúp")


ENTITY_TARGET = {
    "SERVICE_REGISTER": MessageTarget.ADMIN,
    "SERVICE_REISSUE": MessageTarget.ADMIN,
    "SERVICE_APPROVED": MessageTarget.RESIDENT,
    "SERVICE_REJECTED": MessageTarget.RESIDENT,
    "REISSUE_APPROVED": MessageTarget.RESIDENT,
    "REISSUE_REJECTED": MessageTarget.RESIDENT,
    "FEEDBACK_POST": MessageTarget.ADMIN,
    "INVOICE_PROOF_IMAGE_PAYMENT": MessageTarget.ADMIN,
    "NEWS_POST": MessageTarget.RESIDENTS,
    "INVOICE_CREATE": MessageTarget.RESIDENT,
    "LOCKER_ITEM_ADD": MessageTarget.RESIDENT,
}

ENTITY_TYPE_MODEL_MAPPING = {
    "SERVICE_REGISTER": ServiceRegistration,
    "SERVICE_APPROVED": ServiceRegistration,
    "SERVICE_REJECTED": ServiceRegistration,
    "SERVICE_REISSUE": ReissueCard,
    "REISSUE_APPROVED": ReissueCard,
    "REISSUE_REJECTED": ReissueCard,
    "FEEDBACK_POST": Feedback,
    "INVOICE_PROOF_IMAGE_PAYMENT": ProofImage,
    "NEWS_POST": News,
    "INVOICE_CREATE": Invoice,
    "LOCKER_ITEM_ADD": Item,
}

ACTION_MESSAGE_MAPPING = {
    "SERVICE_REGISTER": lambda entity,
    action: f"{entity.resident.__str__()} {action} {entity.service.get_id_display().lower()}",
    "SERVICE_APPROVED": lambda entity,
    action: f"Ban quản trị {action} {entity.service.get_id_display().lower()}",
    "SERVICE_REJECTED": lambda entity,
    action: f"Ban quản trị {action} {entity.service.get_id_display().lower()}",
    "SERVICE_REISSUE": lambda entity,
    action: f"{entity.service_registration.resident.__str__()} {action} {entity.service_registration.service.get_id_display()}.",
    "REISSUE_APPROVED": lambda entity,
    action: f"Ban quản trị {action} {entity.service_registration.service.get_id_display().lower()}",
    "REISSUE_REJECTED": lambda entity,
    action: f"Ban quản trị {action} {entity.service_registration.service.get_id_display().lower()}",
    "FEEDBACK_POST": lambda entity,
    action: f"{entity.author} {action}: {entity.__str__()}",
    "INVOICE_PROOF_IMAGE_PAYMENT": lambda entity,
    action: f"{entity.payment.invoice.resident} {action}: {entity.payment.get_method_display()}",
    "NEWS_POST": lambda entity, _: f"{entity.__str__()}",
    "INVOICE_CREATE": lambda entity,
    action: f"{action.capitalize()} ({entity.created_date.strftime('%d/%m/%Y')})",
    "LOCKER_ITEM_ADD": lambda entity,
    action: f"Ban quản trị {action} {str(entity.quantity)} {entity.name}",
}

LINK_MAPPING = {
    "SERVICE_REGISTER": lambda entity_id: f"{settings.HOST}/admin/service/serviceregistration/{entity_id}/change/",
    "SERVICE_REISSUE": lambda entity_id: f"{settings.HOST}/admin/service/reissuecard/{entity_id}/change/",
    "FEEDBACK_POST": lambda entity_id: f"{settings.HOST}/admin/feedback/feedback/{entity_id}/change/",
    "INVOICE_PROOF_IMAGE_PAYMENT": lambda entity_id: f"{settings.HOST}/admin/invoice/proofimage/{entity_id}/change/",
}
