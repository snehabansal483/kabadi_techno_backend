from django.core.management.base import BaseCommand
from django.utils import timezone
from payment_gateway.models import DealerSubscription


class Command(BaseCommand):
    help = 'Expire subscriptions that have passed their end_date'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be expired without actually expiring',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        
        # Find subscriptions that should be expired
        expired_subscriptions = DealerSubscription.objects.filter(
            status='active',
            end_date__lt=timezone.now()
        )
        
        count = expired_subscriptions.count()
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'DRY RUN: Would expire {count} subscriptions'
                )
            )
            
            if count > 0:
                self.stdout.write("Subscriptions that would be expired:")
                for subscription in expired_subscriptions:
                    self.stdout.write(
                        f"  - {subscription.dealer.kt_id}: {subscription.plan.name} "
                        f"(ended: {subscription.end_date})"
                    )
        else:
            if count == 0:
                self.stdout.write(
                    self.style.SUCCESS('No subscriptions to expire')
                )
            else:
                # Actually expire the subscriptions
                expired_subscriptions.update(status='expired')
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully expired {count} subscriptions'
                    )
                )
                
                # Log which subscriptions were expired
                for subscription in expired_subscriptions:
                    self.stdout.write(
                        f"  - Expired: {subscription.dealer.kt_id}: {subscription.plan.name}"
                    )
