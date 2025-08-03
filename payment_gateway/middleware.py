from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.urls import resolve
from accounts.models import DealerProfile
from .models import DealerSubscription


class SubscriptionMiddleware(MiddlewareMixin):
    """
    Middleware to check dealer subscription status for marketplace access
    """
    
    # URLs that require subscription check (marketplace related)
    SUBSCRIPTION_REQUIRED_URLS = [
        'marketplace',  # Add your marketplace URL patterns here
        'dealer_marketplace',
        # Add other marketplace-related URL names
    ]
    
    # URLs that should be excluded from subscription check
    EXCLUDED_URLS = [
        'subscription_plans',
        'dealer_subscription', 
        'check_marketplace_access',
        'renew_subscription',
        'admin',
        'login',
        'register',
        'payment',
    ]
    
    def process_request(self, request):
        # Skip middleware for non-authenticated users
        if not request.user.is_authenticated:
            return None
        
        # Get current URL name
        try:
            url_name = resolve(request.path_info).url_name
        except:
            return None
        
        # Skip if URL is excluded
        if any(excluded in request.path for excluded in self.EXCLUDED_URLS):
            return None
        
        # Check if this URL requires subscription
        requires_subscription = any(required in request.path for required in self.SUBSCRIPTION_REQUIRED_URLS)
        
        if requires_subscription:
            try:
                # Check if user is a dealer
                dealer = DealerProfile.objects.get(auth_id=request.user)
                
                # Check for active subscription
                active_subscription = DealerSubscription.objects.filter(
                    dealer=dealer,
                    status='active'
                ).first()
                
                if not active_subscription or not active_subscription.is_active:
                    return JsonResponse({
                        'error': 'Subscription required',
                        'message': 'Your subscription has expired. Please renew to access the marketplace.',
                        'marketplace_access': False,
                        'subscription_plans_url': '/api/payment/plans/'
                    }, status=403)
                    
            except DealerProfile.DoesNotExist:
                # User is not a dealer, allow access
                pass
        
        return None
