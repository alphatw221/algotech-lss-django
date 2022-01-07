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

        
        # logger.log_text("Goodbye, world!", severity="ERROR")

        # # Struct log. The struct can be any JSON-serializable dictionary.
        # logger.log_struct(
        #     {
        #         "name": "King Arthur",
        #         "quest": "Find the Holy Grail",
        #         "favorite_color": "Blue",
        #     }
        # )

