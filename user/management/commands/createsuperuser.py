import logging
import traceback

import colorama
from colorama import Fore
from django.contrib.auth import get_user_model
from django.contrib.auth.management.commands import createsuperuser

from user.models import PersonalInformation

log = logging.getLogger(__name__)
colorama.init(autoreset=True)


# TODO: Create transaction for rollback data when errors occur
class Command(createsuperuser.Command):
    help = "Create a superuser with custom fields"

    def handle(self, *args, **options):
        citizen_id = input("Citizen ID: ")
        full_name = input("Full Name: ")
        phone_number = input("Phone Number: ")
        email = input("Email: ")
        hometown = input("Hometown (optional): ") or None
        gender = input("Gender (M/F): ")

        personal_info = PersonalInformation.objects.create(
            citizen_id=citizen_id,
            full_name=full_name,
            phone_number=phone_number,
            email=email,
            hometown=hometown,
            gender=(gender.upper() if gender in ["m", "f"] else "M"),
        )

        try:
            resident_id = get_user_model().generate_resident_id()
        except OverflowError:
            log.error(traceback.format_exc())
            return

        options["personal_information_id"] = personal_info.citizen_id
        options["resident_id"] = resident_id

        print(Fore.GREEN + f"This is your Resident ID: {resident_id}")

        super().handle(
            *args,
            **options,
        )
