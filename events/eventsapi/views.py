from rest_framework import viewsets,generics,status,views,permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import UserAccount,Event,Event_Registration
from .serializers import (EventRegisterSerializer, FeedbackSerializer)
import jwt
from django.conf import settings
from .utils import Util
from .admin import SendEmailForm
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model

User = get_user_model()

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
            email_body = 'User: ' + request.user.get_full_name + '\n' + 'Feedback: ' + request.data['description']
            email_subject = event.name + ' Feedback by ' + request.user.get_full_name
            data = {'email_body': email_body, 'to_email': 'shubhngupta04@gmail.com',
                    'email_subject': email_subject}
            return Response({'success':'true','message':'Feedback saved successfully'}, status = status.HTTP_201_CREATED)
            Util.send_email(data)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

class SendUserEmails(FormView):
    template_name = 'eventsapi/send_email.html'
    form_class = SendEmailForm
    success_url = reverse_lazy('admin:eventsapi_useraccount_changelist')

    def form_valid(self, form):
        users = form.cleaned_data['users']
        subject = form.cleaned_data['subject']
        message = form.cleaned_data['message']
        users_email = []
        for x in users:
            user = User.objects.get(id=x)
            users_email.append(user.email)
        data = {'email_body': message,
                'to_email': users_email,
                'email_subject': subject}
        print(data)
        Util.send_email(data)
        return super(SendUserEmails, self).form_valid(form)
