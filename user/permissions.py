from rest_framework.permissions import BasePermission

"""
A permission class to check if the requesting user is the owner of the object.

This permission allows access only if the requesting user is authenticated and matches the owner of the object based on the resident ID.

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
