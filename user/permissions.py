import contextlib

from django.contrib.sessions.backends.cache import SessionStore
from rest_framework.permissions import BasePermission

from user.models import User

"""
A permission class to check if the requesting user is the owner of the object.

This permission allows access only if the requesting user is authenticated and matches 
the owner of the object based on the resident ID.

Args:
    request: The request object.
    view: The view requesting the permission.
    obj: The object being accessed.

Returns:
    bool: True if the requesting user is the owner, False otherwise.
"""


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            not request.user.is_anonymous
            and obj.resident_id == request.user.resident_id
        )


class NonAccessTokenPermissionMixin:
    def check_permissions(self, request):
        if sessionid := request.COOKIES.get("sessionid"):
            session = SessionStore(session_key=sessionid)

            if session.exists(sessionid) and not session.is_empty():
                if user_id := session.get("_auth_user_id"):
                    with contextlib.suppress(User.DoesNotExist):
                        user = User.objects.get(pk=user_id)
                        request.user = user
            else:
                self.permission_denied(
                    request,
                    message="Authentication credentials were not provided.",
                    code=401,
                )

        return super().check_permissions(request)
