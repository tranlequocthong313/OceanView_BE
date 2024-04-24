from django.shortcuts import get_object_or_404
from rest_framework import permissions

from .models import Item


class LockerOwnsItem(permissions.BasePermission):
    def has_permission(self, request, view):
        locker_id = view.kwargs.get("locker_id")
        item_id = view.kwargs.get("item_id")
        if locker_id is None or item_id is None:
            return False

        get_object_or_404(
            Item,
            pk=item_id,
            locker_id=locker_id,
        )
        return True
