import getpass

import colorama
from colorama import Fore
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.management.commands import createsuperuser
from django.core import exceptions
from django.db import transaction

from user.models import PersonalInformation
from utils import get_logger

log = get_logger(__name__)
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
            self.stderr.write("Error: Cannot generate resident ID.")
            return

        self.stdout.write(f"{Fore.GREEN}This is your Resident ID: {resident_id}")

        user_data = {
            "personal_information": personal_information,
            "resident_id": resident_id,
        }

        while "password" not in user_data:
            password = self.get_password()
            password2 = self.get_password("Password (again): ")

            if password != password2:
                self.stderr.write("Error: Your passwords didn't match.")
                continue

            user_data["password"] = password

        try:
            get_user_model().objects.create_superuser(**user_data)
            self.stdout.write(f"{Fore.GREEN}Created superuser successfully!")
        except exceptions.ValidationError as err:
            self.stderr.write(err.messages[0])
            return

    def get_password(self, prompt="Password: "):
        password = None
        while not password:
            password = getpass.getpass(prompt)
            try:
                password_validation.validate_password(password)
            except exceptions.ValidationError as err:
                self.stderr.write("\n".join(err.messages))
                password = None
        return password
