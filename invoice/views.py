from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from notification.manager import AdminNotificationManager
from utils import get_logger

from . import serializers, swaggers
from .models import Invoice, Payment, ProofImage

log = get_logger(__name__)


class InvoiceView(ListAPIView, RetrieveAPIView, ViewSet):
    serializer_class = serializers.InvoiceSerializer

    def get_queryset(self):
        queries = Invoice.objects.filter(deleted=False)

        if q := self.request.query_params.get("q"):
            queries = queries.filter(id__icontains=q)

        return queries

    @extend_schema(**swaggers.INVOICE_LIST)
    def list(self, request):
        invoices = self.get_queryset().filter(resident=request.user)
        invoices_by_year = {}
        for invoice in invoices:
            year = invoice.created_date.year
            if year not in invoices_by_year:
                invoices_by_year[year] = []
            invoices_by_year[year].append(self.serializer_class(invoice).data)

        return Response(invoices_by_year)

    @extend_schema(**swaggers.INVOICE_RETRIEVE)
    def retrieve(self, request, *args, **kwargs):
        return Response(
            serializers.InvoiceDetailSerializer(self.get_object()).data,
            status=status.HTTP_200_OK,
        )

    @action(
        methods=["POST"],
        url_path="payment",
        detail=True,
        serializer_class=serializers.ProofImageSerializer,
    )
    def pay_by_proof_image(self, request, pk=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        invoice = self.get_object()
        payment = Payment.objects.create(
            method=Payment.PaymentMethod.PROOF_IMAGE,
            status=Payment.PaymentStatus.CONFIRMING,
            invoice=invoice,
            total_amount=invoice.total_amount,
        )
        proof_image = ProofImage.objects.create(
            payment=payment, image=serializer.validated_data["image"]
        )
        AdminNotificationManager.create_notification_for_proof_image(
            request, proof_image
        )
        log.info("Created proof image payment successfully")
        return Response(
            "Created proof image payment successfully", status=status.HTTP_201_CREATED
        )
