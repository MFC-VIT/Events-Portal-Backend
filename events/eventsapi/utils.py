from django.core.mail import EmailMessage
import os
import smtplib
import yagmail


class Util:
    @staticmethod
    def send_email(data):
        yag = yagmail.SMTP(user=os.environ.get('EMAIL_HOST_USER'), password=os.environ.get('EMAIL_HOST_PASSWORD'))
        yag.send(to=data['to_email'], subject=data['email_subject'], contents=data['email_body'])
