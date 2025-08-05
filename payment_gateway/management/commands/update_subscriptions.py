from django.core.management.base import BaseCommand
from django.utils import timezone
from payment_gateway.models import DealerSubscription


class Command(BaseCommand):
    help = 'Update subscription statuses based on end dates'

    def handle(self, *args, **options):
        now = timezone.now()
        
        # Mark expired subscriptions
        expired_subscriptions = DealerSubscription.objects.filter(
            status='active',
            end_date__lt=now
        )
        
        expired_count = expired_subscriptions.update(status='expired')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully marked {expired_count} subscriptions as expired')
        )
        
        # Mark pending subscriptions as cancelled if they are too old (e.g., 7 days)
        old_pending = DealerSubscription.objects.filter(
            status='pending',
            created_at__lt=now - timezone.timedelta(days=7)
        )
        
        cancelled_count = old_pending.update(status='cancelled')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully cancelled {cancelled_count} old pending subscriptions')
        )
