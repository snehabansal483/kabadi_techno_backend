import requests
from django.db.models.signals import post_save,pre_save
from django.dispatch import receiver
from .models import DigiPinAddress

@receiver(pre_save, sender=DigiPinAddress)
def fetch_coordinates_and_digipin(sender, instance, **kwargs):
    if instance.address and (instance.latitude is None or instance.longitude is None):
        address_obj = instance.address
        full_address = ", ".join(filter(None, [
            address_obj.add_line1,
            address_obj.add_line2,
            address_obj.landmark,
            address_obj.city,
            address_obj.state,
            address_obj.country
        ]))

        url = 'https://nominatim.openstreetmap.org/search'
        params = {
            'q': full_address,
            'format': 'json'
        }
        try:
            response = requests.get(url, params=params, headers={'User-Agent': 'digipin-app'})
            response.raise_for_status()
            data = response.json()

            if data:
                instance.latitude = float(data[0]['lat'])
                instance.longitude = float(data[0]['lon'])
                instance.pincode = address_obj.zipcode
                instance.digipin = f"DIGI{str(abs(hash(instance.latitude + instance.longitude)))[:6]}"
            else:
                print("No data returned from Nominatim for address:", full_address)
        except Exception as e:
            print("Error fetching location:", e)

@receiver(pre_save, sender=DigiPinAddress)
def generate_digipin_url(sender, instance, **kwargs):
    if instance.latitude is not None and instance.longitude is not None:
        instance.digipin_url = f"https://www.google.com/maps?q={instance.latitude},{instance.longitude}"
    else:
        instance.digipin_url = None