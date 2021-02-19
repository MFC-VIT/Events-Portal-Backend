from django.urls import path, include
from eventsapi import views
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

app_name = 'eventsapi'

urlpatterns = [
    path('event-register/',views.EventRegisterAPIView,name="event-register"),
    path('feedback/',views.FeedbackAPIView,name="feedback"),
    path('email-users',views.SendUserEmails.as_view(),name='email')
]
