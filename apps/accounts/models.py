from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

class UserProfile(models.Model):
    SUBSCRIPTION_STATUS = (
        ('free', 'Free'),
        ('premium', 'Premium'),
        ('cancelled', 'Cancelled'),
        ('past_due', 'Past Due'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    
    # Subscription fields
    subscription_status = models.CharField(max_length=20, choices=SUBSCRIPTION_STATUS, default='free')
    stripe_customer_id = models.CharField(max_length=100, blank=True)
    stripe_subscription_id = models.CharField(max_length=100, blank=True)
    subscription_end_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def is_premium(self):
        return self.subscription_status == 'premium'
    
    # ADD THIS METHOD - Fixes the error
    def get_subscription_days_left(self):
        """Calculate days left in subscription"""
        if self.subscription_end_date:
            delta = self.subscription_end_date - timezone.now()
            return max(delta.days, 0)
        return 0

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()