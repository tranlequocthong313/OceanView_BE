import threading

from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template


class Email:
    def __init__(self, subject, content, recipient_list):
        self.subject = subject
        self.recipient_list = recipient_list
        self.content = content

    def send(self):
        msg = EmailMultiAlternatives(
            subject=self.subject,
            body=self.content["text_content"],
            to=self.recipient_list,
        )
        msg.attach_alternative(self.content["html_content"], "text/html")
        return msg.send()


class EmailThread(Email, threading.Thread):
    def __init__(self, subject, content, recipient_list):
        super().__init__(subject, content, recipient_list)
        threading.Thread.__init__(self)

    def run(self):
        super().send()


def render_content(template, context):
    plaintext = get_template(f"{template}.txt")
    html = get_template(f"{template}.html")

    return {
        "text_content": plaintext.render(context),
        "html_content": html.render(context),
    }


def send_mail(subject, template, recipient_list, **context):
    return Email(subject, render_content(template, context), recipient_list).send()


def send_mail_async(subject, template, recipient_list, **context):
    EmailThread(subject, render_content(template, context), recipient_list).start()
