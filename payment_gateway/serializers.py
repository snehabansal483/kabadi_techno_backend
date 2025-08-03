from rest_framework import serializers
from .models import SubscriptionPlan, DealerSubscription, SubscriptionHistory, SubscriptionNotification


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
            'id', 'dealer_ktid', 'subscription_plan', 'amount', 'payment_method',
            'payment_status', 'transaction_id', 'payment_date', 'notes'
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
