from django.contrib import messages
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

admin.site.register(PriceList, PriceListAdmin)    
    
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


@admin.action(description='Approve Addrequest and Add Pincode(s)')
def approve_addrequest(modeladmin, request, queryset):
    for obj in queryset:
        if obj.addrequest:
            # Split addrequest into multiple pincodes (in case of multiple)
            new_pins = obj.addrequest.split(',')
            new_pins = [pin.strip() for pin in new_pins if pin.strip().isdigit()]

            # Get current pincode values
            pincode_fields = ['pincode1', 'pincode2', 'pincode3', 'pincode4', 'pincode5', 
                              'pincode6', 'pincode7', 'pincode8', 'pincode9', 'pincode10', 'pincode11']
            current_pins = [getattr(obj, field) for field in pincode_fields]
            
            # Fill in empty slots
            index = 0
            for i in range(len(current_pins)):
                if current_pins[i] in [None, ''] and index < len(new_pins):
                    setattr(obj, pincode_fields[i], new_pins[index])
                    index += 1

            if index > 0:
                messages.success(request, f"{obj.dealer_id}: {index} new pincode(s) added successfully.")
            else:
                messages.warning(request, f"{obj.dealer_id}: No available slots for new pincodes.")

            # Clear the addrequest field after processing
            obj.addrequest = None

            # Update the count
            obj.no_of_pincodes = sum(1 for field in pincode_fields if getattr(obj, field))
            obj.save()
        else:
            messages.warning(request, f"{obj.dealer_id}: No addrequest to process.")

class GetPincodesAdmin(admin.ModelAdmin):
    list_display = ('id', 'dealer_id', 'addrequest', 'pincode1', 'pincode2', 'pincode3', 'pincode4', 'pincode5', 
                    'pincode6', 'pincode7', 'pincode8', 'pincode9', 'pincode10', 'pincode11')
    list_display_links = ('id', 'dealer_id', 'addrequest')
    actions = [approve_addrequest]

admin.site.register(GetPincodes, GetPincodesAdmin)


