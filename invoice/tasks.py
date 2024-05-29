from datetime import datetime, timedelta

from django.db.models import Q

from invoice.models import Invoice, InvoiceDetail
from service.models import MyBaseServiceStatus, ServiceRegistration


def calculate_units_used(registration):
    today = datetime.now()
    created_datetime = datetime.combine(registration.created_date, datetime.min.time())
    return (today - created_datetime).days + 1


def create_invoices(payment=ServiceRegistration.Payment.MONTHLY):
    now = datetime.now()
    if payment == ServiceRegistration.Payment.MONTHLY:
        first_day_of_period = now.replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        last_day_of_period = first_day_of_period.replace(
            month=first_day_of_period.month % 12 + 1, day=1
        ) - timedelta(days=1)
        due_date = last_day_of_period + timedelta(days=15)
    elif payment == ServiceRegistration.Payment.DAILY:
        first_day_of_period = now.replace(hour=0, minute=0, second=0, microsecond=0)
        last_day_of_period = first_day_of_period
        due_date = now + timedelta(days=7)

    service_registrations = ServiceRegistration.objects.filter(
        Q(status=MyBaseServiceStatus.Status.APPROVED)
        | Q(
            status=MyBaseServiceStatus.Status.CANCELED,
            previous_status=MyBaseServiceStatus.Status.APPROVED,
        ),
        created_date__gte=first_day_of_period,
        created_date__lte=last_day_of_period,
        payment=payment,
    )

    residents = service_registrations.values_list("resident", flat=True).distinct()

    for resident in residents:
        invoice = Invoice.objects.create(resident_id=resident, due_date=due_date)

        total_amount = 0
        for service_registration in service_registrations.filter(resident_id=resident):
            service = service_registration.service
            units_used = calculate_units_used(service_registration)
            detail_amount = service.price * units_used
            total_amount += detail_amount
            InvoiceDetail.objects.create(
                invoice=invoice,
                service_registration=service_registration,
                amount=detail_amount,
            )

        invoice.total_amount = total_amount
        invoice.save()

    with open(
        "/home/tranlequocthong313/Workspace/lap_trinh_hien_dai/OceanView_BE/cron-log.txt",
        "a",
    ) as file:
        file.write(f"Payment: {payment}\n")
        file.write(f"Now: {now}\n")
        file.write(f"First day of period: {first_day_of_period}\n")
        file.write(f"Last day of period: {last_day_of_period}\n")
        file.write(f"Due date: {due_date}\n\n")
