from django.contrib import admin
from .models import User,Event,Feedback,Event_Registration
from django.utils.html import format_html
import csv
from django.http import HttpResponse

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


@admin.register(User)
class UserAdmin(admin.ModelAdmin,ExportCsvMixin):
    list_display = ['username','email','phone_number']
    actions = ["export_as_csv"]

@admin.register(Event_Registration)
class Event_RegistrationAdmin(admin.ModelAdmin,ExportCsvMixin):
    list_display = ['user','event']
    list_filter = ['event']
    search_fields = ['user__username']
    actions = ["export_as_csv"]
# Register your models here.

@admin.register(Event)
class EventAdmin(admin.ModelAdmin,ExportCsvMixin):
    list_display = ['name','id']

admin.site.register(Feedback)
