import logging

from rest_framework import status
from rest_framework.response import Response


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


log = logging.getLogger(__name__)


def extract_error_messages(serializer):
    """
    Extract error messages from a serializer's errors and format them nicely.
    """
    errors = serializer.errors
    error_messages = {}
    for field, message in errors.items():
        error_messages[field] = message[0] if isinstance(message, list) else message
    return error_messages


def respond_serializer_error(serializer):
    messages = extract_error_messages(serializer)
    log.error(messages)
    return Response(
        messages,
        status=status.HTTP_400_BAD_REQUEST,
    )
