from django.contrib import admin

# Register your models here.
from .models import *

class dealer_initiativesAdmin(admin.ModelAdmin):
    list_display = ("id","dealer_id","dealer_account_type","deale_name","photo","message","views","likes","comments")

class schedule_pickupAdmin(admin.ModelAdmin):
    list_display = ("id","dealer_id","dealer_account_type","deale_name","name","phone_number","email","pincode","state_n_country","address","select_date","select_time")

class reach_usAdmin(admin.ModelAdmin):
    list_display = ("id","dealer_id","dealer_account_type","deale_name","name","phone_number","email","subject","message")

class dealer_ratingAdmin(admin.ModelAdmin):
    list_display = ("id","dealer_id","dealer_account_type","deale_name","rating","rate_count")

admin.site.register(dealer_initiatives, dealer_initiativesAdmin)
admin.site.register(schedule_pickup, schedule_pickupAdmin)
admin.site.register(reach_us, reach_usAdmin)
admin.site.register(dealer_rating, dealer_ratingAdmin)
