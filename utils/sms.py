import threading

from django.conf import settings
from django.template.loader import get_template
from twilio.rest import Client

from app import settings

TWILIO_SERVICE_SID = settings.TWILIO_SERVICE_SID


client = Client(settings.TWILIO_SID, settings.TWILIO_TOKEN)

"""
Verify the OTP (One-Time Password) by checking if the provided OTP is valid for the given phone number.

Args:
    to (str): The phone number to which the OTP was sent.
    otp (str): The One-Time Password to verify.

Returns:
    bool: True if the OTP is approved and valid, False otherwise.
"""


def verify_otp(to, otp):
    return (
        client.verify.v2.services(TWILIO_SERVICE_SID)
        .verification_checks.create(to=f"+84{to}", code=otp)
        .status
        == "approved"
    )


"""
A class representing an SMS message to be sent.

Args:
    content (str): The content of the SMS message.
    to (str): The phone number to which the SMS will be sent.

Returns:
    str: The status of the SMS message sending process.
"""


class SMS:
    def __init__(self, content, to):
        self.to = (f"+84{to}",)
        self.content = content

    def send(self):
        return client.messages.create(
            to=self.to, from_=settings.TWILIO_NUMBER, body=self.content
        )


"""
A thread class for sending SMS messages asynchronously.

Args:
    content (str): The content of the SMS message.
    to (str): The phone number to which the SMS will be sent.

Returns:
    None
"""


class SMSThread(SMS, threading.Thread):
    def __init__(self, content, to):
        super().__init__(content, to)
        threading.Thread.__init__(self)

    def run(self):
        super().send()


"""
Render the content of an SMS template using the provided context data.

Args:
    template (str): The name of the SMS template.
    context (dict): The context data to be used in rendering the template.

Returns:
    str: The rendered content of the SMS template.
"""


def render_content(template, context):
    return get_template(f"{template}.txt").render(context)


"""
Send an SMS message using the provided template, recipient, and context data.

Args:
    template (str): The name of the SMS template to use.
    to (str): The recipient phone number.
    **context: Additional context data to be used in rendering the SMS template.

Returns:
    str: The status of the SMS sending process.
"""


def send_sms(template, to, **context):
    return SMS(render_content(template, context), to).send()


"""
Send an SMS message asynchronously using the provided template, recipient, and context data.

Args:
    template (str): The name of the SMS template to use.
    to (str): The recipient phone number.
    **context: Additional context data to be used in rendering the SMS template.

Returns:
    None
"""


def send_sms_async(template, to, **context):
    SMSThread(render_content(template, context), to).start()


"""
Send an OTP (One-Time Password) to the provided phone number using SMS.

Args:
    to (str): The recipient phone number to send the OTP.

Returns:
    str: The status of the OTP verification process.
"""


def send_otp(to):
    return client.verify.v2.services(TWILIO_SERVICE_SID).verifications.create(
        to=f"+84{to}", channel="sms"
    )
