# from google.cloud import logging
# from django.conf import settings

# # Instantiates a client
# client = logging.Client(credentials=settings.GS_CREDENTIALS)

# # The name of the log to write to
# log_name = "my-log"
# # Selects the log to write to
# logger = client.logger(log_name)

# # The data to log
# text = "Hello, world!"

# # Writes the log entry
# logger.log_text(text)

# print("Logged: {}".format(text))



# def write_entry(logger_name):

#     # This log can be found in the Cloud Logging console under 'Custom Logs'.
#     logger = client.logger(logger_name)

#     # Make a simple text log
#     logger.log_text("Hello, world!")

#     # Simple text log with severity.
#     logger.log_text("Goodbye, world!", severity="ERROR")

#     # Struct log. The struct can be any JSON-serializable dictionary.
#     logger.log_struct(
#         {
#             "name": "King Arthur",
#             "quest": "Find the Holy Grail",
#             "favorite_color": "Blue",
#         }
#     )

#     print("Wrote logs to {}.".format(logger.name))