import hashlib
import hmac
import uuid

import requests

from app import settings


def pay(invoice):
    if not invoice:
        raise ValueError("invoice must not be null")
    request_id = str(uuid.uuid4())
    order_id = f"{invoice.pk}-{request_id}"
    # NOTE: Dev and Prod env using the same momo api key, what happends is order ids are conflicted. So I add an uuid to solve it
    print("ORDER_ID::", order_id)
    order_info = f"{invoice.resident.__str__()} thanh toán hóa đơn {invoice.__str__()}"
    amount = str(int(invoice.total_amount))
    raw_signature = (
        f"accessKey={settings.MOMO_ACCESS_KEY}&amount={amount}&extraData=&ipnUrl={settings.MOMO_IPN_URL}&orderId={order_id}"
        + "&orderInfo="
        + order_info
        + "&partnerCode="
        + settings.MOMO_PARTNER_CODE
        + "&redirectUrl="
        + settings.MOMO_REDIRECT_URL
        + "&requestId="
        + request_id
        + "&requestType="
        + settings.MOMO_REQUEST_TYPE
    )
    h = hmac.new(
        bytes(settings.MOMO_SECRET_KEY, "utf8"),
        bytes(raw_signature, "utf8"),
        hashlib.sha256,
    )
    signature = h.hexdigest()
    data = {
        "partnerCode": settings.MOMO_PARTNER_CODE,
        "partnerName": settings.MOMO_PARTNER_NAME,
        "storeId": settings.MOMO_STORE_ID,
        "requestId": request_id,
        "amount": amount,
        "orderId": order_id,
        "orderInfo": order_info,
        "redirectUrl": settings.MOMO_REDIRECT_URL,
        "ipnUrl": settings.MOMO_IPN_URL,
        "lang": settings.MOMO_LANG,
        "extraData": "",
        "requestType": settings.MOMO_REQUEST_TYPE,
        "signature": signature,
    }
    return requests.post(settings.MOMO_ENDPOINT, json=data)
