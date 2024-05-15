from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiParameter

from invoice.models import Invoice
from invoice.serializers import InvoiceSerializer
from service.models import Service
from utils import format

INVOICE_LIST = {
    "description": "Get invoices",
    "request": InvoiceSerializer,
    "responses": {200: InvoiceSerializer},
    "parameters": [
        OpenApiParameter(
            name="q",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Search invoices",
            examples=[
                OpenApiExample("Example", value="INV064393"),
            ],
        ),
        OpenApiParameter(
            name="status",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Include invoice status",
            examples=[
                OpenApiExample(
                    "Example", value=format.format_enum_values(Invoice.InvoiceStatus)
                ),
            ],
        ),
        OpenApiParameter(
            name="_status",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Exclude invoice status",
            examples=[
                OpenApiExample(
                    "Example", value=format.format_enum_values(Invoice.InvoiceStatus)
                ),
            ],
        ),
        OpenApiParameter(
            name="category",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Category service",
            examples=[
                OpenApiExample(
                    "Example", value=format.format_enum_values(Service.ServiceType)
                ),
            ],
        ),
    ],
    "examples": [
        OpenApiExample(
            "Example",
            value={
                "2024": [
                    {
                        "id": "INV043923",
                        "created_date": "2024-04-19T16:26:37.203Z",
                        "total_amount": "5350000",
                        "status": format.format_enum_values(Invoice.InvoiceStatus),
                    }
                ]
            },
            response_only=True,
        )
    ],
}

INVOICE_RETRIEVE = {
    "description": "Get an invoice",
    "request": InvoiceSerializer,
    "responses": {200: InvoiceSerializer},
    "examples": [
        OpenApiExample(
            "Example",
            value={
                "id": "INV043923",
                "created_date": "2024-04-19T16:26:37.203Z",
                "total_amount": "5350000",
                "status": format.format_enum_values(Invoice.InvoiceStatus),
                "invoicedetail_set": [
                    {"service_name": "The gui xe", "amount": "520646"}
                ],
            },
            response_only=True,
        )
    ],
}

INVOICE_ONLINE_WALLET_PAYMENT = {
    "description": "Pay invoice with online wallet",
    "request": None,
    "responses": {200: OpenApiTypes.STR},
}

INVOICE_ONLINE_WALLET_RETURN = {
    "description": "Return from online wallet",
    "request": None,
    "responses": {200: OpenApiTypes.STR},
}
