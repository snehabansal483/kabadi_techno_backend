from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from accounts.models import DealerProfile
from order.models import Order, OrderProduct
from invoice.models import DealerCommission

class Command(BaseCommand):
    help = 'Generate next month commissions for dealers who paid within 30 days'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dealer-id',
            type=str,
            help='Generate for specific dealer (kt_id). If not provided, checks all dealers.',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force generation even if payment was overdue',
        )

    def handle(self, *args, **options):
        self.stdout.write('Checking for dealers eligible for next month commission generation...')

        # Get dealers to process
        if options['dealer_id']:
            try:
                dealers = [DealerProfile.objects.get(kt_id=options['dealer_id'])]
            except DealerProfile.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Dealer with kt_id {options["dealer_id"]} not found')
                )
                return
        else:
            dealers = DealerProfile.objects.filter(auth_id__is_active=True)

        commissions_generated = 0
        today = timezone.now().date()

        for dealer in dealers:
            # Find recently paid commissions (paid within last 7 days)
            recently_paid = DealerCommission.objects.filter(
                dealer=dealer,
                status='Paid',
                updated_at__date__gte=today - timedelta(days=7)
            ).order_by('-updated_at')

            if not recently_paid.exists():
                continue

            # Get the most recent paid commission
            last_paid = recently_paid.first()
            
            # Check if payment was within 30 days or if force flag is set
            payment_within_30_days = last_paid.days_until_due >= 0 or options['force']
            
            if not payment_within_30_days and not options['force']:
                self.stdout.write(
                    f'Skipping dealer {dealer.kt_id}: Payment was overdue'
                )
                continue

            # Check if we already generated next month commission for this dealer
            existing_next = DealerCommission.objects.filter(
                dealer=dealer,
                calculation_date=today,
                auto_generated_after_payment=True
            ).exists()

            if existing_next:
                self.stdout.write(
                    f'Next month commission already generated for dealer {dealer.kt_id}'
                )
                continue

            # Generate next month commission
            next_commission = self._generate_next_month_commission(dealer)
            
            if next_commission:
                commissions_generated += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Generated next month commission for dealer {dealer.kt_id}: '
                        f'Amount: {next_commission.commission_amount}, '
                        f'Orders: {len(next_commission.order_numbers)}'
                    )
                )
            else:
                self.stdout.write(
                    f'No new orders found for dealer {dealer.kt_id} - no commission generated'
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully generated {commissions_generated} next month commissions')
        )

    def _generate_next_month_commission(self, dealer):
        """
        Generate next month's commission for a dealer
        """
        # Calculate period for next month (look for recent orders not yet included)
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
            created_at__date__gte=start_date - timedelta(days=30),
            created_at__date__lte=start_date,
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
                auto_generated_after_payment=True
            )
            return next_commission
