from django.contrib import admin
from .models import User,Event,Feedback,Event_Registration
from django.utils.html import format_html
import csv
from django.http import HttpResponse
from django import forms
from django.shortcuts import render

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
choices_list = [(x.username,x.email) for x in user_list]
choices_tuple = tuple(choices_list)

class SendEmailForm(forms.Form):
    subject = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Subject'}))
    message = forms.CharField(widget=forms.Textarea)
    users = forms.MultipleChoiceField(label="To",
                                           choices=choices_tuple,
                                           widget=forms.CheckboxSelectMultiple)

class SendEmailMixin:
    def send_email(self, request, queryset):
        form = SendEmailForm(initial={  'users': [x.user.username for x in queryset],
                                        'subject': 'Please type your Subject',
                                        'message': 'Please type your message'})
        return render(request, 'eventsapi/send_email.html', {'form': form})
    send_email.short_description = "Send Email To Selected"

@admin.register(User)
class UserAdmin(admin.ModelAdmin,ExportCsvMixin):
    list_display = ['username','email','phone_number','id']
    actions = ["export_as_csv"]

@admin.register(Event_Registration)
class Event_RegistrationAdmin(admin.ModelAdmin,ExportCsvMixin,SendEmailMixin):
    list_display = ['user','event']
    list_filter = ['event']
    search_fields = ['user__username']
    actions = ["export_as_csv","send_email"]
# Register your models here.

@admin.register(Event)
class EventAdmin(admin.ModelAdmin,ExportCsvMixin):
    list_display = ['name','id']

admin.site.register(Feedback)
