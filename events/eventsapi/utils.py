from django.core.mail import EmailMessage
import os
import smtplib
import yagmail
from .models import User

class Util:
    @staticmethod
    def send_email(data):
        yag = yagmail.SMTP(user=os.environ.get[Email_host],password=os.environ.get[Email_pass])
        yag.send(to=data['to_email'], subject=data['email_subject'], contents=data['email_body'])
