from django.contrib import admin
from .models import (   UserAccount,Event,
                        Feedback,Event_Registration,
                        EventDetails,EventGallery)
from django.utils.html import format_html
import csv
from django.http import HttpResponse
from django import forms
from django.shortcuts import render
from django.contrib.auth import get_user_model

User = get_user_model()

class ExportCsvMixin:
    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)
        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])
        return response
    export_as_csv.short_description = "Export Selected"

user_list = User.objects.all()
choices_list = [(x.id,x.email) for x in user_list]
choices_tuple = tuple(choices_list)

# choices_tuple = ('Akshat Gupta','akshatguptawelcome@gmail.com')

class SendEmailForm(forms.Form):
    subject = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Subject'}))
    message = forms.CharField(widget=forms.Textarea)
    users = forms.MultipleChoiceField(label="To",
                                           choices=choices_tuple,
                                           widget=forms.CheckboxSelectMultiple)

class SendEmailMixin:
    def send_email(self, request, queryset):
        form = SendEmailForm(initial={  'users': [x.user.id for x in queryset],
                                        'subject': 'Please type your Subject',
                                        'message': 'Please type your message'})
        return render(request, 'eventsapi/send_email.html', {'form': form})
    send_email.short_description = "Send Email To Selected"
    def send_email_to_user(self, request, queryset):
        form = SendEmailForm(initial={  'users': [x.id for x in queryset],
                                        'subject': 'Please type your Subject',
                                        'message': 'Please type your message'})
        return render(request, 'eventsapi/send_email.html', {'form': form})
    send_email_to_user.short_description = "Send Email To Selected"

@admin.register(UserAccount)
class UserAdmin(admin.ModelAdmin,ExportCsvMixin,SendEmailMixin):
    list_display = ['first_name','last_name','email','id']
    actions = ["export_as_csv","send_email_to_user"]

@admin.register(Event_Registration)
class Event_RegistrationAdmin(admin.ModelAdmin,ExportCsvMixin,SendEmailMixin):
    list_display = ['user','event']
    list_filter = ['event']
    search_fields = ['user__first_name','user__last_name','user__get_full_name']
    actions = ["export_as_csv","send_email"]

@admin.register(Event)
class EventAdmin(admin.ModelAdmin,ExportCsvMixin):
    list_display = ['name','id']

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin,ExportCsvMixin):
    list_display = ['event','user','description']
    actions = ["export_as_csv"]

@admin.register(EventGallery)
class EventGalleryAdmin(admin.ModelAdmin):
    list_display = ['event','get_image']
    list_filter = ['event']
    search_fields = ['event__name']

    def get_image(self, obj):
        html = "<img src='" + str(obj.gallery_image) + "' style='height:200px;width:300px' />";
        return format_html(html)
    get_image.short_description = 'Gallery'

@admin.register(EventDetails)
class EventDetailsAdmin(admin.ModelAdmin):
    list_display = ['event','event_date','get_image']
    list_filter = ['event']
    search_fields = ['event__name']

    def get_image(self, obj):
        html = "<img src='" + str(obj.main_image) + "' style='height:200px;width:300px' />";
        return format_html(html)
    get_image.short_description = 'Gallery'
