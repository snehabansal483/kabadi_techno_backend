from django.shortcuts import render
from .serializers import *
# Create your views here.
from .models import *

from rest_framework import viewsets

class dealer_initiatives_viewset(viewsets.ModelViewSet):
    queryset = dealer_initiatives.objects.all()
    serializer_class = dealer_initiatives_serializer

class schedule_pickup(viewsets.ModelViewSet):
    queryset = schedule_pickup.objects.all()
    serializer_class = schedule_pickup_serializer

class reach_us_viewset(viewsets.ModelViewSet):
    queryset = reach_us.objects.all()
    serializer_class = reach_us_serializer

class dealer_rating_viewset(viewsets.ModelViewSet):
    queryset = dealer_rating.objects.all()
    serializer_class = dealer_rating_serializer
