from rest_framework import serializers
from .models import DigiPinAddress

class DigiPinAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = DigiPinAddress
        fields = '__all__'
        read_only_fields = ['digipin', 'digipin_url']  # Assuming these fields are set automatically