# Example of how to use subscription decorator in marketplace views

from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from payment_gateway.decorators import subscription_required, check_subscription_status
from accounts.models import DealerProfile


# Example 1: Using the decorator
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@subscription_required
def marketplace_products_view(request):
    """
    Example marketplace view that requires active subscription
    """
    # The decorator automatically checks subscription and adds request.dealer_subscription
    subscription = getattr(request, 'dealer_subscription', None)
    
    return JsonResponse({
        'message': 'Welcome to the marketplace!',
        'subscription_info': {
            'plan': subscription.plan.name if subscription else None,
            'days_remaining': subscription.days_remaining if subscription else 0,
            'is_trial': subscription.is_trial if subscription else False
        },
        'products': [
            # Your marketplace products here
        ]
    })


# Example 2: Manual subscription check
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def marketplace_dashboard_view(request):
    """
    Example view with manual subscription check
    """
    try:
        dealer = DealerProfile.objects.get(auth_id=request.user)
        has_access, subscription_data = check_subscription_status(dealer)
        
        if not has_access:
            return JsonResponse({
                'error': 'Subscription required',
                'message': 'Please subscribe to access the marketplace dashboard',
                'subscription_plans_url': '/api/payment/plans/'
            }, status=403)
        
        return JsonResponse({
            'message': 'Dashboard data',
            'subscription': subscription_data,
            'dashboard_data': {
                # Your dashboard data here
            }
        })
        
    except DealerProfile.DoesNotExist:
        return JsonResponse({'error': 'Dealer profile not found'}, status=404)


# Example 3: Using in class-based views
from rest_framework.views import APIView
from rest_framework.response import Response

class MarketplaceAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            dealer = DealerProfile.objects.get(auth_id=request.user)
            has_access, subscription_data = check_subscription_status(dealer)
            
            if not has_access:
                return Response({
                    'error': 'Subscription required',
                    'message': 'Please subscribe to access the marketplace',
                    'subscription_data': subscription_data
                }, status=403)
            
            # Your marketplace logic here
            return Response({
                'marketplace_data': 'Your data here',
                'subscription': subscription_data
            })
            
        except DealerProfile.DoesNotExist:
            return Response({'error': 'Dealer profile not found'}, status=404)
