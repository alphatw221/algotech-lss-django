from ..rq._rq import general_queue
from ..rq.queue import enqueue_general_queue
class EmailService:
    @staticmethod
    def send_email(job, subject, email, content, file = None, lang = 'en'):

        general_queue.enqueue(
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

        enqueue_general_queue(job, subject, email, template, parameters, file, lang)