import logging
import traceback
from smtplib import SMTPException

from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.utils.html import mark_safe

from app.admin import MyBaseModelAdmin, admin_site
from utils.email import send_mail
from utils.sms import send_sms

from .models import PersonalInformation, User

log = logging.getLogger(__name__)


class MyUserAdmin(MyBaseModelAdmin):
    model = get_user_model()
    list_display = (
        "resident_id",
        "personal_information",
        "is_staff",
        "is_superuser",
        "status",
        "issued_by",
    )
    exclude = ("is_active",)
    readonly_fields = (
        "resident_id",
        "personal_information",
        "password",
        "user_avatar",
        "issued_by",
    )
    search_fields = (
        "resident_id",
        "personal_information__citizen_id",
        "personal_information__full_name",
        "personal_information__email",
        "personal_information__phone_number",
    )
    list_filter = ("is_staff", "is_superuser", "issued_by")
    actions = ["ban_users"]

    change_form_template = "admin/user_change_form.html"

    def has_add_permission(self, request, obj=None):
        return False

    @admin.display(description="Ảnh đại diện")
    def user_avatar(self, obj):
        return mark_safe(f'<img width="300" src="{obj.avatar.url}" />')

    def ban_user(self, request, user):
        if user.is_banned:
            messages.add_message(
                request, messages.ERROR, f"Ban {user} failed. User has been banned"
            )
        else:
            user.ban()
            messages.add_message(request, messages.SUCCESS, f"Ban {user} successfully")

    @admin.action(description="Khóa tài khoản")
    def ban_users(self, request, queryset):
        for user in queryset:
            self.ban_user(request, user)

    def unban_user(self, request, user):
        if user.is_banned is False:
            messages.add_message(
                request, messages.ERROR, f"Ban {user} failed. User has not been banned"
            )
        else:
            user.unban()
            messages.add_message(
                request, messages.SUCCESS, f"Unban {user} successfully"
            )

    @admin.action(description="Mở khóa tài khoản")
    def unban_users(self, request, queryset):
        for user in queryset:
            self.unban_user(request, user)

    def response_change(self, request, obj):
        if "_ban-user" in request.POST:
            self.ban_user(request, obj)
            return HttpResponseRedirect(".")
        if "_unban-user" in request.POST:
            self.unban_user(request, obj)
            return HttpResponseRedirect(".")
        return super().response_change(request, obj)


class PersonalInformationAdmin(MyBaseModelAdmin):
    list_display = (
        "citizen_id",
        "full_name",
        "date_of_birth",
        "phone_number",
        "email",
        "hometown",
        "gender",
        "status",
    )
    search_fields = ("citizen_id", "full_name", "phone_number", "email", "hometown")
    list_filter = ("gender", "hometown", "date_of_birth")
    actions = ["issue_accounts"]

    change_form_template = "admin/personalinformation_change_form.html"

    @admin.display(description="Trạng thái")
    def status(self, obj):
        if obj.user:
            return obj.user.get_status_display()

    def issue_account(self, request, personal_information):
        if personal_information.is_issued() is False:
            user = None
            try:
                password = get_user_model().objects.make_random_password()
                if personal_information.has_account():
                    user = personal_information.user
                    user.change_password(password)
                else:
                    user = get_user_model().create_user(
                        password=password,
                        personal_information=personal_information,
                        issued_by=request.user,
                    )

                # Prioritize sending emails instead of SMS because Twilio service has many
                # limitations during trial use. Will change priority if Twilio account can
                # be purchased.
                # Do not send accounts asynchronously, as this is a mandatory step otherwise
                # the account granting process will be considered failed.
                if user.personal_information.email is not None:
                    send_mail(
                        subject="Cấp phát tài khoản",
                        template="account/email/issue_email",
                        recipient_list=[personal_information.email],
                        user=user,
                        password=password,
                    )
                else:
                    send_sms(
                        template="account/sms/issue_sms",
                        to=user.personal_information.phone_number,
                        user=user,
                        password=password,
                    )

                log.info(f"issued new account: {user}")
                user.issue()
                user.save()
                return True
            except OverflowError as err:
                log.error(traceback.format_exc())
                messages.add_message(request, messages.ERROR, err)
            except SMTPException:
                log.error(traceback.format_exc())
            return False
        else:
            messages.add_message(
                request, messages.ERROR, "account has been issued before"
            )

    def inform_issue_account_status(self, request, personal_information):
        try:
            success = self.issue_account(request, personal_information)
            if success:
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    f"Issue account {personal_information} successfully",
                )
            else:
                messages.add_message(
                    request,
                    messages.ERROR,
                    f"Issue account {personal_information} failed",
                )
        except Exception:
            log.error(traceback.format_exc())
            messages.add_message(request, messages.ERROR, "something went wrong")

    def response_change(self, request, obj):
        if "_issue-account" in request.POST:
            self.inform_issue_account_status(request, obj)
            return HttpResponseRedirect(".")  # stay on the same detail page
        return super().response_change(request, obj)

    @admin.action(description="Cấp phát tài khoản")
    def issue_accounts(self, request, queryset):
        for personal_information in queryset:
            self.inform_issue_account_status(request, personal_information)


admin_site.register(PersonalInformation, PersonalInformationAdmin)
admin_site.register(User, MyUserAdmin)
