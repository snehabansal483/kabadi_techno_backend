from django.contrib import admin
from .models import Contact

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'phone_number', 'profile_type', 'city')
    search_fields = ('name', 'email', 'city', 'profile_type')

