from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from payment_gateway.models import DealerSubscription, SubscriptionNotification
from datetime import timedelta


class Command(BaseCommand):
    help = 'Check and expire subscriptions, send notifications'

    def add_arguments(self, parser):
        parser.add_argument(
            '--send-notifications',
            action='store_true',
            help='Send email notifications for expiring subscriptions',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )

    def handle(self, *args, **options):
        now = timezone.now()
        dry_run = options['dry_run']
        send_notifications = options['send_notifications']
        
        self.stdout.write(f"Running subscription management at {now}")
        
        # 1. Expire subscriptions that have passed their end date
        expired_subscriptions = DealerSubscription.objects.filter(
            status='active',
            end_date__lt=now
        )
        
        if expired_subscriptions.exists():
            self.stdout.write(
                f"Found {expired_subscriptions.count()} expired subscriptions"
            )
            
            if not dry_run:
                for subscription in expired_subscriptions:
                    subscription.expire_subscription()
                    self.stdout.write(
                        f"Expired subscription for dealer {subscription.dealer.kt_id}"
                    )
                    
                    # Create expiry notification
                    SubscriptionNotification.objects.create(
                        dealer=subscription.dealer,
                        subscription=subscription,
                        notification_type='expired',
                        message=f"Your {subscription.plan.name} subscription has expired. Please renew to continue accessing the marketplace."
                    )
            else:
                for subscription in expired_subscriptions:
                    self.stdout.write(
                        f"Would expire subscription for dealer {subscription.dealer.kt_id}"
                    )
        
        # 2. Find subscriptions expiring in 7 days and send warnings
        warning_date = now + timedelta(days=7)
        expiring_subscriptions = DealerSubscription.objects.filter(
            status='active',
            end_date__range=[now, warning_date]
        )
        
        if expiring_subscriptions.exists():
            self.stdout.write(
                f"Found {expiring_subscriptions.count()} subscriptions expiring within 7 days"
            )
            
            for subscription in expiring_subscriptions:
                # Check if warning already sent
                existing_notification = SubscriptionNotification.objects.filter(
                    dealer=subscription.dealer,
                    subscription=subscription,
                    notification_type='expiry_warning',
                    is_sent=True
                ).exists()
                
                if not existing_notification:
                    if not dry_run:
                        notification = SubscriptionNotification.objects.create(
                            dealer=subscription.dealer,
                            subscription=subscription,
                            notification_type='expiry_warning',
                            message=f"Your {subscription.plan.name} subscription expires on {subscription.end_date.date()}. Please renew to avoid marketplace access interruption."
                        )
                        
                        if send_notifications:
                            self.send_expiry_warning(subscription, notification)
                        
                        self.stdout.write(
                            f"Created expiry warning for dealer {subscription.dealer.kt_id}"
                        )
                    else:
                        self.stdout.write(
                            f"Would create expiry warning for dealer {subscription.dealer.kt_id}"
                        )
        
        # 3. Find subscriptions expiring in 1 day for final reminder
        final_warning_date = now + timedelta(days=1)
        final_expiring = DealerSubscription.objects.filter(
            status='active',
            end_date__range=[now, final_warning_date]
        )
        
        if final_expiring.exists():
            self.stdout.write(
                f"Found {final_expiring.count()} subscriptions expiring within 1 day"
            )
            
            for subscription in final_expiring:
                # Check if final reminder already sent
                existing_reminder = SubscriptionNotification.objects.filter(
                    dealer=subscription.dealer,
                    subscription=subscription,
                    notification_type='renewal_reminder',
                    is_sent=True
                ).exists()
                
                if not existing_reminder:
                    if not dry_run:
                        notification = SubscriptionNotification.objects.create(
                            dealer=subscription.dealer,
                            subscription=subscription,
                            notification_type='renewal_reminder',
                            message=f"URGENT: Your {subscription.plan.name} subscription expires tomorrow! Renew now to maintain marketplace access."
                        )
                        
                        if send_notifications:
                            self.send_renewal_reminder(subscription, notification)
                        
                        self.stdout.write(
                            f"Created renewal reminder for dealer {subscription.dealer.kt_id}"
                        )
                    else:
                        self.stdout.write(
                            f"Would create renewal reminder for dealer {subscription.dealer.kt_id}"
                        )
        
        self.stdout.write(
            self.style.SUCCESS('Subscription management completed successfully')
        )

    def send_expiry_warning(self, subscription, notification):
        """Send expiry warning email"""
        try:
            subject = 'Subscription Expiry Warning - Kabadi Techno'
            message = f"""
            Dear {subscription.dealer.auth_id.full_name},
            
            Your {subscription.plan.name} subscription is expiring soon!
            
            Subscription Details:
            - Plan: {subscription.plan.name}
            - Expires on: {subscription.end_date.date()}
            - Days remaining: {subscription.days_remaining}
            
            To continue accessing the marketplace, please renew your subscription.
            
            Best regards,
            Kabadi Techno Team
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[subscription.dealer.auth_id.email],
                fail_silently=False,
            )
            
            notification.is_sent = True
            notification.sent_at = timezone.now()
            notification.save()
            
            self.stdout.write(f"Sent expiry warning email to {subscription.dealer.auth_id.email}")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Failed to send email to {subscription.dealer.auth_id.email}: {str(e)}")
            )

    def send_renewal_reminder(self, subscription, notification):
        """Send renewal reminder email"""
        try:
            subject = 'URGENT: Subscription Expires Tomorrow - Kabadi Techno'
            message = f"""
            Dear {subscription.dealer.auth_id.full_name},
            
            This is an urgent reminder that your {subscription.plan.name} subscription expires tomorrow!
            
            Subscription Details:
            - Plan: {subscription.plan.name}
            - Expires on: {subscription.end_date.date()}
            - Hours remaining: {(subscription.end_date - timezone.now()).total_seconds() / 3600:.1f}
            
            IMPORTANT: If you don't renew before the expiry time, you will lose access to the marketplace.
            
            Please renew your subscription immediately to avoid any interruption.
            
            Best regards,
            Kabadi Techno Team
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[subscription.dealer.auth_id.email],
                fail_silently=False,
            )
            
            notification.is_sent = True
            notification.sent_at = timezone.now()
            notification.save()
            
            self.stdout.write(f"Sent renewal reminder email to {subscription.dealer.auth_id.email}")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Failed to send email to {subscription.dealer.auth_id.email}: {str(e)}")
            )
