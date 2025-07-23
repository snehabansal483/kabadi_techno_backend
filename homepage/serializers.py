from rest_framework import serializers
from .models import Contact, Donation, WasteDonation

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['name', 'phone_number', 'email', 'message', 'profile_type']

class TakeAllContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        exclude = ['profile_type']

class DonationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donation
        fields = '__all__'

class WasteDonationSerializer(serializers.ModelSerializer):
    class Meta:
        model = WasteDonation
        fields = '__all__'
