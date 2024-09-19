from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save


class Subscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    credits = models.PositiveIntegerField(default=2)
    usage_count = models.PositiveIntegerField(default=0)
    is_subscribed = models.BooleanField(default=False)
    stripe_checkout_id = models.CharField(max_length=500, blank=True, null=True)
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)

    def can_use(self):
        return self.credits > 0 or self.is_subscribed

    def use(self):
        self.usage_count += 1
        if self.credits > 0:
              self.credits -= 1
        self.save()

@receiver(post_save, sender=User)
def create_user_subscription(sender, instance, created, **kwargs):
	if created:
		Subscription.objects.create(user=instance)
