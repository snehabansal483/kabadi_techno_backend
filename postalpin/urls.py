from django.urls import path
from .views import DigiPinAddressCreateView, VerifyDigiPIN

urlpatterns = [
    path('create-address/', DigiPinAddressCreateView.as_view(), name='create-address'),
    path('verify-digipin/', VerifyDigiPIN.as_view(), name='verify-digipin'),
]
