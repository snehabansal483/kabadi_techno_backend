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

class DeleteMarketplaceSerializer(serializers.Serializer):
    """Serializer for delete marketplace response"""
    success = serializers.CharField()
    deleted_marketplace_id = serializers.CharField()
    dealer_name = serializers.CharField()
    deleted_by = serializers.CharField()
    deleted_at = serializers.DateTimeField()

class SoftDeleteMarketplaceSerializer(serializers.Serializer):
    """Serializer for soft delete (deactivate) marketplace response"""
    success = serializers.CharField()
    marketplace_id = serializers.CharField()
    dealer_name = serializers.CharField()
    previous_status = serializers.CharField()
    current_status = serializers.CharField()
    deactivated_by = serializers.CharField()
    deactivated_at = serializers.DateTimeField()
