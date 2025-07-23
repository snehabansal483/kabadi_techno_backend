from django.urls import path,include
from .views import *
from rest_framework.routers import DefaultRouter

router1 = DefaultRouter()
router1.register('dealer_initiatives',dealer_initiatives_viewset,basename="initiatives")

router2 = DefaultRouter()
router2.register('schedule_pickup',schedule_pickup,basename="schedule_pickup")

router3 = DefaultRouter()
router3.register('reach_us',reach_us_viewset,basename="reach_us")

router4 = DefaultRouter()
router4.register('dealer_rating',dealer_rating_viewset,basename="dealer_rating")

urlpatterns = [
    path('dealer_initiatives/',include(router1.urls)),
    path('schedule_pickup/',include(router2.urls)),
    path('reach_us/',include(router3.urls)),
    path('dealer_rating/',include(router4.urls)),
]
