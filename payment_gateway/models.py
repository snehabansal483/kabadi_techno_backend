from django.db import models
from django.utils import timezone
from datetime import timedelta
from accounts.models import DealerProfile

# Create your models here.

class SubscriptionPlan(models.Model):
    """Model to define different subscription plans"""
    PLAN_CHOICES = [
        ('trial', '1 Month Free Trial'),
        ('3_month', '3 Month Plan'),
        ('6_month', '6 Month Plan'),
        ('1_year', '1 Year Plan'),
    ]
    
    plan_type = models.CharField(max_length=20, choices=PLAN_CHOICES, unique=True)
    name = models.CharField(max_length=100)
    duration_days = models.IntegerField(help_text="Duration in days")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.duration_days} days"
    
    class Meta:
        verbose_name = "Subscription Plan"
        verbose_name_plural = "Subscription Plans"


class DealerSubscription(models.Model):
    """Model to track individual dealer subscriptions"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
        ('pending', 'Pending Payment'),
    ]
    
    dealer = models.ForeignKey(DealerProfile, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_trial = models.BooleanField(default=False)
    payment_reference = models.CharField(max_length=100, blank=True, null=True)
    auto_renew = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        """Auto-calculate end_date based on plan duration"""
        if not self.end_date:
            self.end_date = self.start_date + timedelta(days=self.plan.duration_days)
        super().save(*args, **kwargs)
    
    @property
    def is_active(self):
        """Check if subscription is currently active"""
        return (self.status == 'active' and 
                self.start_date <= timezone.now() <= self.end_date)
    
    @property
    def days_remaining(self):
        """Get days remaining in subscription"""
        if self.end_date > timezone.now():
            return (self.end_date - timezone.now()).days
        return 0
    
    @property
    def is_expiring_soon(self):
        """Check if subscription expires within 7 days"""
        return self.days_remaining <= 7 and self.days_remaining > 0
    
    def expire_subscription(self):
        """Mark subscription as expired"""
        self.status = 'expired'
        self.save()
    
    def __str__(self):
        return f"{self.dealer.kt_id} - {self.plan.name} ({self.status})"
    
    class Meta:
        verbose_name = "Dealer Subscription"
        verbose_name_plural = "Dealer Subscriptions"
        ordering = ['-created_at']


class SubscriptionHistory(models.Model):
    """Model to track subscription payment history"""
    dealer = models.ForeignKey(DealerProfile, on_delete=models.CASCADE, related_name='subscription_history')
    subscription = models.ForeignKey(DealerSubscription, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    payment_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ], default='pending')
    transaction_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.dealer.kt_id} - {self.amount} ({self.payment_status})"
    
    class Meta:
        verbose_name = "Subscription Payment"
        verbose_name_plural = "Subscription Payments"
        ordering = ['-payment_date']


class PaymentTransaction(models.Model):
    """Model to store payment details submitted by users"""
    PAYMENT_METHOD_CHOICES = [
        ('neft', 'NEFT Transfer'),
        ('qr_code', 'QR Code Payment'),
    ]
    
    subscription = models.ForeignKey(DealerSubscription, on_delete=models.CASCADE, related_name='payment_transactions')
    transaction_id = models.CharField(max_length=100, help_text="Transaction ID provided by user")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_screenshot = models.ImageField(upload_to='payment_screenshots/', blank=True, null=True)
    verified = models.BooleanField(default=False)
    verified_by = models.CharField(max_length=100, blank=True, null=True, help_text="Admin who verified the payment")
    verified_at = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True, help_text="Admin notes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.subscription.dealer.kt_id} - {self.transaction_id} - {'Verified' if self.verified else 'Pending'}"
    
    class Meta:
        verbose_name = "Payment Transaction"
        verbose_name_plural = "Payment Transactions"
        ordering = ['-created_at']


class BankDetails(models.Model):
    """Model to store company bank account details for NEFT transfers and UPI"""
    account_name = models.CharField(max_length=200)
    account_number = models.CharField(max_length=50)
    ifsc_code = models.CharField(max_length=20)
    bank_name = models.CharField(max_length=200)
    branch_name = models.CharField(max_length=200, blank=True, null=True)

    # QR code URLs for different plans
    plan_2 = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="QR code URL or text for 3-month plan"
    )
    plan_3 = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="QR code URL or text for 6-month plan"
    )
    plan_4 = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="QR code URL or text for 1-year plan"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.account_name} - {self.account_number}"

    class Meta:
        verbose_name = "Bank Details"
        verbose_name_plural = "Bank Details"

class SubscriptionNotification(models.Model):
    """Model to track subscription expiry notifications"""
    NOTIFICATION_TYPES = [
        ('expiry_warning', 'Expiry Warning'),
        ('expired', 'Subscription Expired'),
        ('renewal_reminder', 'Renewal Reminder'),
    ]
    
    dealer = models.ForeignKey(DealerProfile, on_delete=models.CASCADE, related_name='notifications')
    subscription = models.ForeignKey(DealerSubscription, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.dealer.kt_id} - {self.notification_type}"
    
    class Meta:
        verbose_name = "Subscription Notification"
        verbose_name_plural = "Subscription Notifications"
        ordering = ['-created_at']
