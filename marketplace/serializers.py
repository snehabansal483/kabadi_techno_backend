from rest_framework import serializers
from .models import Marketplace

class CreateMarketplaceSerializer(serializers.ModelSerializer):
    dealer_ktid = serializers.CharField(max_length=20, write_only=True)
    
    class Meta:
        model = Marketplace
        fields = ('dealer_ktid',)

class GetMarketplaceSerializer(serializers.ModelSerializer):
    # id = serializers.IntegerField(write_only=True)
    class Meta:
        model = Marketplace
        fields = '__all__'
