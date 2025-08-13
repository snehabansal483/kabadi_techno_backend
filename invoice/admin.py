from django.contrib import admin
from .models import DealerCommission

@admin.register(DealerCommission)
class DealerCommissionAdmin(admin.ModelAdmin):
    list_display = ('dealer', 'total_order_amount', 'commission_amount', 'status', 'calculation_date', 'payment_due_date', 'auto_generated_after_payment')
    list_filter = ('status', 'auto_generated_after_payment', 'dealer')
    search_fields = ('dealer__kt_id',)
    readonly_fields = ('order_numbers', 'total_order_amount')
    actions = ['mark_as_paid']

    def mark_as_paid(self, request, queryset):
        """
        Admin action to mark commissions as paid and auto-generate next month commission
        """
        from invoice.views import DealerCommissionViewSet
        
        updated_count = 0
        next_generated_count = 0
        
        for commission in queryset:
            if commission.status == 'Unpaid':
                # Check if payment is within 30 days
                payment_within_30_days = commission.days_until_due >= 0
                
                # Mark as paid
                commission.status = 'Paid'
                commission.save()
                updated_count += 1
                
                # Try to generate next month commission if paid within 30 days
                if payment_within_30_days:
                    viewset = DealerCommissionViewSet()
                    next_commission = viewset._generate_next_month_commission(commission.dealer)
                    if next_commission:
                        next_generated_count += 1
        
        if next_generated_count > 0:
            self.message_user(
                request, 
                f'{updated_count} commission(s) marked as paid. {next_generated_count} next month commission(s) auto-generated.'
            )
        else:
            self.message_user(request, f'{updated_count} commission(s) marked as paid.')
            
    mark_as_paid.short_description = "Mark selected commissions as Paid and auto-generate next month commissions"
