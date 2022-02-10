import pendulum, time, smtplib

from django.conf import settings
from django.core.mail import send_mail as django_send_mail

from mail.models import Mail
from mail.sender.mail_info import MailInfo
from email.mime.text import MIMEText
from api.utils.error_handle.error.api_error import ApiVerifyError


# # convert email list to save in mongo
# def create_mail_queue(mail_list):
#     try:
#         for mail_info in mail_list:
#             Mail.objects.create(
#                 recipient = mail_info.recipient, 
#                 subject = mail_info.subject, 
#                 content = mail_info.content, 
#                 sent_at = None, 
#                 result = 'unsent'
#             )
#         send_email()
#     except Exception:
#         ...
    

# def send_email():
#     try:
#         mail_set = Mail.objects.filter(sent_at = None)
#         for mail in mail_set:
#             subject = mail.subject
#             message = mail.content
#             recipient = str(mail.recipient)
#             django_send_mail(subject, message, settings.EMAIL_HOST_USER, [recipient], fail_silently = False)
            
#             mail_info = Mail.objects.get(id = mail.id)
#             mail_info.sent_at = pendulum.now()
#             mail_info.result = 'success'
#             mail_info.save()

#             print(f'{pendulum.now()} - {mail.recipient} - {"success"}')
#             time.sleep(0.5)

#     except Exception:
#         ...


def send_Email(mail_list):
    try:
        subject = mail_list[1]
        message = mail_list[2]
        recipient = mail_list[0]
        django_send_mail(subject, message, settings.EMAIL_HOST_USER, [recipient], fail_silently = False)

        print(f'{pendulum.now()} - {mail_list[0]} - {"success"}')
        time.sleep(0.5)

    except Exception:
        #TODO writing error in order meta 
        pass
        # raise ApiVerifyError('email address wrong format')


def send_smtp_mail(customer_email, mail_subject, mail_content):
    mailserver = settings.EMAIL_HOST
    username_send = settings.EMAIL_HOST_USER
    password = settings.EMAIL_HOST_PASSWORD
    username_recv = customer_email
    mail = MIMEText(mail_content, 'html')
    mail['Subject'] = mail_subject
    mail['From'] = username_send
    mail['To'] = username_recv
    
    smtp = smtplib.SMTP_SSL(mailserver)
    smtp.login(username_send, password)
    smtp.sendmail(username_send, username_recv, mail.as_string())
    smtp.quit()

    print(f'{pendulum.now()} - {customer_email} - {"success"}')