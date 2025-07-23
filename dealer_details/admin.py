from django.contrib import admin
from django.utils.html import format_html
import admin_thumbnails

from dealer_details.models import PriceList, GetPincodes, add_category, documents
# Register your models here.
@admin_thumbnails.thumbnail('subcategory_image')
class PriceListAdmin(admin.ModelAdmin):
    def thumbnail(self, object):
        return format_html('<img src="{}" width="50"">'.format(object.subcategory_image.url))
    thumbnail.short_description = "SubImage"
    prepopulated_fields = {'slug': ('subcategory_name', 'price')}
    list_display= ('id', 'category_name', 'subcategory_name', 'slug', 'thumbnail', 'unit', 'percentage', 'dealer_id', 'pincode', 'price')
    list_display_links = ('id', 'subcategory_name', 'slug', 'category_name', 'thumbnail')
    ordering=()
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
    
@admin_thumbnails.thumbnail('category_image')
class add_categoryAdmin(admin.ModelAdmin):
    def thumbnail(self, object):
        return format_html('<img src="{}" width="50"">'.format(object.category_image.url))
    thumbnail.short_description = "Category_Image"
    list_display= ('id', 'dealer_id', 'category_name', 'thumbnail', 'status')
    list_display_links = ('id', 'dealer_id', 'category_name', 'thumbnail', 'status')
    ordering=()
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

@admin_thumbnails.thumbnail('Pic')
class documentsAdmin(admin.ModelAdmin):
    """  def thumbnail(self, object):
            return format_html('<img src="{}" width="50"">'.format(object.Pic.url))
    """
    def thumbnail(self, object):
        if object.Pic and hasattr(object.Pic, 'url'):
            return format_html('<img src="{}" width="50" />', object.Pic.url)
        return "No Image"

    thumbnail.short_description = "dealer_pic"
    list_display = ('id', 'dealer_id', 'Aadhar_card', 'thumbnail', 'status')
    list_display_links = ('id', 'dealer_id', 'Aadhar_card', 'thumbnail', 'status')
    ordering = ()
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


class GetPincodesAdmin(admin.ModelAdmin):
    list_display= ('id', 'dealer_id', 'addrequest', 'pincode1', 'pincode2', 'pincode3', 'pincode4', 'pincode5', 'pincode6', 'pincode7', 'pincode8', 'pincode9', 'pincode10')
    list_display_links = ('id', 'dealer_id', 'addrequest')
    ordering=()
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

admin.site.register(PriceList, PriceListAdmin)
admin.site.register(add_category, add_categoryAdmin)
admin.site.register(documents, documentsAdmin)
admin.site.register(GetPincodes, GetPincodesAdmin)

