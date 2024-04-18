from rest_framework.serializers import ModelSerializer

from .models import Invoice, InvoiceDetail


class InvoiceSerializer(ModelSerializer):
    class Meta:
        model = Invoice
        fields = "__all__"


class PaymentSerializer(ModelSerializer):
    invoice = InvoiceSerializer(read_only=True)

    class Meta:
        model = InvoiceDetail
        fields = "__all__"
