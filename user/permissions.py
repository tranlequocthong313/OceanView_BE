from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            not request.user.is_anonymous
            and obj.resident_id == request.user.resident_id
        )
