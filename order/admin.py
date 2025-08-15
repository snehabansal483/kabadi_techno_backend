from django.contrib import admin

from order.models import Order, OrderProduct

# Register your models here.
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_id', 'order_number', 'first_name', 'last_name', 'phone', 'email', 'ip', 'created_at')
    list_display_links = ('id', 'customer_id', 'order_number', 'first_name', 'last_name')
    list_editable = ('created_at',)  # Now editable in list view
    ordering = ()
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


class OrderProductAdmin(admin.ModelAdmin):
    list_display= ('id', 'customer_id', 'order', 'order_number', 'cart_item', 'percentage', 'subcategory_image', 'quantity', 'unit', 'price')
    list_display_links = ('id', 'customer_id', 'order', 'order_number', 'cart_item', 'percentage', 'subcategory_image')
    ordering=()
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct, OrderProductAdmin)

