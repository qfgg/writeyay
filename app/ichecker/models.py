from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class UserUsage(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    usage_count = models.PositiveIntegerField(default=0)
    subscription_expiry_date = models.DateTimeField(null=True, blank=True)

    def can_use(self):
        if self.usage_count < 2 or (self.subscription_expiry_date and self.subscription_expiry_date > timezone.now()):
            return True
        return False

    def use(self):
        if self.usage_count < 2:
            self.usage_count += 1
            self.save()

    def subscribe(self):
        self.subscription_expiry_date = timezone.now() + timedelta(days=30)
        self.usage_count = 2
        self.save()
