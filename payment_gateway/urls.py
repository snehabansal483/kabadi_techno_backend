from django.urls import path
from . import views

urlpatterns = [
    # Subscription plan endpoints
    path('plans/', views.SubscriptionPlanListView.as_view(), name='subscription_plans'),
    
    # Dealer subscription management
    path('subscription/', views.DealerSubscriptionView.as_view(), name='dealer_subscription'),
    path('subscription/history/', views.subscription_history, name='subscription_history'),
    path('subscription/renew/', views.renew_subscription, name='renew_subscription'),
    
    # Marketplace access check
    path('access/check/', views.check_marketplace_access, name='check_marketplace_access'),
]
