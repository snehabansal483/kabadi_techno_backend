from django.db import models

class Address(models.Model):
    address = models.CharField(max_length=255)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    digipin = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"{self.address} -> {self.digipin}"
