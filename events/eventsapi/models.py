from django.db import models
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)
from django.core.validators import MaxValueValidator, MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from ckeditor.fields import RichTextField

class UserAccountManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user

class UserAccount(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    objects = UserAccountManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def get_full_name(self):
        return self.first_name + ' ' + self.last_name

    def get_short_name(self):
        return self.first_name

    def __str__(self):
        return self.first_name + ' ' + self.last_name

class UserDetails(models.Model):
    pass

class Event(models.Model):
    name = models.CharField(max_length=255,unique=True)
    registered_users = models.ManyToManyField(UserAccount,through="Event_Registration")

    def __str__(self):
        return self.name

class EventDetails(models.Model):
    event = models.OneToOneField(Event, on_delete=models.CASCADE, related_name='event_description')
    event_date = models.DateField()
    description = RichTextField(blank=True,null=True)
    main_image = models.TextField()
    banner_image = models.TextField()

    def __str__(self):
        return self.event.name

class EventGallery(models.Model):
    event = models.ForeignKey(Event,on_delete=models.CASCADE,related_name="event_gallery")
    gallery_image = models.TextField()

    def __str__(self):
        return self.event.name

class Event_Registration(models.Model):
    event = models.ForeignKey(Event,related_name="event_registration",on_delete=models.CASCADE)
    user = models.ForeignKey(UserAccount,related_name="user_events",on_delete=models.CASCADE)

    class Meta:
        unique_together = ('event','user')

    def __str__(self):
        return self.user.first_name + ' Registered in ' + self.event.name

class Feedback(models.Model):
    event = models.ForeignKey(Event,related_name="event_feedback",on_delete=models.CASCADE)
    user = models.ForeignKey(UserAccount,related_name="user_event_feedback",on_delete=models.CASCADE)
    description = models.TextField()

    def __str__(self):
        return self.event.name + ' By ' +self.user.username
