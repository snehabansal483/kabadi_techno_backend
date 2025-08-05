"""
Utility functions for subscription management
"""
from django.utils import timezone
from .models import DealerSubscription


def auto_expire_subscriptions():
    """
    Automatically expire subscriptions that have passed their end_date
    This can be called from views or scheduled tasks
    
    Returns:
        int: Number of subscriptions that were expired
    """
    expired_subscriptions = DealerSubscription.objects.filter(
        status='active',
        end_date__lt=timezone.now()
    )
    
    count = expired_subscriptions.count()
    if count > 0:
        expired_subscriptions.update(status='expired')
    
    return count


def get_dealer_active_subscription(dealer):
    """
    Get dealer's active subscription, automatically expiring if needed
    
    Args:
        dealer: DealerProfile instance
        
    Returns:
        DealerSubscription or None: Active subscription if exists
    """
    # First expire any outdated subscriptions
    DealerSubscription.objects.filter(
        dealer=dealer,
        status='active',
        end_date__lt=timezone.now()
    ).update(status='expired')
    
    # Then get the active subscription
    return DealerSubscription.objects.filter(
        dealer=dealer,
        status='active'
    ).first()


def check_subscription_status(dealer):
    """
    Check dealer's subscription status with automatic expiration
    
    Args:
        dealer: DealerProfile instance
        
    Returns:
        dict: Subscription status information
    """
    active_subscription = get_dealer_active_subscription(dealer)
    
    if active_subscription and active_subscription.is_active:
        return {
            'has_active_subscription': True,
            'subscription': active_subscription,
            'marketplace_access': True,
            'status': 'active'
        }
    else:
        # Get the most recent subscription for historical reference
        recent_subscription = DealerSubscription.objects.filter(
            dealer=dealer
        ).order_by('-created_at').first()
        
        return {
            'has_active_subscription': False,
            'subscription': None,
            'marketplace_access': False,
            'status': 'expired' if recent_subscription else 'no_subscription',
            'last_subscription': recent_subscription
        }
