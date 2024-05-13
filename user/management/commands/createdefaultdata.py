from django.core.management.base import BaseCommand
from django.db import transaction
from oauth2_provider.models import get_application_model

from apartment.models import (
    Apartment,
    ApartmentBuilding,
    ApartmentType,
    Building,
)
from app import settings
from service.models import Service
from user.models import PersonalInformation, User

"""
A management command to create default data for various models in the application.

This command creates default data for models such as User, PersonalInformation, Service, ApartmentBuilding, Building, ApartmentType, Apartment, and OAuth2 Application.

Args:
    *args: Additional positional arguments.
    **kwargs: Additional keyword arguments.

Returns:
    None
"""


class Command(BaseCommand):
    help = "Create default data for models"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        if not User.objects.filter(is_superuser=True).exists():
            self.stdout.write(self.style.HTTP_INFO("Creating superuser..."))
            personal_information = PersonalInformation.objects.create(
                **settings.ADMIN_INFO["personal_information"],
            )
            resident_id = User.generate_resident_id()
            User.objects.create_superuser(
                password=settings.ADMIN_INFO["password"],
                personal_information=personal_information,
                resident_id=resident_id,
            )
            self.stdout.write(self.style.SUCCESS("Created superuser"))

        if Service.objects.count() == 0:
            self.stdout.write(self.style.HTTP_INFO("Creating services..."))
            Service.objects.bulk_create(
                [
                    Service(
                        id=Service.ServiceType.MANAGING,
                        name="Quản lý",
                        price=5000,
                    ),
                    Service(
                        id=Service.ServiceType.ACCESS_CARD,
                        name="Thẻ ra vào",
                        price=55000,
                    ),
                    Service(
                        id=Service.ServiceType.RESIDENT_CARD,
                        name="Thẻ cư dân",
                        price=55000,
                    ),
                    Service(
                        id=Service.ServiceType.BICYCLE_PARKING_CARD,
                        name="Thẻ gửi xe đạp",
                        price=2500,
                    ),
                    Service(
                        id=Service.ServiceType.MOTOR_PARKING_CARD,
                        name="Thẻ gửi xe máy",
                        price=8000,
                    ),
                    Service(
                        id=Service.ServiceType.CAR_PARKING_CARD,
                        name="Thẻ gửi xe ô tô",
                        price=50000,
                    ),
                ],
                ignore_conflicts=True,
            )
            self.stdout.write(self.style.SUCCESS("Created services"))

        if ApartmentBuilding.objects.count() == 0:
            self.stdout.write(self.style.HTTP_INFO("Creating apartment building..."))
            ApartmentBuilding.objects.bulk_create(
                [
                    ApartmentBuilding(
                        name="OceanView",
                        address="Nhơn Đức, Nhà Bè, Q.7, TP.HCM",
                        owner="Trần Lê Quốc Thống",
                        phone_number="0909943501",
                        built_date="2022-01-01",
                    ),
                ],
                ignore_conflicts=True,
            )
            self.stdout.write(self.style.SUCCESS("Created apartment building"))

        if Building.objects.count() == 0:
            self.stdout.write(self.style.HTTP_INFO("Creating buildings..."))
            Building.objects.bulk_create(
                [
                    Building(
                        name="A",
                        number_of_floors=2,
                        apartment_building_id=1,
                    ),
                    Building(
                        name="B",
                        number_of_floors=2,
                        apartment_building_id=1,
                    ),
                ],
                ignore_conflicts=True,
            )
            self.stdout.write(self.style.SUCCESS("Created buildings"))

        if ApartmentType.objects.count() == 0:
            self.stdout.write(self.style.HTTP_INFO("Creating apartment types..."))
            ApartmentType.objects.bulk_create(
                [
                    ApartmentType(
                        name="Thường",
                        width=10,
                        height=20,
                        number_of_bedroom=2,
                        number_of_living_room=1,
                        number_of_kitchen=1,
                        number_of_restroom=1,
                    ),
                    ApartmentType(
                        name="Studio",
                        width=12,
                        height=22,
                        number_of_bedroom=3,
                        number_of_living_room=1,
                        number_of_kitchen=1,
                        number_of_restroom=2,
                    ),
                ],
                ignore_conflicts=True,
            )
            self.stdout.write(self.style.SUCCESS("Created apartment types"))

        if Apartment.objects.count() == 0:
            self.stdout.write(self.style.HTTP_INFO("Creating apartments..."))
            import random

            def init_apartments(
                apartments,
                building_name,
                number_of_floors=2,
                number_of_rooms_per_floor=2,
            ):
                for floor in range(1, number_of_floors + 1):
                    for room in range(1, number_of_rooms_per_floor + 1):
                        apartments.append(
                            Apartment(
                                room_number=Apartment.generate_room_number(
                                    building_name, floor, str(room)
                                ),
                                floor=floor,
                                apartment_type_id=random.randint(1, 2),
                                building_id=building_name,
                            ),
                        )

            apartments = []
            init_apartments(apartments, "A")
            init_apartments(apartments, "B")
            Apartment.objects.bulk_create(apartments, ignore_conflicts=True)
            self.stdout.write(self.style.SUCCESS("Created apartments"))
            if User.objects.count() == 1:
                self.stdout.write(
                    self.style.HTTP_INFO("Adding resident to apartment...")
                )
                apartments[0].residents.add(User.objects.first())
                self.stdout.write(self.style.SUCCESS("Added resident to apartment"))

        Application = get_application_model()
        if Application.objects.count() == 0:
            self.stdout.write(self.style.HTTP_INFO("Creating oauth2 application..."))
            Application.objects.create(
                name=settings.COMPANY_NAME,
                client_type=settings.CLIENT_TYPE,
                authorization_grant_type=settings.GRANT_TYPE,
                user_id=User.objects.first().resident_id,
                client_id=settings.CLIENT_ID,
                client_secret=settings.CLIENT_SECRET,
            )
            self.stdout.write(self.style.SUCCESS("Created oauth2 application"))

        self.stdout.write(self.style.SUCCESS("Default data created successfully."))
