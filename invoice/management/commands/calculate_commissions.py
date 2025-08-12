from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from accounts.models import DealerProfile
from order.models import Order, OrderProduct
from invoice.models import DealerCommission

class Command(BaseCommand):
    help = 'Calculate monthly commissions for all dealers'

    def add_arguments(self, parser):
        parser.add_argument(
            '--month',
            type=str,
            help='Calculate for specific month (YYYY-MM format). Default is current month.',
        )

    def handle(self, *args, **options):
        # Calculate the billing period (last 30 days from today or specified month)
        if options['month']:
            try:
                year, month = map(int, options['month'].split('-'))
                end_date = datetime(year, month, 1).date()
                start_date = end_date - timedelta(days=30)
            except ValueError:
                self.stdout.write(
                    self.style.ERROR('Invalid month format. Use YYYY-MM format.')
                )
                return
        else:
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=30)

        self.stdout.write(f'Calculating commissions for period: {start_date} to {end_date}')

        # Get all active dealers
        dealers = DealerProfile.objects.filter(auth_id__is_active=True)
        commissions_created = 0

        for dealer in dealers:
            # Check if commission already exists for this period
            existing_commission = DealerCommission.objects.filter(
                dealer=dealer,
                calculation_date=end_date
            ).first()

            # Get all orders for this dealer in the billing period
            orders = Order.objects.filter(
                dealer_id=dealer.id,
                created_at__date__gte=start_date,
                created_at__date__lte=end_date,
                is_ordered=True,
                status__in=['Confirmed', 'Completed']
            )

            if not orders.exists():
                self.stdout.write(f'No orders found for dealer {dealer.kt_id} in the period')
                continue

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

            if total_amount > 0:
                # Calculate 1% commission
                commission_amount = total_amount * Decimal('0.01')
                
                # Set payment due date (30 days from calculation)
                payment_due_date = end_date + timedelta(days=30)

                if existing_commission:
                    # Update existing commission record
                    old_amount = existing_commission.commission_amount
                    existing_commission.order_numbers = order_numbers
                    existing_commission.total_order_amount = total_amount
                    existing_commission.commission_amount = commission_amount
                    existing_commission.payment_due_date = payment_due_date
                    
                    # If commission amount increased, reset status to Unpaid
                    if commission_amount > old_amount:
                        existing_commission.status = 'Unpaid'
                        status_msg = " (status reset to Unpaid due to increased amount)"
                    else:
                        status_msg = ""
                    
                    existing_commission.save()
                    
                    commissions_created += 1
                    self.stdout.write(
                        f'Commission updated for dealer {dealer.kt_id}: '
                        f'Amount: {commission_amount}, Orders: {len(order_numbers)} '
                        f'(was {old_amount}){status_msg}'
                    )
                else:
                    # Create new commission record
                    commission = DealerCommission.objects.create(
                        dealer=dealer,
                        order_numbers=order_numbers,
                        total_order_amount=total_amount,
                        commission_amount=commission_amount,
                        calculation_date=end_date,
                        payment_due_date=payment_due_date,
                        status='Unpaid'
                    )

                    commissions_created += 1
                    self.stdout.write(
                        f'Commission created for dealer {dealer.kt_id}: '
                        f'Amount: {commission_amount}, Orders: {len(order_numbers)}'
                    )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully processed {commissions_created} commission records')
        )
