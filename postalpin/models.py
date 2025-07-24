# models.py
from django.db import models

class Address(models.Model):
    address = models.CharField(max_length=255)
    pincode = models.CharField(max_length=6, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    digipin = models.CharField(max_length=20, null=True, blank=True)
    digipin_url = models.URLField(null=True, blank=True)  # new field

    def __str__(self):
        return f"{self.address} -> {self.digipin}"
