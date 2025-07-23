from django.db import models
from accounts.models import DealerProfile
from datetime import date
from datetime import datetime
from dateutil.relativedelta import relativedelta
# Create your models here.
class Marketplace(models.Model):
    status_choice =(
        ('active','active'),
        ('deactive','deactive'),
    )
    dealer_id = models.ForeignKey(DealerProfile, on_delete=models.CASCADE, null=True)
    kt_id = models.CharField(max_length=100, null = True)
    url = models.CharField(max_length=240, null=True, blank=True)
    qrCode = models.ImageField(default = 'cvm_qrcodes/4.jpg', upload_to='marketplace/QRs')
    end_duration = models.DateField(null = True)
    duration_active = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=status_choice, default='deactive')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.dealer_id.auth_id)

    def save(self, *args, **kwargs):
        self.kt_id = self.dealer_id.kt_id
        today = date.today()
        print(self.end_duration)
        print(type(self.end_duration))
        if isinstance(self.end_duration, str):
            dt = self.end_duration
            date_format = "%Y-%m-%d"
            dt1 = datetime.strptime(dt, date_format)
            countd = dt1 - datetime.now()
            self.duration_active = countd.days
        else:
            today = date.today()
            countd = self.end_duration - today
            self.duration_active = countd.days
        if self.duration_active < 0:
            self.status = 'deactive'
            self.duration_active = 0
        super(Marketplace, self).save(*args, **kwargs)
    
