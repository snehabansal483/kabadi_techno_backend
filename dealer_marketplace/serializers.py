from rest_framework import serializers
from .models import *

class dealer_initiatives_serializer(serializers.ModelSerializer):
    class Meta:
        model =dealer_initiatives
        fields = '__all__'

class schedule_pickup_serializer(serializers.ModelSerializer):
    class Meta:
        model =schedule_pickup
        fields = '__all__'

class reach_us_serializer(serializers.ModelSerializer):
    class Meta:
        model = reach_us
        fields = '__all__'

class dealer_rating_serializer(serializers.ModelSerializer):
    class Meta:
        model = dealer_rating
        fields = '__all__'
