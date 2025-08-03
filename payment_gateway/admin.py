from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import SubscriptionPlan, DealerSubscription, SubscriptionHistory, SubscriptionNotification

# Register your models here.

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'plan_type', 'duration_days', 'price', 'is_active', 'created_at']
    list_filter = ['plan_type', 'is_active', 'created_at']
    search_fields = ['name', 'plan_type']
    list_editable = ['price', 'is_active']
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
        if days > 7:
            color = 'green'
        elif days > 0:
            color = 'orange'
        else:
            color = 'red'
        return format_html(f'<span style="color: {color};">{days} days</span>')
    days_remaining_display.short_description = 'Days Remaining'
    
    def payment_status(self, obj):
        history = SubscriptionHistory.objects.filter(dealer=obj.dealer).order_by('-payment_date')
        if history.exists():
            latest_payment = history.first()
            return latest_payment.payment_status
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


@admin.register(SubscriptionHistory)
class SubscriptionHistoryAdmin(admin.ModelAdmin):
    list_display = ['dealer_ktid', 'amount', 'payment_status', 'payment_method', 
                   'transaction_id', 'payment_date']
    list_filter = ['payment_status', 'payment_method', 'payment_date']
    search_fields = ['dealer__kt_id', 'transaction_id', 'dealer__auth_id__email']
    readonly_fields = ['payment_date']
    date_hierarchy = 'payment_date'
    
    def dealer_ktid(self, obj):
        return obj.dealer.kt_id
    dealer_ktid.short_description = 'KT ID'


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
        from django.utils import timezone
        updated = queryset.update(is_sent=True, sent_at=timezone.now())
        self.message_user(request, f'{updated} notifications marked as sent.')
    mark_as_sent.short_description = 'Mark selected notifications as sent'
