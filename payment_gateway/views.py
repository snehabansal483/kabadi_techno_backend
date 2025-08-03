from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from accounts.models import DealerProfile
from .models import SubscriptionPlan, DealerSubscription, SubscriptionHistory
from .serializers import (
    SubscriptionPlanSerializer, 
    DealerSubscriptionSerializer, 
    SubscriptionHistorySerializer
)

# Create your views here.

class SubscriptionPlanListView(APIView):
    """API view to list all available subscription plans"""
    
    def get(self, request):
        plans = SubscriptionPlan.objects.filter(is_active=True)
        serializer = SubscriptionPlanSerializer(plans, many=True)
        return Response(serializer.data)


class DealerSubscriptionView(APIView):
    """API view for dealer subscription management"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get current dealer's subscription status"""
        try:
            dealer = DealerProfile.objects.get(auth_id=request.user)
            current_subscription = DealerSubscription.objects.filter(
                dealer=dealer, 
                status='active'
            ).first()
            
            if current_subscription:
                serializer = DealerSubscriptionSerializer(current_subscription)
                return Response({
                    'has_active_subscription': True,
                    'subscription': serializer.data,
                    'marketplace_access': current_subscription.is_active
                })
            else:
                return Response({
                    'has_active_subscription': False,
                    'subscription': None,
                    'marketplace_access': False,
                    'message': 'No active subscription found. Please subscribe to access the marketplace.'
                })
        except DealerProfile.DoesNotExist:
            return Response(
                {'error': 'Dealer profile not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    def post(self, request):
        """Create a new subscription for the dealer"""
        try:
            dealer = DealerProfile.objects.get(auth_id=request.user)
            plan_id = request.data.get('plan_id')
            
            if not plan_id:
                return Response(
                    {'error': 'Plan ID is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            plan = get_object_or_404(SubscriptionPlan, id=plan_id, is_active=True)
            
            # Check if dealer already has an active subscription
            existing_subscription = DealerSubscription.objects.filter(
                dealer=dealer, 
                status='active'
            ).first()
            
            if existing_subscription:
                return Response(
                    {'error': 'You already have an active subscription'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create new subscription
            subscription = DealerSubscription.objects.create(
                dealer=dealer,
                plan=plan,
                is_trial=(plan.plan_type == 'trial'),
                status='active' if plan.plan_type == 'trial' else 'pending'
            )
            
            # If it's a trial, activate immediately
            if plan.plan_type == 'trial':
                subscription.status = 'active'
                subscription.save()
            
            serializer = DealerSubscriptionSerializer(subscription)
            return Response({
                'message': 'Subscription created successfully',
                'subscription': serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except DealerProfile.DoesNotExist:
            return Response(
                {'error': 'Dealer profile not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_marketplace_access(request):
    """Check if dealer has marketplace access"""
    try:
        dealer = DealerProfile.objects.get(auth_id=request.user)
        current_subscription = DealerSubscription.objects.filter(
            dealer=dealer, 
            status='active'
        ).first()
        
        if current_subscription and current_subscription.is_active:
            return Response({
                'access_granted': True,
                'subscription_type': current_subscription.plan.plan_type,
                'days_remaining': current_subscription.days_remaining,
                'expires_on': current_subscription.end_date
            })
        else:
            return Response({
                'access_granted': False,
                'message': 'Your subscription has expired. Please renew to access the marketplace.',
                'available_plans_url': '/api/subscription/plans/'
            })
    except DealerProfile.DoesNotExist:
        return Response(
            {'error': 'Dealer profile not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def renew_subscription(request):
    """Renew an existing subscription"""
    try:
        dealer = DealerProfile.objects.get(auth_id=request.user)
        plan_id = request.data.get('plan_id')
        
        if not plan_id:
            return Response(
                {'error': 'Plan ID is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        plan = get_object_or_404(SubscriptionPlan, id=plan_id, is_active=True)
        
        # Get current subscription
        current_subscription = DealerSubscription.objects.filter(
            dealer=dealer
        ).order_by('-created_at').first()
        
        # Create new subscription starting from current subscription end date or now
        start_date = timezone.now()
        if current_subscription and current_subscription.end_date > timezone.now():
            start_date = current_subscription.end_date
        
        new_subscription = DealerSubscription.objects.create(
            dealer=dealer,
            plan=plan,
            start_date=start_date,
            status='pending'  # Will be activated after payment
        )
        
        serializer = DealerSubscriptionSerializer(new_subscription)
        return Response({
            'message': 'Subscription renewal initiated',
            'subscription': serializer.data
        }, status=status.HTTP_201_CREATED)
        
    except DealerProfile.DoesNotExist:
        return Response(
            {'error': 'Dealer profile not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def subscription_history(request):
    """Get dealer's subscription history"""
    try:
        dealer = DealerProfile.objects.get(auth_id=request.user)
        subscriptions = DealerSubscription.objects.filter(dealer=dealer).order_by('-created_at')
        serializer = DealerSubscriptionSerializer(subscriptions, many=True)
        return Response(serializer.data)
    except DealerProfile.DoesNotExist:
        return Response(
            {'error': 'Dealer profile not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
