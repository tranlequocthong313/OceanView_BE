from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiParameter

from invoice.models import Invoice
from invoice.serializers import InvoiceSerializer

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
    ],
    "examples": [
        OpenApiExample(
            "Example",
            value={
                "id": "INV043923",
                "created_date": "2024-04-19T16:26:37.203Z",
                "updated_date": "2024-04-19T16:26:37.204Z",
                "amount": "5350000",
                "due_date": "2024-04-19",
                "payment_status": Invoice.PAYMENT_STATUS.PENDING,
                "resident": "240269",
                "invoice_type": 1,
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
                "updated_date": "2024-04-19T16:26:37.204Z",
                "amount": "5350000",
                "due_date": "2024-04-19",
                "payment_status": "PENDING",
                "resident": "240269",
                "invoice_type": 1,
            },
            response_only=True,
        )
    ],
}
