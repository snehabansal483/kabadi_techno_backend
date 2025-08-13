from order.models import Order, OrderProduct  
from django.shortcuts import render, get_object_or_404
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.conf import settings
import os

# Commission-related imports
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, BasePermission
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .models import DealerCommission, CommissionPaymentTransaction
from .serializers import DealerCommissionSerializer, CommissionPaymentTransactionSerializer, SubmitCommissionPaymentSerializer
from accounts.models import DealerProfile

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

def dealer_invoice_view(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number)
        order_items = OrderProduct.objects.filter(order=order)
    except Order.DoesNotExist:
        return render(request, 'invoice/dealer_invoice.html', {
            'order': None,
            'order_found': False,
            'order_number': order_number
        })

    # Only allow invoice for pending and accepted status
    if order.status in ["Cancelled by Customer", "Cancelled"]:
        return render(request, 'invoice/dealer_invoice.html', {
            'order': None,
            'order_found': False,
            'order_number': order_number,
            'message': "Invoice not available for cancelled orders."
        })

    # Calculate line totals and grand total
    grand_total = 0
    for item in order_items:
        item.total = item.quantity * item.price
        grand_total += item.total

    context = {
        'order': order,
        'order_items': order_items,
        'grand_total': grand_total,
        'order_found': True,
        'order_number': order_number,
    }

    if request.GET.get("download") == "pdf":
        template_path = 'invoice/dealer_invoice.html'
        template = get_template(template_path)
        html = template.render(context)
        output_path = os.path.join(settings.MEDIA_ROOT, 'invoices')
        os.makedirs(output_path, exist_ok=True)
        filename = f"invoice_{order_number}.pdf"
        full_path = os.path.join(output_path, filename)

        with open(full_path, "wb") as f:
            pisa.CreatePDF(html, dest=f)

        with open(full_path, "rb") as f:
            response = HttpResponse(f.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response

    return render(request, 'invoice/dealer_invoice.html', context)


def dealer_commission_bill_view(request, commission_id):
    """
    Generate and display dealer commission bill
    """
    try:
        commission = DealerCommission.objects.select_related('dealer__auth_id').get(id=commission_id)
    except DealerCommission.DoesNotExist:
        return render(request, 'invoice/dealer_commission_bill.html', {
            'commission': None,
            'commission_found': False,
            'commission_id': commission_id
        })

    # Get the orders included in this commission
    orders = Order.objects.filter(
        order_number__in=commission.order_numbers,
        dealer_id=commission.dealer.id
    ).order_by('created_at')

    context = {
        'commission': commission,
        'orders': orders,
        'commission_found': True,
        'today': timezone.now(),
    }

    if request.GET.get("download") == "pdf":
        template_path = 'invoice/dealer_commission_bill.html'
        template = get_template(template_path)
        html = template.render(context)
        output_path = os.path.join(settings.MEDIA_ROOT, 'commission_bills')
        os.makedirs(output_path, exist_ok=True)
        filename = f"commission_bill_{commission.dealer.kt_id}_{commission.calculation_date}.pdf"
        full_path = os.path.join(output_path, filename)

        with open(full_path, "wb") as f:
            pisa.CreatePDF(html, dest=f)

        with open(full_path, "rb") as f:
            response = HttpResponse(f.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response

    return render(request, 'invoice/dealer_commission_bill.html', context)


class DealerCommissionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing dealer commissions
    """
    queryset = DealerCommission.objects.all().select_related('dealer__auth_id')
    serializer_class = DealerCommissionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by dealer if provided
        dealer_id = self.request.query_params.get('dealer_id', None)
        if dealer_id:
            queryset = queryset.filter(dealer_id=dealer_id)
            
        # Filter by date range if provided
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        if start_date:
            queryset = queryset.filter(calculation_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(calculation_date__lte=end_date)
        
        return queryset.order_by('-calculation_date')
    
    @action(detail=True, methods=['post'])
    def mark_as_paid(self, request, pk=None):
        """
        Mark a commission as paid and generate next month's commission if applicable
        """
        commission = self.get_object()
        
        # Check if payment is within 30 days of due date
        days_until_due = commission.days_until_due
        payment_within_30_days = days_until_due >= 0  # Not overdue
        
        # Mark current commission as paid
        commission.status = 'Paid'
        commission.save()
        
        response_data = {
            'status': 'success',
            'message': f'Commission for dealer {commission.dealer.kt_id} marked as paid'
        }
        
        # If paid within 30 days, generate next month's commission
        if payment_within_30_days:
            next_commission = self._generate_next_month_commission(commission.dealer)
            if next_commission:
                response_data['next_commission_generated'] = True
                response_data['next_commission_id'] = next_commission.id
                response_data['next_commission_amount'] = str(next_commission.commission_amount)
                response_data['message'] += f'. Next month commission generated with amount {next_commission.commission_amount}'
            else:
                response_data['next_commission_generated'] = False
                response_data['message'] += '. No new orders found for next month commission'
        else:
            response_data['next_commission_generated'] = False
            response_data['message'] += '. Payment was overdue, next commission not auto-generated'
        
        return Response(response_data)
    
    @action(detail=False, methods=['get'])
    def dealer_summary(self, request):
        """
        Get commission summary for a specific dealer
        """
        dealer_id = request.query_params.get('dealer_id')
        if not dealer_id:
            return Response(
                {'error': 'dealer_id parameter is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Try to get dealer by ID first, then by kt_id if it's not a number
            try:
                dealer_id_int = int(dealer_id)
                dealer = DealerProfile.objects.get(id=dealer_id_int)
            except (ValueError, TypeError):
                # If dealer_id is not a number, try kt_id
                dealer = DealerProfile.objects.get(kt_id=dealer_id)
        except DealerProfile.DoesNotExist:
            return Response(
                {'error': f'Dealer not found with ID or kt_id: {dealer_id}'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Auto-update commission calculation before returning summary
        self._auto_update_commission(dealer)
        
        commissions = DealerCommission.objects.filter(dealer=dealer).order_by('-calculation_date')
        
        # Calculate summary statistics
        total_commissions = commissions.count()
        paid_commissions = commissions.filter(status='Paid').count()
        unpaid_commissions = commissions.filter(status='Unpaid').count()
        total_commission_amount = sum(c.commission_amount for c in commissions)
        total_paid_amount = sum(c.commission_amount for c in commissions.filter(status='Paid'))
        total_unpaid_amount = sum(c.commission_amount for c in commissions.filter(status='Unpaid'))
        
        # Check for overdue commissions
        today = timezone.now().date()
        overdue_commissions = commissions.filter(
            status='Unpaid', 
            payment_due_date__lt=today
        ).count()

        payment_qr_url = (
        f"upi://pay?"
        f"pa=snehabansal481@okhdfcbank&"
        f"pn=Sneha%20Bansal&"
        f"am={total_unpaid_amount}&"  # Commission amount passed here
        f"cu=INR"
    )
        
        # Include payment transaction details if available
        commissions_data = []
        for commission in commissions:
            payment_transaction = CommissionPaymentTransaction.objects.filter(commission=commission).order_by('-created_at').first()
            transaction_data = {
                'id': payment_transaction.id,
                'transaction_id': payment_transaction.transaction_id,
                'amount': str(payment_transaction.amount),
                'payment_method': payment_transaction.payment_method,
                'payment_screenshot': payment_transaction.payment_screenshot.url,
                'created_at': payment_transaction.created_at,
                'status': 'pending_verification' if not payment_transaction.verified else 'verified'
            } if payment_transaction else None

            commission_data = DealerCommissionSerializer(commission).data
            commission_data['payment_transaction'] = transaction_data
            commissions_data.append(commission_data)

        return Response({
            'dealer': {
                'kt_id': dealer.kt_id,
                'name': dealer.auth_id.full_name if dealer.auth_id else '',
                'is_active': dealer.auth_id.is_active if dealer.auth_id else False
            },
            'summary': {
                'total_commissions': total_commissions,
                'paid_commissions': paid_commissions,
                'unpaid_commissions': unpaid_commissions,
                'overdue_commissions': overdue_commissions,
                'total_commission_amount': total_commission_amount,
                'total_paid_amount': total_paid_amount,
                'total_unpaid_amount': total_unpaid_amount
            },
            'payment_qr_url': payment_qr_url,
            'commissions': commissions_data
        })
    
    @action(detail=False, methods=['post'])
    def calculate_commission_preview(self, request):
        """
        Preview commission calculation for a dealer without saving
        """
        dealer_id = request.data.get('dealer_id')
        if not dealer_id:
            return Response(
                {'error': 'dealer_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Try to get dealer by ID first, then by kt_id if it's not a number
            try:
                dealer_id_int = int(dealer_id)
                dealer = DealerProfile.objects.get(id=dealer_id_int)
            except (ValueError, TypeError):
                # If dealer_id is not a number, try kt_id
                dealer = DealerProfile.objects.get(kt_id=dealer_id)
        except DealerProfile.DoesNotExist:
            return Response(
                {'error': f'Dealer not found with ID or kt_id: {dealer_id}'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Auto-update commission calculation
        self._auto_update_commission(dealer)
        
        # Calculate for last 30 days
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
        
        # Get orders for this dealer in the period
        orders = Order.objects.filter(
            dealer_id=dealer.id,
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
            is_ordered=True,
            status__in=['Confirmed', 'Completed']
        )
        
        total_amount = Decimal('0.00')
        order_numbers = []
        
        for order in orders:
            # Use order.order_total if available, otherwise calculate from products
            if order.order_total:
                order_total = Decimal(str(order.order_total))
            else:
                # Calculate from order products if order_total is not set
                order_products = OrderProduct.objects.filter(order=order)
                order_total = Decimal('0.00')
                for product in order_products:
                    if product.total_amount:
                        order_total += Decimal(str(product.total_amount))
                    else:
                        # Fallback calculation: quantity * price
                        product_total = Decimal(str(product.quantity)) * Decimal(str(product.price))
                        order_total += product_total
            
            total_amount += order_total
            order_numbers.append(order.order_number)
        
        commission_amount = total_amount * Decimal('0.01')
        
        return Response({
            'dealer_kt_id': dealer.kt_id,
            'calculation_period': f'{start_date} to {end_date}',
            'total_orders': len(order_numbers),
            'order_numbers': order_numbers,
            'total_order_amount': total_amount,
            'commission_rate': '1%',
            'commission_amount': commission_amount
        })
    
    @action(detail=False, methods=['post'])
    def generate_next_month_commission(self, request):
        """
        Manually generate next month commission for a dealer
        """
        dealer_id = request.data.get('dealer_id')
        if not dealer_id:
            return Response(
                {'error': 'dealer_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Try to get dealer by ID first, then by kt_id if it's not a number
            try:
                dealer_id_int = int(dealer_id)
                dealer = DealerProfile.objects.get(id=dealer_id_int)
            except (ValueError, TypeError):
                # If dealer_id is not a number, try kt_id
                dealer = DealerProfile.objects.get(kt_id=dealer_id)
        except DealerProfile.DoesNotExist:
            return Response(
                {'error': f'Dealer not found with ID or kt_id: {dealer_id}'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Generate next month commission
        next_commission = self._generate_next_month_commission(dealer)
        
        if next_commission:
            return Response({
                'status': 'success',
                'message': f'Next month commission generated for dealer {dealer.kt_id}',
                'commission_id': next_commission.id,
                'commission_amount': next_commission.commission_amount,
                'order_count': len(next_commission.order_numbers),
                'payment_due_date': next_commission.payment_due_date
            })
        else:
            return Response({
                'status': 'no_orders',
                'message': f'No new orders found for dealer {dealer.kt_id} to generate commission'
            })
    
    def _auto_update_commission(self, dealer):
        """
        Automatically update commission calculation for dealer with partial payment support
        """
        from datetime import timedelta
        
        # Calculate for last 30 days
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
        
        # Get orders for this dealer that haven't been included in any PAID commission yet
        # Only exclude orders from paid commissions, not unpaid ones
        paid_commissions = DealerCommission.objects.filter(dealer=dealer, status='Paid')
        included_order_numbers = set()
        for comm in paid_commissions:
            included_order_numbers.update(comm.order_numbers)
        
        # Get orders for this dealer in the period that aren't in paid commissions
        orders = Order.objects.filter(
            dealer_id=dealer.id,
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
            is_ordered=True,
            status__in=['Confirmed', 'Completed']
        ).exclude(order_number__in=included_order_numbers)
        
        if not orders.exists():
            return
        
        # Check existing UNPAID commission for today
        existing_commission = DealerCommission.objects.filter(
            dealer=dealer,
            calculation_date=end_date,
            status='Unpaid'
        ).first()
        
        # # Ensure no duplicate entries are created
        # if DealerCommission.objects.filter(dealer=dealer, calculation_date=end_date).exists():
        #     return
        
        # Calculate total order amount and collect order numbers
        total_amount = Decimal('0.00')
        order_numbers = []
        
        for order in orders:
            # Use order.order_total if available, otherwise calculate from products
            if order.order_total:
                order_total = Decimal(str(order.order_total))
            else:
                # Calculate from order products if order_total is not set
                order_products = OrderProduct.objects.filter(order=order)
                order_total = Decimal('0.00')
                for product in order_products:
                    if product.total_amount:
                        order_total += Decimal(str(product.total_amount))
                    else:
                        # Fallback calculation: quantity * price
                        product_total = Decimal(str(product.quantity)) * Decimal(str(product.price))
                        order_total += product_total
            
            total_amount += order_total
            order_numbers.append(order.order_number)
        
        if total_amount <= 0:
            return
        
        # Calculate 1% commission
        commission_amount = total_amount * Decimal('0.01')
        payment_due_date = end_date + timedelta(days=30)
        
        if existing_commission:
            # Update existing UNPAID commission with new orders
            existing_commission.order_numbers = order_numbers
            existing_commission.total_order_amount = total_amount
            existing_commission.commission_amount = commission_amount
            existing_commission.payment_due_date = payment_due_date
            existing_commission.save()
        else:
            # Create new commission record (only if no unpaid commission exists)
            DealerCommission.objects.create(
                dealer=dealer,
                order_numbers=order_numbers,
                total_order_amount=total_amount,
                commission_amount=commission_amount,
                calculation_date=end_date,
                payment_due_date=payment_due_date,
                status='Unpaid'
            )

    def _generate_next_month_commission(self, dealer):
        """
        Generate next month's commission for a dealer after they pay current commission
        """
        from datetime import timedelta
        
        # Calculate period for next month (next 30 days from today)
        start_date = timezone.now().date()
        
        # Get orders for this dealer that haven't been included in any PAID commission yet
        # Only exclude orders from paid commissions, not unpaid ones
        paid_commissions = DealerCommission.objects.filter(dealer=dealer, status='Paid')
        included_order_numbers = set()
        for comm in paid_commissions:
            included_order_numbers.update(comm.order_numbers)
        
        # Get recent orders (last 30 days) that haven't been included in any PAID commission yet
        recent_orders = Order.objects.filter(
            dealer_id=dealer.id,
            created_at__date__gte=start_date - timedelta(days=30),  # Look back 30 days for new orders
            created_at__date__lte=start_date,  # Up to today
            is_ordered=True,
            status__in=['Confirmed', 'Completed']
        ).exclude(order_number__in=included_order_numbers)
        
        if not recent_orders.exists():
            return None
        
        # Calculate total order amount and collect order numbers
        total_amount = Decimal('0.00')
        order_numbers = []
        
        for order in recent_orders:
            # Use order.order_total if available, otherwise calculate from products
            if order.order_total:
                order_total = Decimal(str(order.order_total))
            else:
                # Calculate from order products if order_total is not set
                order_products = OrderProduct.objects.filter(order=order)
                order_total = Decimal('0.00')
                for product in order_products:
                    if product.total_amount:
                        order_total += Decimal(str(product.total_amount))
                    else:
                        # Fallback calculation: quantity * price
                        product_total = Decimal(str(product.quantity)) * Decimal(str(product.price))
                        order_total += product_total
            
            total_amount += order_total
            order_numbers.append(order.order_number)
        
        if total_amount <= 0:
            return None
        
        # Calculate 1% commission
        commission_amount = total_amount * Decimal('0.01')
        payment_due_date = start_date + timedelta(days=30)
        
        # Check if there's already an UNPAID commission for today for this dealer
        existing_unpaid_today = DealerCommission.objects.filter(
            dealer=dealer,
            calculation_date=start_date,
            status='Unpaid'
        ).first()
        
        # Ensure no duplicate entries are created for the next month
        if DealerCommission.objects.filter(dealer=dealer, calculation_date=start_date).exists():
            return None
        
        if existing_unpaid_today:
            # Update existing unpaid commission with new orders (merge new orders)
            all_order_numbers = list(set(existing_unpaid_today.order_numbers + order_numbers))
            existing_unpaid_today.order_numbers = all_order_numbers
            existing_unpaid_today.total_order_amount += total_amount
            existing_unpaid_today.commission_amount += commission_amount
            existing_unpaid_today.payment_due_date = payment_due_date
            existing_unpaid_today.auto_generated_after_payment = True
            existing_unpaid_today.save()
            return existing_unpaid_today
        else:
            # Create new commission record for next month
            next_commission = DealerCommission.objects.create(
                dealer=dealer,
                order_numbers=order_numbers,
                total_order_amount=total_amount,
                commission_amount=commission_amount,
                calculation_date=start_date,
                payment_due_date=payment_due_date,
                status='Unpaid',
                auto_generated_after_payment=True  # Mark as auto-generated
            )
            return next_commission

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_commission_payment(request):
    """Submit payment details for a commission"""
    try:
        dealer = DealerProfile.objects.get(auth_id=request.user)

        # Add context for validation
        serializer = SubmitCommissionPaymentSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            payment_transaction = serializer.save()

            # Update payment reference in commission
            commission = payment_transaction.commission
            commission.payment_reference = payment_transaction.transaction_id
            commission.status = 'Unpaid'  # Set to Unpaid until admin verification
            commission.save()

            response_serializer = CommissionPaymentTransactionSerializer(payment_transaction)
            return Response({
                'message': 'Commission payment details submitted successfully. Awaiting admin verification.',
                'payment_transaction': response_serializer.data,
                'status': 'pending_verification'
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except DealerProfile.DoesNotExist:
        return Response(
            {'error': 'Dealer profile not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUserCustom])
def verify_commission_payment(request, payment_id):
    """Admin endpoint to verify commission payment"""
    try:
        payment_transaction = get_object_or_404(CommissionPaymentTransaction, id=payment_id)
        action = request.data.get('action')  # 'approve' or 'reject'
        notes = request.data.get('notes', '')

        if action == 'approve':
            # Verify the payment
            payment_transaction.verified = True
            payment_transaction.notes = notes
            payment_transaction.save()

            # Update commission status
            commission = payment_transaction.commission
            commission.status = 'Paid'  # Change status to Paid after verification
            commission.save()

            return Response({
                'message': 'Payment verified successfully',
                'payment_transaction_id': payment_transaction.id,
                'status': 'verified'
            })

        elif action == 'reject':
            payment_transaction.notes = notes
            payment_transaction.save()

            # Update commission status
            commission = payment_transaction.commission
            commission.status = 'Rejected'
            commission.save()

            return Response({
                'message': 'Payment rejected',
                'payment_transaction_id': payment_transaction.id,
                'status': 'rejected'
            })

        else:
            return Response(
                {'error': 'Invalid action. Use "approve" or "reject"'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    except CommissionPaymentTransaction.DoesNotExist:
        return Response(
            {'error': 'Payment transaction not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUserCustom])
def get_all_payment_details(request):
    """Admin endpoint to retrieve all commission payment details with status, order, and dealer details"""
    try:
        payment_transactions = CommissionPaymentTransaction.objects.select_related('commission__dealer').all()
        payment_details = []

        for transaction in payment_transactions:
            commission = transaction.commission
            dealer = commission.dealer
            orders = Order.objects.filter(order_number__in=commission.order_numbers)
            order_details = [
                {
                    'order_number': order.order_number,
                    'status': order.status,
                    'total_amount': order.order_total,
                    'created_at': order.created_at
                } for order in orders
            ]

            payment_details.append({
                'id':transaction.id,
                'transaction_id': transaction.transaction_id,
                'amount': str(transaction.amount),
                'payment_method': transaction.payment_method,
                'payment_screenshot': transaction.payment_screenshot.url if transaction.payment_screenshot else None,
                'verified': transaction.verified,
                'notes': transaction.notes,
                'commission_status': commission.status,
                'dealer': {
                    'id': dealer.id,
                    'kt_id': dealer.kt_id,
                    'name': dealer.auth_id.full_name if dealer.auth_id else '',
                    'email': dealer.auth_id.email if dealer.auth_id else '',
                    'is_active': dealer.auth_id.is_active if dealer.auth_id else False
                },
                'order_details': order_details
            })

        return Response({
            'message': 'All commission payment details retrieved successfully.',
            'payment_transactions': payment_details
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {'error': f'An error occurred: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

