import getpass
import logging
import traceback

import colorama
from colorama import Fore
from django.contrib.auth import get_user_model
from django.contrib.auth.management.commands import createsuperuser
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from django.db import transaction

from user.models import PersonalInformation

log = logging.getLogger(__name__)
colorama.init(autoreset=True)


class Command(createsuperuser.Command):
    help = "Create a superuser with custom fields"

    @transaction.atomic
    def handle(self, *args, **options):
        citizen_id = input("Citizen ID: ")
        full_name = input("Full Name: ")
        phone_number = input("Phone Number: ")
        email = input("Email: ")
        gender = input("Gender (M/F): ")

        personal_information = PersonalInformation.objects.create(
            citizen_id=citizen_id,
            full_name=full_name,
            phone_number=phone_number,
            email=email,
            gender=(gender.upper() if gender in ["m", "f"] else "M"),
        )

        try:
            resident_id = get_user_model().generate_resident_id()
        except OverflowError:
            log.error(traceback.format_exc())
            return

        print(Fore.GREEN + f"This is your Resident ID: {resident_id}")

        user_data = {}
        user_data["personal_information"] = personal_information
        user_data["resident_id"] = resident_id

        while "password" not in user_data:
            password = getpass.getpass()
            password2 = getpass.getpass("Password (again): ")

            if password != password2:
                self.stderr.write("Error: Your passwords didn't match.")
                # Don't validate passwords that don't match.
                continue
            if password.strip() == "":
                self.stderr.write("Error: Blank passwords aren't allowed.")
                # Don't validate blank passwords.
                continue
            try:
                validate_password(password2, self.UserModel(**user_data))
            except exceptions.ValidationError as err:
                self.stderr.write("\n".join(err.messages))
                continue
            except Exception as err:
                self.stderr.write("\n".join(err.messages))
                raise Exception(err)
            user_data["password"] = password

        get_user_model().objects.create_superuser(**user_data)

        print(Fore.GREEN + "Created superuser successfully!")
