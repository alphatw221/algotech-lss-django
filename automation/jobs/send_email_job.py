import os
import django

try:
    os.environ['DJANGO_SETTINGS_MODULE'] = 'lss.settings'  # for rq_job
    django.setup()
except Exception:
    pass

from django.conf import settings
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.template.loader import render_to_string
from api.utils.error_handle.error_handler.email_error_handler import email_error_handler
from django.utils import translation

@email_error_handler
def send_email_job(subject, email, template_name=None, content=None, parameters={}, file=None, lang='en'):
    
    mail = MIMEMultipart()
    mail['Subject'] = subject
    mail['From'] = settings.EMAIL_HOST_USER
    mail['To'] = email

    if template_name:
        with translation.override(lang):
            rendered = render_to_string(template_name, parameters)
        mail.attach(MIMEText(rendered, 'html'))
    elif content:
        mail.attach(MIMEText(content, 'html'))
    
    if file:
        with open(file, "rb") as f:
            part = MIMEApplication(
                f.read(),
                Name=os.path.basename(file)
            )
        part['Content-Disposition'] = f"attachment; filename='{os.path.basename(file)}'" 
        mail.attach(part)

    smtp = smtplib.SMTP_SSL(settings.EMAIL_HOST)
    smtp.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
    smtp.sendmail(settings.EMAIL_HOST_USER, email, mail.as_string())
    smtp.quit()