from django.urls import path

from . import views


urlpatterns = [
    path('dealer/<str:order_number>/', views.dealer_invoice_view, name='download_invoice'),
]
