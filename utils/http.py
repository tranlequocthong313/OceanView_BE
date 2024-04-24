"""
Get the client's IP address from the request object.

Args:
    request: The request object containing client information.

Returns:
    str: The client's IP address extracted from the request.
"""


def get_client_ip(request):
    return (
        x_forwarded_for.split(",")[0]
        if (x_forwarded_for := request.META.get("HTTP_X_FORWARDED_FOR"))
        else request.META.get("REMOTE_ADDR")
    )
