from django.contrib import admin
from .models import User
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
# Register your models here.
