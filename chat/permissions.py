from rest_framework.permissions import BasePermission


class IsRelated(BasePermission):
    def has_object_permission(self, request, view, obj):
        return not request.user.is_anonymous and (
            obj.user_1 == request.user or obj.user_2 == request.user
        )
