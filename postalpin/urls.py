from django.urls import path
from .views import AddressCreateView, VerifyDigiPIN

urlpatterns = [
    path('create-address/', AddressCreateView.as_view(), name='create-address'),
    path('verify-digipin/<str:digipin>/', VerifyDigiPIN.as_view(), name='verify-digipin'),
]
