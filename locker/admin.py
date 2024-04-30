from django.apps import apps
from django.contrib import admin
from django.utils.html import mark_safe

from app.admin import MyBaseModelAdmin, admin_site

from .models import Item


class ItemInline(admin.TabularInline):
    model = Item
    extra = 0
    fields = ["name", "quantity", "image", "display_image", "status"]
    readonly_fields = ["display_image"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(status=Item.ItemStatus.NOT_RECEIVED)

    def display_image(self, obj):
        if obj.image:
            return mark_safe(
                '<img src="{url}" width="{width}" height={height} />'.format(
                    url=obj.image_url,
                    width=100,
                    height=100,
                )
            )
        else:
            return "No image"

    display_image.short_description = "Image"


class LockerAdmin(MyBaseModelAdmin):
    list_display = ["owner", "status"]
    readonly_fields = ["owner", "status"]
    search_fields = [
        "owner__resident_id",
        "owner__personal_information__citizen_id",
        "owner__personal_information__phone_number",
        "owner__personal_information__email",
        "status",
    ]
    list_filter = ["status"]
    inlines = [ItemInline]

    def has_add_permission(self, request, obj=None):
        return False


class ItemAdmin(MyBaseModelAdmin):
    list_display = ["name", "locker", "quantity", "status"]
    list_filter = ["status"]
    search_fields = [
        "name",
        "quantity",
        "locker__owner__resident_id",
        "locker__owner__personal_information__citizen_id",
        "locker__owner__personal_information__phone_number",
        "locker__owner__personal_information__email",
        "status",
    ]
    actions = ["mark_as_received", "mark_as_not_received"]

    def mark_as_received(self, request, queryset):
        queryset.update(status=Item.ItemStatus.RECEIVED)

    mark_as_received.short_description = "Đánh dấu là đã nhận"

    def mark_as_not_received(self, request, queryset):
        queryset.update(status=Item.ItemStatus.NOT_RECEIVED)

    mark_as_not_received.short_description = "Đánh dấu là chưa nhận"


locker_app = apps.get_app_config("locker")

model_admins = {
    "locker": LockerAdmin,
    "item": ItemAdmin,
}

for model_name, model in locker_app.models.items():
    admin_site.register(model, model_admins[model_name])
