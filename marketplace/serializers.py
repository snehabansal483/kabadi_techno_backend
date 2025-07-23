from rest_framework import serializers
from .models import Marketplace

class CreateMarketplaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marketplace
        fields = ('dealer_id', 'end_duration')

class GetMarketplaceSerializer(serializers.ModelSerializer):
    # id = serializers.IntegerField(write_only=True)
    class Meta:
        model = Marketplace
        fields = '__all__'
