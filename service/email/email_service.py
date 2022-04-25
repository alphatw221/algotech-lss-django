from backend.python_rq.python_rq import email_queue
from service.email.email_job import send_email_job


class EmailService:

    @staticmethod
    def send_email(subject, email, content, file = None):

        email_queue.enqueue(
            send_email_job,
            kwargs={
                "subject": subject,
                "email": email, 
                "content":content,
                "file":file
            }, result_ttl=10, failure_ttl=10)



    @staticmethod
    def send_email_template(subject, email, template, parameters, file=None):
        email_queue.enqueue(
            send_email_job,
            kwargs={
                "subject": subject,
                "email": email, 
                "template": template,
                "parameters": parameters,
                "file":file
            }, result_ttl=10, failure_ttl=10)