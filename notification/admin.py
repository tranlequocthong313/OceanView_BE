from typing import Any

from django.http import HttpRequest

from app.admin import MyBaseModelAdmin, admin_site

from .models import (
    FCMToken,
    Notification,
    NotificationContent,
    NotificationSender,
)


class NotificationAdmin(MyBaseModelAdmin):
    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_delete_permission(
        self, request: HttpRequest, obj: Any | None = ...
    ) -> bool:
        return False

    def has_change_permission(
        self, request: HttpRequest, obj: Any | None = ...
    ) -> bool:
        return False


class NotificationSenderAdmin(MyBaseModelAdmin):
    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_delete_permission(
        self, request: HttpRequest, obj: Any | None = ...
    ) -> bool:
        return False

    def has_change_permission(
        self, request: HttpRequest, obj: Any | None = ...
    ) -> bool:
        return False


class NotificationContentAdmin(MyBaseModelAdmin):
    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_delete_permission(
        self, request: HttpRequest, obj: Any | None = ...
    ) -> bool:
        return False

    def has_change_permission(
        self, request: HttpRequest, obj: Any | None = ...
    ) -> bool:
        return False


class FCMTokenAdmin(MyBaseModelAdmin):
    def has_change_permission(
        self, request: HttpRequest, obj: Any | None = ...
    ) -> bool:
        return False

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False


admin_site.register(FCMToken, FCMTokenAdmin)
admin_site.register(Notification, NotificationAdmin)
admin_site.register(NotificationContent, NotificationContentAdmin)
admin_site.register(NotificationSender, NotificationSenderAdmin)
