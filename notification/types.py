from django.db import models
from django.utils.translation import gettext_lazy as _

from app import settings
from feedback.models import Feedback
from invoice.models import Invoice, ProofImage
from news.models import News
from service.models import ReissueCard, ServiceRegistration


class MessageTarget(models.TextChoices):
    ADMIN = "ADMIN", _("Ban quản trị")
    RESIDENT = "RESIDENT", _("Cư dân")
    RESIDENTS = "RESIDENTS", _("Nhiều cư dân")
    ALL = "ALL", _("Tất cả")


class EntityType(models.TextChoices):
    SERVICE_REGISTER = "SERVICE_REGISTER", _("Đăng ký dịch vụ")
    SERVICE_REISSUE = "SERVICE_REISSUE", _("Cấp lại")
    FEEDBACK_POST = "FEEDBACK_POST", _("Đăng phản ánh")
    INVOICE_PROOF_IMAGE_PAYMENT = "INVOICE_PROOF_IMAGE_PAYMENT", _("Thanh toán")
    NEWS_POST = "NEWS_POST", _("Đăng thông báo")
    INVOICE_CREATE = "INVOICE_CREATE", _("Nhận hóa đơn")


ENTITYP_TARGET = {
    "SERVICE_REGISTER": MessageTarget.ADMIN,
    "SERVICE_REISSUE": MessageTarget.ADMIN,
    "FEEDBACK_POST": MessageTarget.ADMIN,
    "INVOICE_PROOF_IMAGE_PAYMENT": MessageTarget.ADMIN,
    "NEWS_POST": MessageTarget.RESIDENTS,
    "INVOICE_CREATE": MessageTarget.RESIDENT,
}

ENTITY_TYPE_MODEL_MAPPING = {
    "SERVICE_REGISTER": ServiceRegistration,
    "SERVICE_REISSUE": ReissueCard,
    "FEEDBACK_POST": Feedback,
    "INVOICE_PROOF_IMAGE_PAYMENT": ProofImage,
    "NEWS_POST": News,
    "INVOICE_CREATE": Invoice,
}

ACTION_MESSAGE_MAPPING = {
    "FEEDBACK_POST": lambda entity, content: entity.message_feedback_post(
        content.get_entity_type_display().lower()
    ),
    "SERVICE_REGISTER": lambda entity, content: entity.message_service_register(
        content.get_entity_type_display().lower()
    ),
    "SERVICE_REISSUE": lambda entity, content: entity.message_service_reissue(
        content.get_entity_type_display().lower()
    ),
    "INVOICE_PROOF_IMAGE_PAYMENT": lambda entity,
    content: entity.message_proof_image_created(
        content.get_entity_type_display().lower()
    ),
    "NEWS_POST": lambda entity, content: entity.message_news_post(
        content.get_entity_type_display().lower()
    ),
    "INVOICE_CREATE": lambda entity, content: entity.message_invoice_create(
        content.get_entity_type_display().lower()
    ),
}

LINK_MAPPING = {
    "SERVICE_REGISTER": lambda entity_id: f"{settings.HOST}/admin/service/serviceregistration/{entity_id}/change/",
    "SERVICE_REISSUE": lambda entity_id: f"{settings.HOST}/admin/service/reissuecard/{entity_id}/change/",
    "FEEDBACK_POST": lambda entity_id: f"{settings.HOST}/admin/feedback/feedback/{entity_id}/change/",
    "INVOICE_PROOF_IMAGE_PAYMENT": lambda entity_id: f"{settings.HOST}/admin/invoice/proofimage/{entity_id}/change/",
}
