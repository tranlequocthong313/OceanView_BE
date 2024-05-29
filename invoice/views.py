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
from invoice import momo
from notification.manager import NotificationManager
from notification.types import EntityType
from utils import get_logger, token

from . import serializers, swaggers
from .models import Invoice, OnlineWallet, Payment, ProofImage

log = get_logger(__name__)


class InvoiceView(ListAPIView, RetrieveAPIView, ViewSet):
    serializer_class = serializers.InvoiceSerializer
    MOMO_SUCCESS_CODE = 0
    VNPAY_SUCCESS_CODE = "00"

    def get_queryset(self):
        queries = Invoice.objects.filter(deleted=False)
        if q := self.request.query_params.get("q"):
            queries = queries.filter(id__icontains=q)
        if status := self.request.query_params.get("status"):
            queries = queries.filter(status=status)
        if _status := self.request.query_params.get("_status"):
            queries = queries.exclude(status=_status)
        if category := self.request.query_params.get("category"):
            category = [item.strip() for item in category.split(",")]
            queries = queries.filter(
                invoicedetail__service_registration__service__id__in=category
            )
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
        invoice.wait_for_approval()
        NotificationManager.create_notification(
            entity=proof_image,
            entity_type=EntityType.INVOICE_PROOF_IMAGE_PAYMENT,
            sender=request.user,
        )
        log.info("Created proof image payment successfully")
        return Response(
            "Created proof image payment successfully", status=status.HTTP_201_CREATED
        )

    @extend_schema(**swaggers.INVOICE_ONLINE_WALLET_PAYMENT)
    @action(
        methods=["POST"],
        url_path="payment/vnpay",
        detail=True,
    )
    @transaction.atomic
    def payment_vnpay(self, request, pk=None):
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
            log.error(f"Vnpay payment failed:::{r.json()}")
            return Response(
                "Internal server error", status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        payment_url = r.json()["payment_url"]
        parsed_url = urlparse(payment_url)
        vnpay_reference_number = parse_qs(parsed_url.query)["vnp_TxnRef"][0]
        vnpay_billing = Billing.objects.filter(
            reference_number=vnpay_reference_number
        ).first()
        if not vnpay_billing:
            log.error(f"Vnpay payment failed, not found vnpay billing:::{r.json()}")
            return Response("Not found transaction", status=status.HTTP_404_NOT_FOUND)

        payment = Payment.objects.create(
            method=Payment.PaymentMethod.ONLINE_WALLET,
            status=Payment.PaymentStatus.CONFIRMING,
            invoice=invoice,
            total_amount=invoice.total_amount,
        )
        OnlineWallet.objects.create(
            payment=payment,
            wallet_type=OnlineWallet.WalletType.VNPAY,
            reference_number=vnpay_reference_number,
        )
        log.info("Created online wallet payment successfully")
        return Response(r.json(), status.HTTP_200_OK)

    @extend_schema(**swaggers.INVOICE_ONLINE_WALLET_RETURN)
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
        if (
            not r.ok
            or "RspCode" not in r.json()
            or r.json()["RspCode"] != self.VNPAY_SUCCESS_CODE
        ):
            log.error(f"Vnpay payment failed:::{r.json()}")
            return Response(
                "Transaction is not success", status=status.HTTP_400_BAD_REQUEST
            )

        parsed_url = urlparse(request.get_full_path())
        vnpay_reference_number = parse_qs(parsed_url.query)["vnp_TxnRef"][0]
        online_wallet = OnlineWallet.objects.filter(
            wallet_type=OnlineWallet.WalletType.VNPAY,
            reference_number=vnpay_reference_number,
        ).first()
        if not online_wallet:
            log.error(f"Vnpay payment failed, not found vnpay billing:::{r.json()}")
            return Response("Not found transaction", status=status.HTTP_404_NOT_FOUND)
        paid = online_wallet.pay()
        if not paid:
            log.error(
                "Vnpay payment failed, can't set success status for payment model"
            )
            return Response(
                "Internal server error", status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        log.info("Paid online wallet payment successfully")
        return Response("Paid successfully", status.HTTP_200_OK)

    # TODO: Handle when users exit the transaction before finishing
    @extend_schema(**swaggers.INVOICE_ONLINE_WALLET_PAYMENT)
    @action(
        methods=["POST"],
        url_path="payment/momo",
        detail=True,
    )
    @transaction.atomic
    def payment_momo(self, request, pk=None):
        invoice = self.get_object()
        r = momo.pay(invoice)
        if not r.ok:
            log.error(f"Momo payment failed:::{r.json()}")
            return Response(
                "Internal server error", status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        data = r.json()
        if data["resultCode"] != self.MOMO_SUCCESS_CODE:
            log.error(f"Momo payment failed:::{r.json()}")
            return Response(
                "Transaction is not success", status=status.HTTP_400_BAD_REQUEST
            )
        payment = Payment.objects.create(
            method=Payment.PaymentMethod.ONLINE_WALLET,
            status=Payment.PaymentStatus.CONFIRMING,
            invoice=invoice,
            total_amount=invoice.total_amount,
        )
        OnlineWallet.objects.create(
            payment=payment,
            wallet_type=OnlineWallet.WalletType.MOMO,
            reference_number=data["requestId"],
        )
        log.info("Created online wallet payment successfully")
        return Response(
            {
                "pay_url": data["payUrl"],
                "deeplink": data["deeplink"],
                "qrcode_url": data["qrCodeUrl"],
            },
            status.HTTP_200_OK,
        )

    @extend_schema(**swaggers.INVOICE_ONLINE_WALLET_RETURN)
    @action(
        methods=["POST"],
        url_path="payment/ipn-momo",
        detail=False,
        permission_classes=[AllowAny],
    )
    @transaction.atomic
    def ipn_momo(self, request):
        if (
            "resultCode" not in request.data
            or request.data["resultCode"] != self.MOMO_SUCCESS_CODE
        ):
            log.error(f"Momo payment failed:::{request.data}")
            return Response(
                "Transaction is not success", status=status.HTTP_400_BAD_REQUEST
            )
        online_wallet = OnlineWallet.objects.filter(
            reference_number=request.data["requestId"]
        ).first()
        if not online_wallet:
            log.error(
                f"Momo payment failed, not found momo transaction:::{request.data}"
            )
            return Response("Not found transaction", status=status.HTTP_404_NOT_FOUND)
        if online_wallet.payment.total_amount != int(request.data["amount"]):
            log.error(f"Momo payment failed, amounts are not matching:::{request.data}")
            return Response(
                "Redirected data is invalid", status=status.HTTP_400_BAD_REQUEST
            )
        paid = online_wallet.pay(transaction_id=request.data["transId"])
        if not paid:
            log.error("Momo payment failed, can't set success status for payment model")
            return Response(
                "Internal server error", status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        log.info("IPN paid online wallet payment successfully")
        return Response(status.HTTP_204_NO_CONTENT)

    @extend_schema(**swaggers.INVOICE_ONLINE_WALLET_RETURN)
    @action(
        methods=["GET"],
        url_path="payment/momo",
        detail=False,
        permission_classes=[AllowAny],
    )
    @transaction.atomic
    def return_momo(self, request):
        if "resultCode" not in request.GET or request.GET.get("resultCode") != str(
            self.MOMO_SUCCESS_CODE
        ):
            log.error("Momo payment failed")
            return Response("Bad request", status=status.HTTP_400_BAD_REQUEST)
        online_wallet = OnlineWallet.objects.filter(
            reference_number=request.GET.get("requestId")
        ).first()
        if not online_wallet:
            log.error(
                f"Momo payment failed, not found momo transaction:::{request.GET}"
            )
            return Response("Not found transaction", status=status.HTTP_400_BAD_REQUEST)
        if online_wallet.payment.total_amount != int(request.GET.get("amount")):
            log.error(f"Momo payment failed, amounts are not matching:::{request.GET}")
            return Response(
                "Redirected data is invalid",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        log.info("Redirect paid online wallet payment successfully")
        return Response("Paid with Momo successfully", status.HTTP_200_OK)
