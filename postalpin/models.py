# # models.py
# from django.db import models

# class DigiPinAddress(models.Model):
#     address = models.CharField(max_length=255)
#     pincode = models.CharField(max_length=6, null=True, blank=True)
#     latitude = models.FloatField(null=True, blank=True)
#     longitude = models.FloatField(null=True, blank=True)
#     digipin = models.CharField(max_length=20, null=True, blank=True)
#     digipin_url = models.URLField(null=True, blank=True)  # new field

#     def __str__(self):
#         return f"{self.address} -> {self.digipin}"


# digipin/models.py

from django.db import models
from accounts.models import Address  # adjust import if different

class DigiPinAddress(models.Model):
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    pincode = models.CharField(max_length=6, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    digipin = models.CharField(max_length=20, null=True, blank=True)
    digipin_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return f"{self.address} -> {self.digipin}"
