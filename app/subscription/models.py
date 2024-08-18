from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save


class Subscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    usage_count = models.PositiveIntegerField(default=0)
    is_subscribed = models.BooleanField(default=False)
    stripe_checkout_id = models.CharField(max_length=500, blank=True, null=True)

    def can_use(self):
        return self.usage_count < 2 or self.is_subscribed

    def use(self):
        if (not self.is_subscribed) and self.usage_count < 2:
            self.usage_count += 1
            self.save()

@receiver(post_save, sender=User)
def create_user_subscription(sender, instance, created, **kwargs):
	if created:
		Subscription.objects.create(user=instance)
