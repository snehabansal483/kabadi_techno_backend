from django.contrib import admin

from .models import Marketplace

# Register your models here.

class MarketplaceAdmin(admin.ModelAdmin):
    list_display= ('id', 'dealer_id', 'url', 'qr_code_status', 'duration_active', 'status', 'created_at', 'updated_at')
    list_display_links = ('id', 'dealer_id', 'url', 'duration_active')
    ordering=()
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
    
    def qr_code_status(self, obj):
        """Display QR code status safely"""
        if obj.qrCode:
            try:
                return f"Available: {obj.qrCode.name}"
            except:
                return "Error loading QR code"
        return "No QR code"
    qr_code_status.short_description = 'QR Code'

admin.site.register(Marketplace, MarketplaceAdmin)
