from django.db.models import F
from rest_framework.serializers import (
    ImageField,
    ModelSerializer,
    SerializerMethodField,
)

from .models import Invoice, ProofImage


class InvoiceSerializer(ModelSerializer):
    class Meta:
        model = Invoice
        fields = ["status", "id", "total_amount", "created_date"]


class InvoiceDetailSerializer(ModelSerializer):
    invoicedetail_set = SerializerMethodField()

    def get_invoicedetail_set(self, instance):
        return instance.invoicedetail_set.annotate(
            service_name=F("service_registration__service__name")
        ).values("service_name", "amount")

    class Meta:
        model = InvoiceSerializer.Meta.model
        fields = InvoiceSerializer.Meta.fields + ["invoicedetail_set"]


class ProofImageSerializer(ModelSerializer):
    image = ImageField(required=True, write_only=True)

    class Meta:
        model = ProofImage
        fields = ["image"]
