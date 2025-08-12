from order.models import Order, OrderProduct  
from django.shortcuts import render
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.conf import settings
import os

# Commission-related imports
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .models import DealerCommission
from .serializers import DealerCommissionSerializer
from accounts.models import DealerProfile

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
        Mark a commission as paid
        """
        commission = self.get_object()
        commission.status = 'Paid'
        commission.save()
        
        return Response({
            'status': 'success',
            'message': f'Commission for dealer {commission.dealer.kt_id} marked as paid'
        })
    
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
            'commissions': DealerCommissionSerializer(commissions, many=True).data
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
    
    def _auto_update_commission(self, dealer):
        """
        Automatically update commission calculation for dealer with partial payment support
        """
        from datetime import timedelta
        
        # Calculate for last 30 days
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
        
        # Get all orders for this dealer in the period
        orders = Order.objects.filter(
            dealer_id=dealer.id,
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
            is_ordered=True,
            status__in=['Confirmed', 'Completed']
        )
        
        if not orders.exists():
            return
        
        # Check existing commission for today
        existing_commission = DealerCommission.objects.filter(
            dealer=dealer,
            calculation_date=end_date
        ).first()
        
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
            # There's already a commission for today
            # Check if there are new orders
            existing_orders = set(existing_commission.order_numbers)
            current_orders = set(order_numbers)
            new_orders = current_orders - existing_orders
            
            if new_orders:
                # There are new orders to add
                if existing_commission.status == 'Paid':
                    # If the existing commission is paid, we still update it with new orders
                    # This creates a new unpaid amount for the additional orders
                    existing_commission.order_numbers = order_numbers  # All orders
                    existing_commission.total_order_amount = total_amount  # Total amount
                    existing_commission.commission_amount = commission_amount  # Total commission
                    existing_commission.status = 'Unpaid'  # Reset to unpaid since new orders added
                    existing_commission.payment_due_date = payment_due_date
                    existing_commission.save()
                else:
                    # Update existing unpaid commission with all orders
                    existing_commission.order_numbers = order_numbers
                    existing_commission.total_order_amount = total_amount
                    existing_commission.commission_amount = commission_amount
                    existing_commission.payment_due_date = payment_due_date
                    existing_commission.save()
        else:
            # Create new commission record
            DealerCommission.objects.create(
                dealer=dealer,
                order_numbers=order_numbers,
                total_order_amount=total_amount,
                commission_amount=commission_amount,
                calculation_date=end_date,
                payment_due_date=payment_due_date,
                status='Unpaid'
            )

