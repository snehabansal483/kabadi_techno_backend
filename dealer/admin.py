from django.contrib import admin
# from leaflet.admin import LeafletGeoAdmin #map
from import_export.admin import ImportExportModelAdmin
from .resources import dealersAdminResource
from .models import *
from django.utils.html import format_html
import admin_thumbnails

@admin.register(dealer)
class dealerAdmin(ImportExportModelAdmin):
    list_display = ["id","name","mobile","dealing","min_qty","max_qty","pincode","timing","live_location"]
    resource_class=dealersAdminResource

# @admin.register(dealer) # leafletgeo means loading maps admin 
# class dealerAdmin(LeafletGeoAdmin,ImportExportModelAdmin):
#     list_display = ["id","name","mobile","old","new","other","min_qty","max_qty","pincode"]
#     resource_class=dealersAdminResource

@admin_thumbnails.thumbnail('itemPic')
class RequestInquiryAdmin(admin.ModelAdmin):
    def thumbnail(self, object):
        return format_html('<img src="{}" width="50"">'.format(object.itemPic.url))
    thumbnail.short_description = "ItemPic"
    list_display= ('id', 'dealer_id', 'customer_name', 'email', 'itemName', 'thumbnail', 'quantity')
    list_display_links = ('id', 'dealer_id', 'customer_name', 'email', 'itemName', 'thumbnail')
    ordering=()
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

admin.site.register(RequestInquiry, RequestInquiryAdmin)

#check    
