from rest_framework import serializers
from .models import SubscriptionPlan, DealerSubscription, SubscriptionHistory, SubscriptionNotification, PaymentTransaction, BankDetails


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ['id', 'plan_type', 'name', 'duration_days', 'price', 'description']


class DealerSubscriptionSerializer(serializers.ModelSerializer):
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    plan_type = serializers.CharField(source='plan.plan_type', read_only=True)
    dealer_ktid = serializers.CharField(source='dealer.kt_id', read_only=True)
    days_remaining = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    is_expiring_soon = serializers.ReadOnlyField()
    
    class Meta:
        model = DealerSubscription
        fields = [
            'id', 'dealer_ktid', 'plan_name', 'plan_type', 'start_date', 
            'end_date', 'status', 'is_trial', 'days_remaining', 'is_active',
            'is_expiring_soon', 'auto_renew', 'created_at'
        ]


class SubscriptionHistorySerializer(serializers.ModelSerializer):
    dealer_ktid = serializers.CharField(source='dealer.kt_id', read_only=True)
    subscription_plan = serializers.CharField(source='subscription.plan.name', read_only=True)
    
    class Meta:
        model = SubscriptionHistory
        fields = [
            'id',
            'dealer_ktid',              # Read-only: shown in response
            'subscription',             # Required for POST request
            'subscription_plan',        # Read-only: shown in response
            'amount',
            'payment_method',
            'payment_status',
            'transaction_id',
            'payment_date',
            'notes'
        ]
        read_only_fields = ['dealer_ktid', 'subscription_plan', 'payment_date']


class PaymentTransactionSerializer(serializers.ModelSerializer):
    dealer_ktid = serializers.CharField(source='subscription.dealer.kt_id', read_only=True)
    subscription_plan = serializers.CharField(source='subscription.plan.name', read_only=True)
    
    class Meta:
        model = PaymentTransaction
        fields = [
            'id', 'subscription', 'dealer_ktid', 'subscription_plan', 
            'transaction_id', 'amount', 'payment_method', 'payment_screenshot',
            'verified', 'verified_by', 'verified_at', 'notes', 'created_at'
        ]
        read_only_fields = ['verified', 'verified_by', 'verified_at', 'notes']


class SubmitPaymentSerializer(serializers.ModelSerializer):
    """Serializer for users submitting payment details"""
    class Meta:
        model = PaymentTransaction
        fields = ['subscription', 'transaction_id', 'amount', 'payment_method', 'payment_screenshot']
    
    def validate(self, data):
        subscription = data.get('subscription')
        amount = data.get('amount')
        
        # Validate that subscription belongs to the authenticated user
        if hasattr(self.context['request'], 'user'):
            if subscription.dealer.auth_id != self.context['request'].user:
                raise serializers.ValidationError("You can only submit payment for your own subscription.")
        
        # Validate amount matches subscription plan price
        if subscription.plan.price != amount:
            raise serializers.ValidationError(
                f"Amount must be {subscription.plan.price} for this subscription plan."
            )
        
        # Check if payment already exists for this subscription
        if PaymentTransaction.objects.filter(subscription=subscription).exists():
            raise serializers.ValidationError("Payment details already submitted for this subscription.")
        
        return data

class BankDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankDetails
        fields = [
            'account_name',
            'account_number',
            'ifsc_code',
            'bank_name',
            'branch_name',
            'plan_2',
            'plan_3',
            'plan_4'
        ]




class SubscriptionNotificationSerializer(serializers.ModelSerializer):
    dealer_ktid = serializers.CharField(source='dealer.kt_id', read_only=True)
    subscription_plan = serializers.CharField(source='subscription.plan.name', read_only=True)
    
    class Meta:
        model = SubscriptionNotification
        fields = [
            'id', 'dealer_ktid', 'subscription_plan', 'notification_type',
            'message', 'is_sent', 'sent_at', 'created_at'
        ]
