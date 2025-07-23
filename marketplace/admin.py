from django.contrib import admin

from .models import Marketplace

# Register your models here.

class MarketplaceAdmin(admin.ModelAdmin):
    list_display= ('id', 'dealer_id', 'url', 'qrCode', 'duration_active', 'status', 'created_at', 'updated_at')
    list_display_links = ('id', 'dealer_id', 'url', 'qrCode', 'duration_active')
    ordering=()
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

admin.site.register(Marketplace, MarketplaceAdmin)
