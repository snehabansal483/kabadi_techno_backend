from django.urls import path
from . import views

urlpatterns = [
    # Subscription plan endpoints
    path('plans/', views.SubscriptionPlanListView.as_view(), name='subscription_plans'),
    
    # Dealer subscription management
    path('subscription/', views.DealerSubscriptionView.as_view(), name='dealer_subscription'),
    path('subscription/history/', views.subscription_history, name='subscription_history'),
    path('subscription/renew/', views.renew_subscription, name='renew_subscription'),
    
    # Payment related endpoints
    path('submit-payment/', views.submit_payment, name='submit_payment'),
    path('bank-details/', views.get_bank_details, name='bank_details'),
    path('payment-status/<int:subscription_id>/', views.get_payment_status, name='payment_status'),
    path('verify-payment/<int:payment_id>/', views.verify_payment, name='verify_payment'),
    
    # Marketplace access check
    path('access/check/', views.check_marketplace_access, name='check_marketplace_access'),
]
