from django.urls import path, include
from eventsapi import views
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

app_name = 'eventsapi'

urlpatterns = [
    path('register/',views.RegisterView.as_view(),name="register"),
    path('email-verify/', views.VerifyEmail.as_view(), name="email-verify"),
    path('login/',views.LoginAPIView.as_view(),name="login"),
    path('logout/', views.LogoutAPIView.as_view(), name="logout"),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('request-reset-email/', views.RequestPasswordResetEmail.as_view(),name="request-reset-email"),
    path('password-reset/<uidb64>/<token>/',views.PasswordTokenCheckAPI.as_view(), name='password-reset-confirm'),
    path('password-reset-complete', views.SetNewPasswordAPIView.as_view(),name='password-reset-complete'),

    path('event-register/',views.EventRegisterAPIView,name="event-register"),
    path('feedback/',views.FeedbackAPIView,name="feedback"),

    path('email-users',views.SendUserEmails.as_view(),name='email')
]
