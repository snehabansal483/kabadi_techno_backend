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


@admin.action(description='Approve addrequest and update pincodes')
def approve_addrequest(modeladmin, request, queryset):
    for obj in queryset:
        if obj.addrequest:
            # Parse the addrequest — assuming it's a comma-separated list of pincodes
            new_pincodes = obj.addrequest.split(",")
            new_pincodes = [p.strip() for p in new_pincodes if p.strip().isdigit()]

            # Assign up to 10 pincodes
            for i in range(min(10, len(new_pincodes))):
                setattr(obj, f'pincode{i+1}', new_pincodes[i])

            obj.addrequest = None  # Clear the request after processing
            obj.save()

class GetPincodesAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'dealer_id', 'addrequest',
        'pincode1', 'pincode2', 'pincode3', 'pincode4', 'pincode5',
        'pincode6', 'pincode7', 'pincode8', 'pincode9', 'pincode10'
    )
    list_display_links = ('id', 'dealer_id', 'addrequest')
    actions = [approve_addrequest]

# Register admin
admin.site.register(GetPincodes, GetPincodesAdmin)


