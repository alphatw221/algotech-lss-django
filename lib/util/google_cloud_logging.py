from google.cloud import logging
from django.conf import settings

# Instantiates a client
client = logging.Client(credentials=settings.GS_CREDENTIALS)


class ApiLogEntry():
    name="lss-api-log"
    logger = client.logger(name)

    @classmethod
    def write_entry(cls, message):
        cls.logger.log_text(message)
