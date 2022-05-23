from backend.python_rq.python_rq import email_queue
# from service.email.email_job import send_email_job
# from automation import jobs
from ..rq.job import enqueue_email_queue
class EmailService:
    @staticmethod
    def send_email(job, subject, email, content, file = None, lang = 'en'):

        email_queue.enqueue(
            job,
            kwargs={
                "subject": subject,
                "email": email, 
                "content":content,
                "file":file,
                "lang":lang
            }, result_ttl=10, failure_ttl=10)



    @staticmethod
    def send_email_template(job, subject, email, template, parameters, file=None, lang="en"):

        enqueue_email_queue(job, subject, email, template, parameters, file, lang)