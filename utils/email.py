import threading

from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template

"""
A class representing an email message to be sent.

Args:
    subject (str): The subject of the email.
    content (dict): The content of the email including text and HTML content.
    recipient_list (list): A list of recipients for the email.

Returns:
    int: The number of emails sent.
"""


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


"""
A thread class for sending emails asynchronously.

Args:
    subject (str): The subject of the email.
    content (dict): The content of the email.
    recipient_list (list): A list of recipients for the email.

Returns:
    None
"""


class EmailThread(Email, threading.Thread):
    def __init__(self, subject, content, recipient_list):
        super().__init__(subject, content, recipient_list)
        threading.Thread.__init__(self)

    def run(self):
        super().send()


"""
Render the content of an email template using the provided context data.

Args:
    template (str): The name of the email template.
    context (dict): The context data to be used in rendering the template.

Returns:
    dict: A dictionary containing the rendered text and HTML content of the email template.
"""


def render_content(template, context):
    plaintext = get_template(f"{template}.txt")
    html = get_template(f"{template}.html")

    return {
        "text_content": plaintext.render(context),
        "html_content": html.render(context),
    }


"""
Send an email with the specified subject, template, and recipient list.

Args:
    subject (str): The subject of the email.
    template (str): The template content of the email.
    recipient_list (list): A list of recipients for the email.
    **context: Additional context data to be used in rendering the template.

Returns:
    None
"""


def send_mail(subject, template, recipient_list, **context):
    return Email(subject, render_content(template, context), recipient_list).send()


"""
Send an email asynchronously with the specified subject, template, and recipient list.

Args:
    subject (str): The subject of the email.
    template (str): The template content of the email.
    recipient_list (list): A list of recipients for the email.
    **context: Additional context data to be used in rendering the template.

Returns:
    None
"""


def send_mail_async(subject, template, recipient_list, **context):
    EmailThread(subject, render_content(template, context), recipient_list).start()
