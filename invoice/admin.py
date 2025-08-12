from django.contrib import admin
from .models import DealerCommission

@admin.register(DealerCommission)
class DealerCommissionAdmin(admin.ModelAdmin):
    list_display = ('dealer', 'total_order_amount', 'commission_amount', 'status', 'calculation_date', 'payment_due_date')
    list_filter = ('status', 'dealer')
    search_fields = ('dealer__kt_id',)
    readonly_fields = ('order_numbers', 'total_order_amount', 'commission_amount', 'calculation_date', 'payment_due_date')
    actions = ['mark_as_paid']

    def mark_as_paid(self, request, queryset):
        queryset.update(status='Paid')
    mark_as_paid.short_description = "Mark selected commissions as Paid"
