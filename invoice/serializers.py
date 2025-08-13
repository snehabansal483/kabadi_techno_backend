from rest_framework import serializers
from .models import DealerCommission, CommissionPaymentTransaction

class DealerCommissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DealerCommission
        fields = '__all__'

class CommissionPaymentTransactionSerializer(serializers.ModelSerializer):
    """Serializer for commission payment transactions"""
    class Meta:
        model = CommissionPaymentTransaction
        fields = ['id', 'commission', 'transaction_id', 'amount', 'payment_method', 'payment_screenshot', 'created_at']

class SubmitCommissionPaymentSerializer(serializers.ModelSerializer):
    """Serializer for users submitting commission payment details"""
    class Meta:
        model = CommissionPaymentTransaction
        fields = ['commission', 'transaction_id', 'amount', 'payment_method', 'payment_screenshot']

    def validate(self, data):
        commission = data.get('commission')
        amount = data.get('amount')

        # Validate that commission belongs to the authenticated user
        if hasattr(self.context['request'], 'user'):
            if commission.dealer.auth_id != self.context['request'].user:
                raise serializers.ValidationError("You can only submit payment for your own commission.")

        # Validate amount matches commission amount
        if commission.commission_amount != amount:
            raise serializers.ValidationError(
                f"Amount must be {commission.commission_amount} for this commission."
            )

        # Check if payment already exists for this commission
        if CommissionPaymentTransaction.objects.filter(commission=commission).exists():
            raise serializers.ValidationError("Payment details already submitted for this commission.")

        return data
