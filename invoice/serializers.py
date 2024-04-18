from rest_framework.serializers import ModelSerializer

from .models import Invoice


class InvoiceSerializer(ModelSerializer):
    class Meta:
        model = Invoice
        fields = "__all__"
