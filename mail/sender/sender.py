from mail.models import Mail
from lss.settings import EMAIL_HOST_USER
from django.core.mail import send_mail
import pendulum, time


# convert email list to save in mongo
def create_mail_queue(mail_list):
    try:
        for mail_info in mail_list:
            Mail.objects.create(
                recipient = mail_info[0], 
                subject = mail_info[1], 
                content = mail_info[2], 
                sent_at = mail_info[3], 
                result = mail_info[4]
            )
        send_email()
    except Exception:
        ...
    

def send_email():
    try:
        mail_set = Mail.objects.filter(sent_at = None)
        for mail in mail_set:
            subject = mail.subject
            message = mail.content
            recipient = str(mail.recipient)
            send_mail(subject, message, EMAIL_HOST_USER, [recipient], fail_silently = False)
            
            mail_info = Mail.objects.get(id = mail.id)
            mail_info.sent_at = pendulum.now()
            mail_info.result = 'success'
            mail_info.save()

            print(f'{pendulum.now()} - {mail.recipient} - {"success"}')
            time.sleep(0.5)

    except Exception:
        ...
        