from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import SubscriptionPlan, DealerSubscription, SubscriptionNotification, PaymentTransaction, BankDetails

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'plan_type', 'duration_days', 'amount', 'is_active', 'created_at']
    list_filter = ['plan_type', 'is_active', 'created_at']
    search_fields = ['name', 'plan_type']
    list_editable = ['amount', 'is_active']
    ordering = ['plan_type']


@admin.register(DealerSubscription)
class DealerSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['dealer_ktid', 'plan_name', 'status', 'start_date', 'end_date', 
                   'days_remaining_display', 'is_trial', 'payment_status']
    list_filter = ['status', 'is_trial', 'plan__plan_type', 'start_date', 'end_date']
    search_fields = ['dealer__kt_id', 'dealer__auth_id__email', 'dealer__auth_id__full_name']
    readonly_fields = ['created_at', 'updated_at', 'days_remaining_display']
    date_hierarchy = 'start_date'
    actions = ['expire_subscriptions', 'activate_subscriptions']
    
    def dealer_ktid(self, obj):
        return obj.dealer.kt_id
    dealer_ktid.short_description = 'KT ID'
    
    def plan_name(self, obj):
        return obj.plan.name
    plan_name.short_description = 'Plan'
    
    def days_remaining_display(self, obj):
        days = obj.days_remaining
        color = 'green' if days > 7 else 'orange' if days > 0 else 'red'
        return format_html(f'<span style="color: {color};">{days} days</span>')
    days_remaining_display.short_description = 'Days Remaining'
    
    def payment_status(self, obj):
        transaction = obj.payment_transactions.order_by('-created_at').first()
        if transaction:
            return transaction.payment_status
        return 'No Payment'
    payment_status.short_description = 'Payment Status'
    
    def expire_subscriptions(self, request, queryset):
        updated = queryset.update(status='expired')
        self.message_user(request, f'{updated} subscriptions marked as expired.')
    expire_subscriptions.short_description = 'Mark selected subscriptions as expired'
    
    def activate_subscriptions(self, request, queryset):
        updated = queryset.update(status='active')
        self.message_user(request, f'{updated} subscriptions marked as active.')
    activate_subscriptions.short_description = 'Mark selected subscriptions as active'


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ['dealer_ktid', 'subscription_plan', 'transaction_id', 'amount', 
                   'payment_method', 'verified', 'payment_status', 'verified_by', 'created_at']
    list_filter = ['payment_method', 'verified', 'payment_status', 'created_at']
    search_fields = ['subscription__dealer__kt_id', 'transaction_id', 'verified_by']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    actions = ['verify_payments', 'unverify_payments']
    
    def dealer_ktid(self, obj):
        return obj.subscription.dealer.kt_id
    dealer_ktid.short_description = 'KT ID'
    
    def subscription_plan(self, obj):
        return obj.subscription.plan.name
    subscription_plan.short_description = 'Plan'
    
    def verify_payments(self, request, queryset):
        updated = 0
        for payment in queryset.filter(verified=False):
            payment.verified = True
            payment.verified_by = request.user.username
            payment.verified_at = timezone.now()
            payment.save()

            # Activate subscription
            subscription = payment.subscription
            subscription.status = 'active'
            subscription.start_date = timezone.now()
            subscription.end_date = subscription.start_date + timezone.timedelta(days=subscription.plan.duration_days)
            subscription.save()
            updated += 1

        self.message_user(request, f'{updated} payments verified and subscriptions activated.')
    verify_payments.short_description = 'Verify selected payments and activate subscriptions'
    
    def unverify_payments(self, request, queryset):
        updated = queryset.filter(verified=True).update(
            verified=False, 
            verified_by=None, 
            verified_at=None
        )
        self.message_user(request, f'{updated} payments marked as unverified.')
    unverify_payments.short_description = 'Mark selected payments as unverified'


@admin.register(BankDetails)
class BankDetailsAdmin(admin.ModelAdmin):
    list_display = ['account_name', 'bank_name', 'is_active']
    fields = [
        'account_name', 'account_number', 'ifsc_code',
        'bank_name', 'branch_name', 'plan_2', 'plan_3', 'plan_4',
        'is_active'
    ]


@admin.register(SubscriptionNotification)
class SubscriptionNotificationAdmin(admin.ModelAdmin):
    list_display = ['dealer_ktid', 'notification_type', 'is_sent', 'sent_at', 'created_at']
    list_filter = ['notification_type', 'is_sent', 'created_at']
    search_fields = ['dealer__kt_id', 'dealer__auth_id__email']
    readonly_fields = ['created_at', 'sent_at']
    actions = ['mark_as_sent']
    
    def dealer_ktid(self, obj):
        return obj.dealer.kt_id
    dealer_ktid.short_description = 'KT ID'
    
    def mark_as_sent(self, request, queryset):
        updated = queryset.update(is_sent=True, sent_at=timezone.now())
        self.message_user(request, f'{updated} notifications marked as sent.')
    mark_as_sent.short_description = 'Mark selected notifications as sent'
