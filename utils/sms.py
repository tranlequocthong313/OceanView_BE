import threading

from django.conf import settings
from django.template.loader import get_template
from twilio.rest import Client

from app import settings

TWILIO_SERVICE_SID = settings.TWILIO_SERVICE_SID


client = Client(settings.TWILIO_SID, settings.TWILIO_TOKEN)


def verify_otp(to, otp):
    return (
        client.verify.v2.services(TWILIO_SERVICE_SID)
        .verification_checks.create(to=f"+84{to}", code=otp)
        .status
        == "approved"
    )


class SMS:
    def __init__(self, content, to):
        self.to = (f"+84{to}",)
        self.content = content

    def send(self):
        client.messages.create(
            to=self.to, from_=settings.TWILIO_NUMBER, body=self.content
        )


class SMSThread(SMS, threading.Thread):
    def __init__(self, content, to):
        super().__init__(content, to)
        threading.Thread.__init__(self)

    def run(self):
        super().send()


def render_content(template, context):
    return get_template(f"{template}.txt").render(context)


def send_sms(template, to, **context):
    SMS(render_content(template, context), to).send()


def send_sms_async(template, to, **context):
    SMSThread(render_content(template, context), to).start()


def send_otp(to):
    print(
        client.verify.v2.services(TWILIO_SERVICE_SID).verifications.create(
            to=f"+84{to}", channel="sms"
        )
    )
