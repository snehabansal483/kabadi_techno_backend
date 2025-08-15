from django.db import models
from django.utils import timezone
from datetime import timedelta

# You may need to adjust the import path for Dealer if it's in another app
from accounts.models import DealerProfile  # Assuming Dealer model exists and has kt_id

class DealerCommission(models.Model):
    STATUS_CHOICES = [
        ("Paid", "Paid"),
        ("Unpaid", "Unpaid"),
    ]

    dealer = models.ForeignKey(DealerProfile, on_delete=models.CASCADE, related_name="commissions")
    order_numbers = models.JSONField()  # List of order_number strings
    total_order_amount = models.DecimalField(max_digits=12, decimal_places=2)
    commission_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Unpaid")
    calculation_date = models.DateField(default=timezone.now)
    payment_due_date = models.DateField()
    auto_generated_after_payment = models.BooleanField(default=False)  # Track if generated after payment
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Dealer Commission"
        verbose_name_plural = "Dealer Commissions"
        ordering = ['-calculation_date']
        unique_together = ['dealer', 'calculation_date']  # Prevent duplicate commissions for same dealer on same date

    def __str__(self):
        return f"Commission for {self.dealer.kt_id} on {self.calculation_date}"
    
    def save(self, *args, **kwargs):
        # Auto-set payment due date if not provided (last day of the calculation month)
        if not self.payment_due_date:
            from calendar import monthrange
            if isinstance(self.calculation_date, str):
                from datetime import datetime
                calc_date = datetime.strptime(self.calculation_date, '%Y-%m-%d').date()
            else:
                calc_date = self.calculation_date
            
            # Get last day of the calculation month
            last_day = monthrange(calc_date.year, calc_date.month)[1]
            self.payment_due_date = calc_date.replace(day=last_day)
        super().save(*args, **kwargs)
    
    @property
    def is_overdue(self):
        """Check if the commission payment is overdue"""
        return self.status == 'Unpaid' and self.payment_due_date < timezone.now().date()
    
    @property
    def days_until_due(self):
        """Get number of days until payment is due (negative if overdue)"""
        return (self.payment_due_date - timezone.now().date()).days
    
    @property
    def order_count(self):
        """Get count of orders in this commission"""
        return len(self.order_numbers) if self.order_numbers else 0

class CommissionPaymentTransaction(models.Model):
    """Model for storing commission payment transactions"""
    commission = models.ForeignKey(DealerCommission, on_delete=models.CASCADE, related_name="payment_transactions")
    transaction_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    payment_screenshot = models.ImageField(upload_to="commission_payments/screenshots/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)  # Field to track verification status
    notes = models.TextField(null=True, blank=True)  # Field to store additional notes

    def __str__(self):
        return f"Transaction {self.transaction_id} for Commission {self.commission.id}"
