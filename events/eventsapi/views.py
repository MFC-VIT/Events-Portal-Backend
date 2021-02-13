from rest_framework import viewsets,generics,status,views,permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import User,Event,Event_Registration
from .serializers import (RegisterSerializer,LoginSerializer,
                            LogoutSerializer,
                            EmailVerificationSerializer,
                            ResetPasswordEmailRequestSerializer,
                            GoogleSocialAuthSerializer,
                            SetNewPasswordSerializer,EventRegisterSerializer, FeedbackSerializer)
from rest_framework.generics import ListCreateAPIView,GenericAPIView
import random
from django.shortcuts import render
from rest_framework_simplejwt.tokens import RefreshToken
import jwt
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import Util
from django.shortcuts import redirect
from .renderers import UserRenderer
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from .admin import SendEmailForm
from django.views.generic.edit import FormView
from django.urls import reverse_lazy

# Create your views here.
##########################################################


def generate_otp():
    key = random.randint(100,999)
    counter = random.randint(100,999)
    otp_str = str(key) + str(counter)
    otp = int(otp_str)
    return otp

###########################################################
class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    renderer_classes = (UserRenderer,)
    def post(self,request):
        user=request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data
        user = User.objects.get(email=user_data['email'])
        user_otp = generate_otp()
        user.otp = user_otp
        user.save()
        token = RefreshToken.for_user(user).access_token
        email_body = 'Hi '+ user.username +  ' Use the OTP below to verify your email \n' + str(user_otp)
        data = {'email_body': email_body, 'to_email': user.email,
                'email_subject': 'Verify your email for MFC recruitment portal'}

        Util.send_email(data)
        return Response(user_data, status=status.HTTP_201_CREATED)

class VerifyEmail(views.APIView):
    serializer_class = EmailVerificationSerializer
    def post(self, request):
        otp = request.data['otp']
        email = request.data['email']
        try:
            user = User.objects.get(email = email)
            if otp == user.otp:
                if not user.is_verified:
                    user.is_verified = True
                    user.save()
                    email_body = '<h1> Hello ' + user.username + ', Greetings from MFCVIT, </h1>' + 'Your account has been successfully activated. \n' + 'You can now go to recruitment portal and attempt test for all domains.'
                    data = {'email_body': email_body, 'to_email': user.email,
                            'email_subject': 'Account activation successful'}
                    Util.send_email(data)
                return Response({'email': 'Successfully activated'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'error': 'Invalid OTP or Email'}, status=status.HTTP_400_BAD_REQUEST)

class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    def post(self,request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

class RequestPasswordResetEmail(generics.GenericAPIView):
    serializer_class = ResetPasswordEmailRequestSerializer
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        email = request.data.get('email', '')
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(request=request).domain
            relativeLink = reverse('api:password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})[19:]
            redirect_url = request.data.get('redirect_url', '')
            absurl = 'https://recruitments.mfcvit.in/user/newpassword' + relativeLink
            email_body = '<h1>Greetings from MFC VIT</h1> \n Use link below to reset your password  \n' + absurl
            data = {'email_body': email_body, 'to_email': user.email,
                    'email_subject': 'Reset your passsword'}
            Util.send_email(data)
        return Response({'success': 'We have sent you a link to reset your password'}, status=status.HTTP_200_OK)

class PasswordTokenCheckAPI(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer
    def get(self, request, uidb64, token):
        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'error':'Token is not valid, please request a new one'}, status = status.HTTP_401_UNAUTHORIZED)
            return Response({'success':True,'message':'Credentials Valid','uidb64': uidb64, 'token':token},status = status.HTTP_200_OK)

        except DjangoUnicodeDecodeError as identifier:
            if not PasswordResetTokenGenerator().check_token(user):
                return Response({'error':'Token is not valid, please request a new one'}, status = status.HTTP_401_UNAUTHORIZED)

class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success': True, 'message': 'Password reset success'}, status=status.HTTP_200_OK)

class LogoutAPIView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = (permissions.IsAuthenticated,)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success':'User successfully logged out'},status=status.HTTP_200_OK)

##############################################################################################################

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def EventRegisterAPIView(request):
    if request.method == 'POST':
        serializer = EventRegisterSerializer(data=request.data)
        registered = False
        event = Event.objects.get(pk = request.data['event'])
        user = request.user
        if serializer.is_valid():
            if user not in event.registered_users.all():
                serializer.save(user = user)
                return Response({'success':'true','message':'event registered successfully'}, status=status.HTTP_201_CREATED)
            return Response({'success':'false','message':'user already registered'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def FeedbackAPIView(request):
    if request.method == 'POST':
        serializer = FeedbackSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user = request.user)
            event = Event.objects.get(pk = request.data['event'])
            email_body = 'user: ' + request.user.username + '\n' + 'Feedback: ' + request.data['description']
            email_subject = event.name + ' Feedback by ' + request.user.username
            data = {'email_body': email_body, 'to_email': 'shubhngupta04@gmail.com',
                    'email_subject': email_subject}
            return Response({'success':'true','message':'Feedback saved successfully'}, status = status.HTTP_201_CREATED)
            Util.send_email(data)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

class SendUserEmails(FormView):
    template_name = 'eventsapi/send_email.html'
    form_class = SendEmailForm
    success_url = reverse_lazy('admin:eventsapi_user_changelist')

    def form_valid(self, form):
        users = form.cleaned_data['users']
        subject = form.cleaned_data['subject']
        message = form.cleaned_data['message']
        users_email = []
        for x in users:
            user = User.objects.get(username=x)
            users_email.append(user.email)
        data = {'email_body': message,
                'to_email': users_email,
                'email_subject': subject}
        print(data)
        Util.send_email(data)
        return super(SendUserEmails, self).form_valid(form)

######################################################################################################################



class GoogleSocialAuthView(GenericAPIView):
    serializer_class = GoogleSocialAuthSerializer
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = ((serializer.validated_data)['auth_token'])
        return Response(data, status=status.HTTP_200_OK)

def google_login(request):
    return render(request, 'eventsapi/google_login.html', {})
