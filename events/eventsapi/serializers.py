from rest_framework import serializers
from .models import UserAccount,Event_Registration, Feedback

from djoser.serializers import UserCreateSerializer
from django.contrib.auth import get_user_model
User = get_user_model()

class UserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'password')

class EventRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event_Registration
        fields = ['event']

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['event','description']
