import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _

log = logging.getLogger(__name__)


class CustomUserWithForeignKeyManager(BaseUserManager):
    """
    Custom user model manager where resident_id is the unique identifiers
    for authentication instead of usernames.
    """

    def create_superuser(self, password=None, **extra_fields):
        """
        Create and save a SuperUser with the given resident_id and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        user = self.model(**extra_fields)
        user.set_password(password)
        user.issue()
        user.save()
        return user
