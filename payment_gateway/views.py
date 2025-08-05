from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework import status
from accounts.models import DealerProfile
from .models import SubscriptionPlan, DealerSubscription, PaymentTransaction, BankDetails
from .serializers import (
    SubscriptionPlanSerializer, 
    DealerSubscriptionSerializer, 
    PaymentTransactionSerializer,
    SubmitPaymentSerializer,
    BankDetailsSerializer
)
from .utils import auto_expire_subscriptions, get_dealer_active_subscription, check_subscription_status

# Custom permission classes
class IsAdminUserCustom(BasePermission):
    """
    Custom permission to only allow admin users to access the view.
    Requires the user to be authenticated and have is_admin=True.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            getattr(request.user, 'is_admin', False)
        )

# Create your views here.

def check_trial_eligibility(dealer):
    """
    Check if a dealer is eligible for free trial
    Returns True if eligible, False if already used
    """
    previous_trial = DealerSubscription.objects.filter(
        dealer=dealer,
        plan__plan_type='trial'
    ).first()
    return not bool(previous_trial)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUserCustom])
def expire_subscriptions_manually(request):
    """
    Admin endpoint to manually expire outdated subscriptions
    This can be called periodically or as needed
    """
    # Note: In production, add admin permission check
    try:
        expired_count = auto_expire_subscriptions()
        return Response({
            'message': f'Successfully expired {expired_count} subscriptions',
            'expired_count': expired_count
        })
    except Exception as e:
        return Response(
            {'error': f'Failed to expire subscriptions: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_trial_eligibility_view(request):
    """API endpoint to check if current dealer is eligible for free trial"""
    try:
        dealer = DealerProfile.objects.get(auth_id=request.user)
        is_eligible = check_trial_eligibility(dealer)
        
        response_data = {
            'trial_eligible': is_eligible,
            'message': 'You are eligible for free trial' if is_eligible else 'You have already used your one-time free trial'
        }
        
        if not is_eligible:
            # Get the previous trial subscription details
            previous_trial = DealerSubscription.objects.filter(
                dealer=dealer,
                plan__plan_type='trial'
            ).first()
            if previous_trial:
                response_data['previous_trial'] = {
                    'start_date': previous_trial.start_date,
                    'end_date': previous_trial.end_date,
                    'status': previous_trial.status
                }
        
        return Response(response_data)
        
    except DealerProfile.DoesNotExist:
        return Response(
            {'error': 'Dealer profile not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


class SubscriptionPlanListView(APIView):
    """API view to list all available subscription plans"""
    
    def get(self, request):
        plans = SubscriptionPlan.objects.filter(is_active=True)
        serializer = SubscriptionPlanSerializer(plans, many=True)
        
        # If user is authenticated, check if they've used trial before
        response_data = serializer.data
        if request.user.is_authenticated:
            try:
                dealer = DealerProfile.objects.get(auth_id=request.user)
                previous_trial = DealerSubscription.objects.filter(
                    dealer=dealer,
                    plan__plan_type='trial'
                ).first()
                
                # Add flag to indicate if trial was already used
                for plan in response_data:
                    if plan.get('plan_type') == 'trial':
                        plan['trial_already_used'] = bool(previous_trial)
                        plan['available'] = not bool(previous_trial)
                    else:
                        plan['available'] = True
                        
            except DealerProfile.DoesNotExist:
                # If no dealer profile, mark trial as available
                for plan in response_data:
                    plan['available'] = True
                    if plan.get('plan_type') == 'trial':
                        plan['trial_already_used'] = False
        else:
            # If not authenticated, mark all as available
            for plan in response_data:
                plan['available'] = True
                if plan.get('plan_type') == 'trial':
                    plan['trial_already_used'] = False
        
        return Response(response_data)


class DealerSubscriptionView(APIView):
    """API view for dealer subscription management"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get current dealer's subscription status"""
        try:
            dealer = DealerProfile.objects.get(auth_id=request.user)
            
            # Use utility function to get subscription status with auto-expiration
            subscription_status = check_subscription_status(dealer)
            
            if subscription_status['has_active_subscription']:
                serializer = DealerSubscriptionSerializer(subscription_status['subscription'])
                return Response({
                    'has_active_subscription': True,
                    'subscription': serializer.data,
                    'marketplace_access': True
                })
            else:
                response_data = {
                    'has_active_subscription': False,
                    'subscription': None,
                    'marketplace_access': False,
                    'message': 'No active subscription found. Please subscribe to access the marketplace.'
                }
                
                # If there was a recent subscription that expired, include its details
                if subscription_status['last_subscription']:
                    serializer = DealerSubscriptionSerializer(subscription_status['last_subscription'])
                    response_data['last_subscription'] = serializer.data
                    response_data['message'] = 'Your subscription has expired. Please renew to access the marketplace.'
                
                return Response(response_data)
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
            
            # Check if dealer already has an active subscription (with auto-expiration)
            existing_subscription = get_dealer_active_subscription(dealer)
            
            if existing_subscription:
                return Response(
                    {'error': 'You already have an active subscription'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if dealer is trying to use trial plan but has already used it before
            if plan.plan_type == 'trial':
                previous_trial = DealerSubscription.objects.filter(
                    dealer=dealer,
                    plan__plan_type='trial'
                ).first()
                
                if previous_trial:
                    return Response(
                        {
                            'error': 'Free trial can only be used once. Please choose a paid subscription plan.',
                            'message': 'You have already used your one-time free trial period. Please select from our paid subscription plans to continue.',
                            'redirect_to_paid_plans': True
                        }, 
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
        
        # Use utility function to get active subscription with auto-expiration
        active_subscription = get_dealer_active_subscription(dealer)
        
        if active_subscription and active_subscription.is_active:
            return Response({
                'access_granted': True,
                'subscription_type': active_subscription.plan.plan_type,
                'days_remaining': active_subscription.days_remaining,
                'expires_on': active_subscription.end_date
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
        
        # Check if dealer is trying to renew with trial plan but has already used it before
        if plan.plan_type == 'trial':
            previous_trial = DealerSubscription.objects.filter(
                dealer=dealer,
                plan__plan_type='trial'
            ).first()
            
            if previous_trial:
                return Response(
                    {
                        'error': 'Free trial can only be used once. Please choose a paid subscription plan.',
                        'message': 'You have already used your one-time free trial period. Please select from our paid subscription plans to renew.',
                        'redirect_to_paid_plans': True
                    }, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
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
@permission_classes([IsAuthenticated, IsAdminUserCustom])
def verify_payment(request, payment_id):
    """Admin endpoint to verify payment and activate subscription"""
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


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUserCustom])
def get_all_dealers_with_subscriptions(request):
    """
    Admin-only endpoint to get all dealers with their subscription details
    """
    try:
        # Get all dealers with their related subscriptions, excluding those without auth_id
        dealers = DealerProfile.objects.select_related('auth_id').prefetch_related(
            'subscriptions__plan',
            'subscriptions__payment_transactions'
        ).filter(auth_id__isnull=False)
        
        dealers_data = []
        
        for dealer in dealers:
            # Get dealer's current active subscription
            active_subscription = dealer.subscriptions.filter(
                status='active',
                start_date__lte=timezone.now(),
                end_date__gte=timezone.now()
            ).first()
            
            # Get dealer's latest subscription (active or not)
            latest_subscription = dealer.subscriptions.order_by('-created_at').first()
            
            # Get subscription history count
            subscription_count = dealer.subscriptions.count()
            
            dealer_info = {
                'dealer_id': dealer.id,
                'kt_id': dealer.kt_id,
                'dealer_name': dealer.auth_id.full_name if dealer.auth_id.full_name else dealer.auth_id.email,
                'email': dealer.auth_id.email,
                'phone_number': dealer.auth_id.phone_number or 'N/A',
                'profile_type': dealer.profile_type or 'N/A',
                'account_active': dealer.auth_id.is_active,
                'total_subscriptions': subscription_count,
                'current_subscription': None,
                'latest_subscription': None,
                'marketplace_access': False
            }
            
            # Add current active subscription details
            if active_subscription:
                # Get the payment transaction for this subscription (using prefetched data)
                payment_transaction = active_subscription.payment_transactions.first()
                
                dealer_info['current_subscription'] = {
                    'id': active_subscription.id,
                    'plan_name': active_subscription.plan.name,
                    'plan_type': active_subscription.plan.plan_type,
                    'start_date': active_subscription.start_date,
                    'end_date': active_subscription.end_date,
                    'status': active_subscription.status,
                    'is_trial': active_subscription.is_trial,
                    'days_remaining': active_subscription.days_remaining,
                    'is_expiring_soon': active_subscription.is_expiring_soon,
                    'payment_transaction_id': payment_transaction.id if payment_transaction else None,
                    'user_transaction_reference': payment_transaction.transaction_id if payment_transaction else None,
                    'payment_verified': payment_transaction.verified if payment_transaction else None,
                    'payment_method': payment_transaction.payment_method if payment_transaction else None
                }
                dealer_info['marketplace_access'] = True
            
            # Add latest subscription details if different from active
            if latest_subscription and (not active_subscription or latest_subscription.id != active_subscription.id):
                # Get the payment transaction for this subscription (using prefetched data)
                latest_payment_transaction = latest_subscription.payment_transactions.first()
                
                dealer_info['latest_subscription'] = {
                    'id': latest_subscription.id,
                    'plan_name': latest_subscription.plan.name,
                    'plan_type': latest_subscription.plan.plan_type,
                    'start_date': latest_subscription.start_date,
                    'end_date': latest_subscription.end_date,
                    'status': latest_subscription.status,
                    'is_trial': latest_subscription.is_trial,
                    'payment_transaction_id': latest_payment_transaction.id if latest_payment_transaction else None,
                    'user_transaction_reference': latest_payment_transaction.transaction_id if latest_payment_transaction else None,
                    'payment_verified': latest_payment_transaction.verified if latest_payment_transaction else None,
                    'payment_method': latest_payment_transaction.payment_method if latest_payment_transaction else None
                }
            
            dealers_data.append(dealer_info)
        
        # Sort by latest subscription date (most recent first)
        # Handle cases where latest_subscription might be None
        def get_sort_date(dealer_data):
            if dealer_data.get('latest_subscription') and dealer_data['latest_subscription'].get('start_date'):
                return dealer_data['latest_subscription']['start_date']
            elif dealer_data.get('current_subscription') and dealer_data['current_subscription'].get('start_date'):
                return dealer_data['current_subscription']['start_date']
            else:
                # Return a very old date for dealers without any subscriptions
                return timezone.make_aware(datetime.min)
        
        dealers_data.sort(key=get_sort_date, reverse=True)
        
        return Response({
            'total_dealers': len(dealers_data),
            'dealers_with_subscriptions': len([d for d in dealers_data if d['total_subscriptions'] > 0]),
            'dealers_with_active_access': len([d for d in dealers_data if d['marketplace_access']]),
            'dealers': dealers_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to retrieve dealer subscriptions: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )