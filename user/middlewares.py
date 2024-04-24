import logging

from django.core.cache import cache
from django.http import HttpResponseForbidden

from utils import http

log = logging.getLogger(__name__)

"""
A middleware class to rate limit the sending of OTP (One-Time Password) requests.

This middleware checks the number of OTP requests from a user's IP address and restricts the frequency of sending OTPs.

Args:
    get_response: The function to get the response in the middleware.

Returns:
    HttpResponse: The response to the request after rate limiting the OTP sending.
"""


class SendOTPRateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == "/users/otp/":
            ip = str(http.get_client_ip(request))
            if number_of_requests := cache.get(ip):
                number_of_requests = cache.incr(ip)
                log.warning(
                    f"User request for sending otp {number_of_requests} time(s)"
                )
                if number_of_requests > 1:
                    return HttpResponseForbidden(
                        "Only allows sending OTP every 1 minute"
                    )

        return self.get_response(request)
