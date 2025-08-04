from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from accounts.models import DealerProfile
from .models import SubscriptionPlan, DealerSubscription, SubscriptionHistory, PaymentTransaction, BankDetails
from .serializers import (
    SubscriptionPlanSerializer, 
    DealerSubscriptionSerializer, 
    SubscriptionHistorySerializer,
    PaymentTransactionSerializer,
    SubmitPaymentSerializer,
    BankDetailsSerializer
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
            if plan.plan_type == 'trial':
                # Trial subscription - activate immediately
                subscription = DealerSubscription.objects.create(
                    dealer=dealer,
                    plan=plan,
                    is_trial=True,
                    status='active'
                )
                message = 'Trial subscription activated successfully'
            else:
                # Paid subscription - set to pending until payment verification
                subscription = DealerSubscription.objects.create(
                    dealer=dealer,
                    plan=plan,
                    is_trial=False,
                    status='pending'
                )
                message = 'Subscription created successfully. Please submit payment details to activate.'
            
            serializer = DealerSubscriptionSerializer(subscription)
            return Response({
                'message': message,
                'subscription': serializer.data,
                'next_step': 'submit_payment' if plan.plan_type != 'trial' else 'complete'
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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_payment(request):
    """Submit payment details for a subscription"""
    try:
        dealer = DealerProfile.objects.get(auth_id=request.user)
        
        # Add context for validation
        serializer = SubmitPaymentSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            payment_transaction = serializer.save()
            
            # Update payment reference in subscription
            subscription = payment_transaction.subscription
            subscription.payment_reference = payment_transaction.transaction_id
            subscription.save()
            
            response_serializer = PaymentTransactionSerializer(payment_transaction)
            return Response({
                'message': 'Payment details submitted successfully. Awaiting admin verification.',
                'payment_transaction': response_serializer.data,
                'status': 'pending_verification'
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    except DealerProfile.DoesNotExist:
        return Response(
            {'error': 'Dealer profile not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
def get_bank_details(request):
    """Get company bank details for NEFT transfer and QR code"""
    try:
        bank_details = BankDetails.objects.filter(is_active=True).first()
        
        if not bank_details:
            return Response(
                {'error': 'Bank details not configured'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = BankDetailsSerializer(bank_details, context={'request': request})
        return Response(serializer.data)
        
    except Exception as e:
        return Response(
            {'error': 'Failed to retrieve bank details'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_payment_status(request, subscription_id):
    """Get payment status for a specific subscription"""
    try:
        dealer = DealerProfile.objects.get(auth_id=request.user)
        subscription = get_object_or_404(DealerSubscription, id=subscription_id, dealer=dealer)
        
        payment_transaction = PaymentTransaction.objects.filter(subscription=subscription).first()
        
        if not payment_transaction:
            return Response({
                'payment_submitted': False,
                'subscription_status': subscription.status,
                'message': 'No payment details submitted yet.'
            })
        
        serializer = PaymentTransactionSerializer(payment_transaction)
        return Response({
            'payment_submitted': True,
            'payment_verified': payment_transaction.verified,
            'subscription_status': subscription.status,
            'payment_details': serializer.data
        })
        
    except DealerProfile.DoesNotExist:
        return Response(
            {'error': 'Dealer profile not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_payment(request, payment_id):
    """Admin endpoint to verify payment and activate subscription"""
    # Note: This should have admin permission check in a real application
    try:
        payment_transaction = get_object_or_404(PaymentTransaction, id=payment_id)
        action = request.data.get('action')  # 'approve' or 'reject'
        notes = request.data.get('notes', '')
        
        if action == 'approve':
            # Verify the payment
            payment_transaction.verified = True
            payment_transaction.verified_by = request.user.username
            payment_transaction.verified_at = timezone.now()
            payment_transaction.notes = notes
            payment_transaction.save()
            
            # Activate the subscription
            subscription = payment_transaction.subscription
            subscription.status = 'active'
            subscription.start_date = timezone.now()
            subscription.end_date = subscription.start_date + timezone.timedelta(days=subscription.plan.duration_days)
            subscription.save()
            
            return Response({
                'message': 'Payment verified and subscription activated successfully',
                'subscription_id': subscription.id,
                'status': 'active'
            })
            
        elif action == 'reject':
            payment_transaction.notes = notes
            payment_transaction.save()
            
            # Optionally cancel the subscription
            subscription = payment_transaction.subscription
            subscription.status = 'cancelled'
            subscription.save()
            
            return Response({
                'message': 'Payment rejected and subscription cancelled',
                'subscription_id': subscription.id,
                'status': 'cancelled'
            })
        
        else:
            return Response(
                {'error': 'Invalid action. Use "approve" or "reject"'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
    except PaymentTransaction.DoesNotExist:
        return Response(
            {'error': 'Payment transaction not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
