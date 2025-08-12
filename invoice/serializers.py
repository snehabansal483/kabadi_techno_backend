from rest_framework import serializers
from .models import DealerCommission

class DealerCommissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DealerCommission
        fields = '__all__'
