from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import DealerProfile
from .models import SubscriptionPlan, DealerSubscription


@receiver(post_save, sender=DealerProfile)
def create_trial_subscription(sender, instance, created, **kwargs):
    """
    Automatically create a 1-month trial subscription when a dealer profile is created
    """
    if created:
        try:
            # Get the trial plan
            trial_plan = SubscriptionPlan.objects.get(plan_type='trial')
            
            # Create trial subscription
            trial_subscription = DealerSubscription.objects.create(
                dealer=instance,
                plan=trial_plan,
                is_trial=True,
                status='active'
            )
            
            print(f"Trial subscription created for dealer {instance.kt_id}")
            
        except SubscriptionPlan.DoesNotExist:
            print(f"Trial plan not found. Please create a trial plan in admin.")
        except Exception as e:
            print(f"Error creating trial subscription for {instance.kt_id}: {str(e)}")
