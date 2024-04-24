from drf_spectacular.utils import extend_schema
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.viewsets import ViewSet

from . import serializers, swaggers
from .models import Invoice


class InvoiceView(ListAPIView, RetrieveAPIView, ViewSet):
    queryset = Invoice.objects.all()
    serializer_class = serializers.InvoiceSerializer

    def get_queryset(self):
        queries = self.queryset

        if q := self.request.query_params.get("q"):
            queries = queries.filter(id__icontains=q)

        return queries

    @extend_schema(**swaggers.INVOICE_LIST)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(**swaggers.INVOICE_RETRIEVE)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
