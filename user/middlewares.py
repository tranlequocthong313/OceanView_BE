import logging

from django.core.cache import cache
from django.http import HttpResponseForbidden

from app import settings
from utils import http

log = logging.getLogger(__name__)


class SendOTPRateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == "/users/send-otp/":
            ip = str(http.get_client_ip(request))
            number_of_requests = cache.get(ip)
            if number_of_requests:
                number_of_requests = cache.incr(ip)
            else:
                cache.set(ip, 1, timeout=settings.RATE_LIMIT_EXPIRE_TIME)
                number_of_requests = 1

            log.warning(f"User request for sending otp {number_of_requests} time(s)")

            if number_of_requests > 1:
                return HttpResponseForbidden("Only allows sending OTP every 1 minute")

        response = self.get_response(request)
        return response
