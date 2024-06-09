from app.admin import MyBaseModelAdmin, admin_site

from .models import Inbox, Message


class InboxAdmin(MyBaseModelAdmin):
    list_display = (
        "id",
        "user_1",
        "user_2",
        "created_date",
        "updated_date",
    )
    search_fields = ("user_1__resident_id", "user_2__resident_id")
    list_filter = ("created_date", "updated_date")


class MessageAdmin(MyBaseModelAdmin):
    list_display = ("id", "inbox", "sender", "content", "created_date")
    search_fields = ("sender__resident_id", "content")
    list_filter = ("created_date",)


admin_site.register(Inbox, InboxAdmin)
admin_site.register(Message, MessageAdmin)
