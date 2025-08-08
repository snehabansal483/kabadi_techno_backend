from django.contrib import admin
from .models import Employee

from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
import admin_thumbnails
# Register your models here.
@admin_thumbnails.thumbnail('qrCode')
@admin_thumbnails.thumbnail('ProfilePic')
class EmployeeAdmin(UserAdmin):
    def qr_thumbnail(self, object):
        return format_html('<img src="{}" width="50"">'.format(object.qrCode.url))
    qr_thumbnail.short_description = "QR_Code_Image"
    def pp_thumbnail(self, object):
        return format_html('<img src="{}" width="50"">'.format(object.ProfilePic.url))
    pp_thumbnail.short_description = "Profile_Picture_Image"
    list_display=('id','auth_id','dealer_id', 'pp_thumbnail', 'username', 'kt_id','online', 'email', 'mobile_number' , 'qr_thumbnail','is_active', 'created_at', 'updated_at')
    list_display_links = ('id', 'pp_thumbnail', 'email', 'username')
    readonly_fields = ('email','auth_id','password','username', 'kt_id', 'qrCode', 'created_at', 'updated_at', 'last_login')
    ordering = ('-created_at',)
    filter_horizontal = ()
    list_filter = ()
    fieldsets = () 

admin.site.register(Employee, EmployeeAdmin)
