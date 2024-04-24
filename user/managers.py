from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _

from utils import get_logger

log = get_logger(__name__)

"""
A custom user manager class for creating superusers with foreign key relationships.

This manager creates superusers with specific attributes and ensures that is_staff and 
is_superuser are set to True.

Args:
    password (str): The password for the superuser.
    **extra_fields: Additional fields to set for the superuser.

Returns:
    User: The created superuser instance.
"""


class CustomUserWithForeignKeyManager(BaseUserManager):
    def create_superuser(self, password=None, **extra_fields):
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
