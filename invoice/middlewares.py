from django.http import HttpResponseNotFound

from app import settings
from utils import get_logger, token

log = get_logger(__name__)


class VnPayMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.path.startswith("/vnpay/"):
            return self.get_response(request)
        if "token" not in request.GET:
            log.error("token not exist")
            return HttpResponseNotFound()
        payload = token.verify_token(request.GET.get("token"))
        if payload == settings.SECRET_KEY:
            log.info("vnpay middleware ok")
            return self.get_response(request)
        log.error("token payload invalid")
        return HttpResponseNotFound()
