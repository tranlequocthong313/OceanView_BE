from urllib.parse import parse_qs, urlparse

import requests
from cloudinary.utils import urllib
from django.db import transaction
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from vnpay.models import Billing

from app import settings
from notification.manager import AdminNotificationManager
from utils import get_logger, token

from . import serializers, swaggers
from .models import Invoice, OnlineWallet, Payment, ProofImage

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
    @transaction.atomic
    def payment_proof_image(self, request, pk=None):
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

    # TODO: Split payment businesses to another module
    # TODO: Prevent client request directly to vnpay apis
    @extend_schema(**swaggers.INVOICE_VNPAY_PAYMENT)
    @action(
        methods=["POST"],
        url_path="payment/vnpay",
        detail=True,
    )
    @transaction.atomic
    def payment_vnpay(self, request, pk=None):
        log.info(request.data)
        invoice = self.get_object()

        r = requests.post(
            url=f"{settings.HOST}/vnpay/payment_url/?token={token.generate_token(settings.SECRET_KEY)}",
            headers={
                "AUTHORIZATION": request.META["HTTP_AUTHORIZATION"],
            },
            data={"amount": int(invoice.total_amount)},
        )
        log.info("Requested to VNPay successfully")
        if not r.ok or "payment_url" not in r.json():
            log.error("Vnpay payment failed", r.json())
            return Response(
                "Vnpay server error", status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        payment_url = r.json()["payment_url"]
        parsed_url = urlparse(payment_url)
        vnpay_reference_number = parse_qs(parsed_url.query)["vnp_TxnRef"][0]
        vnpay_billing = Billing.objects.filter(
            reference_number=vnpay_reference_number
        ).first()
        if not vnpay_billing:
            log.error("Vnpay payment failed, not found vnpay billing", r.json())
            return Response(
                "Vnpay server error", status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        payment = Payment.objects.create(
            method=Payment.PaymentMethod.ONLINE_WALLET,
            status=Payment.PaymentStatus.CONFIRMING,
            invoice=invoice,
            total_amount=invoice.total_amount,
        )
        OnlineWallet.objects.create(payment=payment, vnpay_billing=vnpay_billing)
        log.info("Created online wallet payment successfully")
        return Response(r.json(), status.HTTP_200_OK)

    # TODO: Prevent client request directly to vnpay apis
    @extend_schema(**swaggers.INVOICE_VNPAY_RETURN)
    @action(
        methods=["GET"],
        url_path="payment/vnpay",
        detail=False,
        permission_classes=[AllowAny],
    )
    @transaction.atomic
    def return_vnpay(self, request):
        r = requests.get(
            url=f"{settings.HOST}/vnpay/payment_ipn/?{urllib.parse.urlencode(request.GET, doseq=False)}&token={token.generate_token(settings.SECRET_KEY)}",
        )
        log.info("Requested to VNPay successfully")
        vnpay_success_code = "00"
        if (
            not r.ok
            or "RspCode" not in r.json()
            or r.json()["RspCode"] != vnpay_success_code
        ):
            log.error("Vnpay payment failed", r.json())
            return Response(
                "Vnpay server error", status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        parsed_url = urlparse(request.get_full_path())
        vnpay_reference_number = parse_qs(parsed_url.query)["vnp_TxnRef"][0]
        online_wallet = OnlineWallet.objects.filter(
            vnpay_billing__reference_number=vnpay_reference_number
        ).first()
        if not online_wallet:
            log.error("Vnpay payment failed, not found vnpay billing", r.json())
            return Response(
                "Vnpay server error", status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        paid = online_wallet.payment.pay()
        if not paid:
            log.error(
                "Vnpay payment failed, can't set success status for payment model"
            )
            return Response(
                "Internal server error", status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        log.info("Paid online wallet payment successfully")
        return Response("Paid successfully", status.HTTP_200_OK)
