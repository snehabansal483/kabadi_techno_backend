from django.db import models

class Contact(models.Model):
    PROFILE_CHOICES = [
        ('kabaadiwaale', 'Kabaadiwaale'),
        ('collectors', 'Collectors'),
    ]

    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    message = models.TextField()
    profile_type = models.CharField(max_length=20, choices=PROFILE_CHOICES)
    company_or_organization = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} - {self.profile_type}"



# class Donation(models.Model):
#     name = models.CharField(max_length=255)
#     phone_number = models.CharField(max_length=20)
#     email = models.EmailField()
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     payment_id = models.CharField(max_length=255, blank=True, null=True)  # Razorpay payment ID
#     payment_status = models.CharField(max_length=50, default="Pending")   # Success / Failed / Pending
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.name} - ₹{self.amount}"


class WasteDonation(models.Model):
    donor_name = models.CharField(max_length=255)
    donation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.donor_name        
