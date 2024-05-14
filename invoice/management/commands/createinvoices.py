from datetime import datetime, timedelta

from django.core.management.base import BaseCommand

from invoice.models import Invoice, InvoiceDetail
from service.models import MyBaseServiceStatus, ServiceRegistration


class Command(BaseCommand):
    help = "Create invoices for residents every month"

    def handle(self, *args, **kwargs):
        now = datetime.now()
        first_day_of_month = now.replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        last_day_of_month = first_day_of_month.replace(
            month=first_day_of_month.month % 12 + 1, day=1
        ) - timedelta(days=1)

        service_registrations = ServiceRegistration.objects.filter(
            status=MyBaseServiceStatus.Status.APPROVED,
            created_date__gte=first_day_of_month,
            created_date__lte=last_day_of_month,
        )

        residents = service_registrations.values_list("resident", flat=True).distinct()

        for resident in residents:
            invoice = Invoice.objects.create(
                resident_id=resident, due_date=last_day_of_month + timedelta(days=15)
            )

            total_amount = 0
            for service_registration in service_registrations.filter(
                resident_id=resident
            ):
                service = service_registration.service
                price_per_day = service.price / last_day_of_month.day
                days_used = self.calculate_days_used(service_registration)

                detail_amount = price_per_day * days_used

                total_amount += detail_amount

                InvoiceDetail.objects.create(
                    invoice=invoice,
                    service_registration=service_registration,
                    amount=detail_amount,
                )

            invoice.total_amount = total_amount
            invoice.save()

    def calculate_days_used(self, registration):
        today = datetime.now()
        last_day_of_month = today.replace(
            day=1, month=today.month % 12 + 1
        ) - timedelta(days=1)
        last_day_of_month_date = last_day_of_month.date()
        created_datetime = datetime.combine(
            registration.created_date, datetime.min.time()
        )
        days_used = (last_day_of_month_date - created_datetime.date()).days + 1
        days_used = min(days_used, last_day_of_month.day)
        return days_used
