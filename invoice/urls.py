from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for API endpoints
router = DefaultRouter()
router.register(r'commissions', views.DealerCommissionViewSet)

urlpatterns = [
    path('dealer/<str:order_number>/', views.dealer_invoice_view, name='download_invoice'),
    path('commission/<int:commission_id>/', views.dealer_commission_bill_view, name='dealer_commission_bill'),
    path('api/', include(router.urls)),
    path('submit-commission-payment/', views.submit_commission_payment, name='submit_commission_payment'),
    path('verify-commission-payment/<int:payment_id>/', views.verify_commission_payment, name='verify_commission_payment'),
    path('get-all-payment-details/', views.get_all_payment_details, name='get_all_payment_details'),
    path('get-all-dealers-with-orders/', views.get_all_dealers_with_orders, name='get_all_dealers_with_orders'),
]
