from django.contrib import admin
from .models import *

# Register your models here.
class DGKabadiTechnoAdmin(admin.ModelAdmin):
    list_display= ('id', 'email', 'kt_id', 'name', 'aadhar_number', 'account_type')
    list_display_links = ('id', 'email', 'kt_id', 'name', 'aadhar_number', 'account_type')
    ordering=()
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

class DGDetailsAdmin(admin.ModelAdmin):
    list_display= ('id', 'DGkt', 'kt_id', 'name', 'ip', 'document_hash_value')
    list_display_links = ('id', 'DGkt', 'kt_id', 'name', 'ip', 'document_hash_value')
    ordering=()
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

admin.site.register(DGKabadiTechno, DGKabadiTechnoAdmin)
admin.site.register(DGDetails, DGDetailsAdmin)
