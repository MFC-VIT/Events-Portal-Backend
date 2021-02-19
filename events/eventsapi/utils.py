from django.core.mail import EmailMessage
import os
import smtplib
import yagmail
from .models import UserAccount

class Util:
    @staticmethod
    def send_email(data):
        yag = yagmail.SMTP(user=os.environ.get('EMAIL_HOST'),password=os.environ.get('EMAIL_PASSWORD'))
        yag.send(to=data['to_email'], subject=data['email_subject'], contents=data['email_body'])

    # @staticmethod
    # def send_email_by_name(data):
    #     yag = yagmail.SMTP(user=os.environ.get['EMAIL_HOST'],password=os.environ.get['EMAIL_PASSWORD'])
    #     for em in data['to_email']:
    #         user = User.objects.get(email = em)
    #         user_email_temp = data['email_body'].replace('{{ name }}',user.username)
    #         yag.send(to=em, subject=data['email_subject'], contents=user_email_temp)
