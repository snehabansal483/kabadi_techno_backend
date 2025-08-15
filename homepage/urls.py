from django.urls import path
from .views import ContactCreateView, ContactListCreateView, create_waste_donation, list_waste_donations

urlpatterns = [
    path('contacts/', ContactListCreateView.as_view(), name='contact-list-create'),
    path('contacts/create/', ContactCreateView.as_view(), name='contact-create'),
    # path('donate/', CreateDonationView.as_view(), name='create-donation'),
    # path('payment-success/', payment_success, name='payment-success'),
    path('waste-donation/', create_waste_donation, name='create_waste_donation'),
    path('waste-donations/', list_waste_donations, name='list_waste_donations'),
]
