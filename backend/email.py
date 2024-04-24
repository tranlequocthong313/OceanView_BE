import ssl

from django.core.mail.backends.smtp import EmailBackend as SMTPBackend
from django.utils.functional import cached_property

"""
A custom email backend class that extends SMTPBackend to handle SSL context configuration.

This class provides an SSL context property based on the presence of SSL certificate and key files.

Returns:
    SSLContext: The SSL context for the email backend.
"""


class EmailBackend(SMTPBackend):
    @cached_property
    def ssl_context(self):
        if self.ssl_certfile or self.ssl_keyfile:
            ssl_context = ssl.SSLContext(protocol=ssl.PROTOCOL_TLS_CLIENT)
            ssl_context.load_cert_chain(self.ssl_certfile, self.ssl_keyfile)
        else:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

        return ssl_context
