from django.contrib import admin
from .models import *

#from leaflet.admin import LeafletGeoAdmin


@admin.register(CvmRegistration)
class CvmRegistration(admin.ModelAdmin):
    list_display = ('id', 'uid', 'imei_number', 'cvm_name', 'cvm_model',
        'state', 'city', 'area', 'pincode','registered_at')
    list_display_links = ('id', 'uid', 'imei_number', 'cvm_name', 'cvm_model',
        'state', 'city', 'area', 'pincode')


@admin.register(QRCode)
class QRCode(admin.ModelAdmin):
    list_display = ('id', 'user_type', 'user_id', 'user_email_id', 'cvm_id', 'qr_code', 'active', 'scaned')
    list_display_links = ('id', 'user_type', 'user_id', 'user_email_id', 'cvm_id', 'qr_code', 'active', 'scaned')

@admin.register(CvmDetails)
class CvmDetails(admin.ModelAdmin):
    list_display = ('id', 'qrcode', 'cvm_id', 'cvm_uid', 'weight', 'volume', 'date', 'time')
    list_display_links = ('id', 'qrcode', 'cvm_id', 'cvm_uid', 'weight', 'volume', 'date', 'time')

@admin.register(UnloadScrap)
class CvmUnloadScrapLogDetails(admin.ModelAdmin):
    list_display = ('id', 'cvm_id', 'dealer_id', 'active', 'status', 'date', 'time')
    list_display_links = ('id', 'cvm_id', 'dealer_id', 'active', 'status', 'date', 'time')

@admin.register(cart)
class Cvmcartadmin(admin.ModelAdmin):
    list_display = ('id',"cart_id","cvm_uid","customer_email","status","order_id","created_at","updated_at",)
    list_display_links = ('id',"cart_id","cvm_uid","customer_email","status","order_id","created_at","updated_at",)

@admin.register(order)
class Cvmorderadmin(admin.ModelAdmin):
    list_display = ('id',"order_id","cvm_uid","total_cart_no","dealer_email","status","created_at","updated_at",)
    list_display_links = ('id',"order_id","cvm_uid","total_cart_no","dealer_email","status","created_at","updated_at",)
