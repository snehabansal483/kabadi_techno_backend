import requests
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Address

@receiver(pre_save, sender=Address)
def fetch_coordinates_and_digipin(sender, instance, **kwargs):
    if instance.address and (instance.latitude is None or instance.longitude is None):
        url = 'https://nominatim.openstreetmap.org/search'
        params = {
            'q': instance.address,
            'format': 'json'
        }
        response = requests.get(url, params=params, headers={'User-Agent': 'digipin-app'})
        data = response.json()
        if data:
            instance.latitude = float(data[0]['lat'])
            instance.longitude = float(data[0]['lon'])

            # Create a DigiPIN (example: hash + lat/long shortened)
            instance.digipin = f"DIGI{str(abs(hash(instance.latitude + instance.longitude)))[:6]}"
