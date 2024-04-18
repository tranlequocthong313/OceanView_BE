from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from .models import Invoice
from .serializers import InvoiceSerializer, PaymentSerializer


class InvoiceView(ViewSet, ListAPIView, RetrieveAPIView):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer

    def get_queryset(self):
        queries = self.queryset

        q = self.request.query_params.get("q")
        if q:
            queries = queries.filter(id__icontains=q)

        return queries

    @extend_schema(
        request=PaymentSerializer,
        responses={200: PaymentSerializer},
    )
    @action(
        methods=["post"],
        url_path="payment",
        detail=True,
        serializer_class=PaymentSerializer,
    )
    def pay(self, request, pk):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(self.serializer_class(serializer.save(invoice_id=pk)).data)
