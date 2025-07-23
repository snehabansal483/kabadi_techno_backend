from django.contrib import admin
from .models import Cart, CartItem
from django.utils.html import format_html
import admin_thumbnails

class CartAdmin(admin.ModelAdmin):
    list_display=('cart_id', 'date_added')

@admin_thumbnails.thumbnail('subcategory_image')
class CartItemAdmin(admin.ModelAdmin):
    def thumbnail(self, object):
        return format_html('<img src="{}" width="50"">'.format(object.subcategory_image.url))
    thumbnail.short_description = "SubImage"
    list_display= ('id', 'subcategory_name', 'thumbnail', 'customer', 'dealer_id', 'price_list', 'percentage', 'unit', 'quantity', 'price', 'is_active')
    list_display_links = ('id', 'subcategory_name', 'customer', 'dealer_id', 'thumbnail')
    ordering=()
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

# Register your models here.
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
