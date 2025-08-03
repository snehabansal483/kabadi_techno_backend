from functools import wraps
from django.http import JsonResponse
from django.shortcuts import redirect
from accounts.models import DealerProfile
from .models import DealerSubscription


def subscription_required(view_func=None, *, redirect_url=None):
    """
    Decorator to check if dealer has an active subscription
    Usage:
    @subscription_required
    def my_view(request):
        # Your view logic here
        
    @subscription_required(redirect_url='/subscription/plans/')
    def my_view(request):
        # Your view logic here
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({
                    'error': 'Authentication required'
                }, status=401)
            
            try:
                dealer = DealerProfile.objects.get(auth_id=request.user)
                active_subscription = DealerSubscription.objects.filter(
                    dealer=dealer,
                    status='active'
                ).first()
                
                if not active_subscription or not active_subscription.is_active:
                    if redirect_url:
                        return redirect(redirect_url)
                    
                    return JsonResponse({
                        'error': 'Subscription required',
                        'message': 'Your subscription has expired. Please renew to access this feature.',
                        'marketplace_access': False,
                        'subscription_plans_url': '/api/payment/plans/',
                        'days_remaining': 0
                    }, status=403)
                
                # Add subscription info to request for use in view
                request.dealer_subscription = active_subscription
                
            except DealerProfile.DoesNotExist:
                # User is not a dealer, this decorator shouldn't apply
                pass
            
            return func(request, *args, **kwargs)
        return wrapper
    
    if view_func is None:
        return decorator
    else:
        return decorator(view_func)


def check_subscription_status(dealer):
    """
    Utility function to check dealer subscription status
    Returns tuple: (has_access, subscription_data)
    """
    try:
        active_subscription = DealerSubscription.objects.filter(
            dealer=dealer,
            status='active'
        ).first()
        
        if active_subscription and active_subscription.is_active:
            return True, {
                'subscription_id': active_subscription.id,
                'plan_name': active_subscription.plan.name,
                'plan_type': active_subscription.plan.plan_type,
                'days_remaining': active_subscription.days_remaining,
                'end_date': active_subscription.end_date,
                'is_trial': active_subscription.is_trial,
                'is_expiring_soon': active_subscription.is_expiring_soon
            }
        else:
            return False, {
                'message': 'No active subscription found',
                'last_subscription': None
            }
    except Exception as e:
        return False, {'error': str(e)}
