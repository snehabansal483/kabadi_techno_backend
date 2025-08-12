from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from accounts.models import DealerProfile
from invoice.models import DealerCommission

class Command(BaseCommand):
    help = 'Deactivate dealers with overdue commission payments (30+ days)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show which dealers would be deactivated without actually deactivating them',
        )

    def handle(self, *args, **options):
        today = timezone.now().date()
        
        # Find all unpaid commissions that are overdue (payment_due_date < today)
        overdue_commissions = DealerCommission.objects.filter(
            status='Unpaid',
            payment_due_date__lt=today
        ).select_related('dealer__auth_id')

        if not overdue_commissions.exists():
            self.stdout.write(self.style.SUCCESS('No overdue commissions found.'))
            return

        # Group by dealer to get unique dealers with overdue payments
        overdue_dealers = {}
        for commission in overdue_commissions:
            dealer_id = commission.dealer.id
            if dealer_id not in overdue_dealers:
                overdue_dealers[dealer_id] = {
                    'dealer': commission.dealer,
                    'commissions': [],
                    'total_overdue': 0
                }
            overdue_dealers[dealer_id]['commissions'].append(commission)
            overdue_dealers[dealer_id]['total_overdue'] += commission.commission_amount

        deactivated_count = 0

        for dealer_data in overdue_dealers.values():
            dealer = dealer_data['dealer']
            commissions = dealer_data['commissions']
            total_overdue = dealer_data['total_overdue']
            
            # Check if dealer is still active
            if not dealer.auth_id.is_active:
                self.stdout.write(f'Dealer {dealer.kt_id} is already deactivated')
                continue

            if options['dry_run']:
                self.stdout.write(
                    f'[DRY RUN] Would deactivate dealer {dealer.kt_id} '
                    f'(Overdue amount: {total_overdue}, Overdue commissions: {len(commissions)})'
                )
            else:
                # Deactivate the dealer
                dealer.auth_id.is_active = False
                dealer.auth_id.save()
                
                deactivated_count += 1
                
                self.stdout.write(
                    f'Deactivated dealer {dealer.kt_id} '
                    f'(Overdue amount: {total_overdue}, Overdue commissions: {len(commissions)})'
                )
                
                # Log the overdue commission details
                for commission in commissions:
                    days_overdue = (today - commission.payment_due_date).days
                    self.stdout.write(
                        f'  - Commission from {commission.calculation_date}: '
                        f'{commission.commission_amount} ({days_overdue} days overdue)'
                    )

        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING(f'[DRY RUN] Would deactivate {len(overdue_dealers)} dealers')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully deactivated {deactivated_count} dealers')
            )
