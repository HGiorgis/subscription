from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import json

class Plan(models.Model):
    """Subscription plans available in the system"""
    
    BILLING_CYCLE_CHOICES = (
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    )
    
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Stripe fields
    stripe_price_id = models.CharField(max_length=100, blank=True, null=True)
    stripe_product_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Plan details
    billing_cycle = models.CharField(max_length=20, choices=BILLING_CYCLE_CHOICES, default='monthly')
    duration_days = models.IntegerField(default=30)
    
    # Status flags
    is_active = models.BooleanField(default=True)
    is_popular = models.BooleanField(default=False)
    
    # Features stored as JSON
    features = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['price']
    
    def __str__(self):
        return f"{self.name} - ${self.price}/{self.billing_cycle}"
    
    def get_features_list(self):
        if isinstance(self.features, str):
            return json.loads(self.features)
        return self.features

class Subscription(models.Model):
    """User subscriptions"""
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
        ('past_due', 'Past Due'),
        ('incomplete', 'Incomplete'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, related_name='subscriptions')
    
    # Stripe fields
    stripe_subscription_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    stripe_customer_id = models.CharField(max_length=100, blank=True)
    
    # Subscription details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='incomplete')
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    cancel_at_period_end = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.plan.name if self.plan else 'No Plan'}"
    
    def is_active(self):
        return self.status == 'active' and (not self.end_date or self.end_date > timezone.now())
    
    def days_remaining(self):
        if self.end_date:
            delta = self.end_date - timezone.now()
            return max(delta.days, 0)
        return 0
class Payment(models.Model):
    """Payment history"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    
    # Stripe fields - MAKE THESE OPTIONAL
    stripe_payment_intent_id = models.CharField(max_length=100, blank=True, null=True)  # Added null=True
    stripe_invoice_id = models.CharField(max_length=100, blank=True, null=True)  # Added null=True
    
    # Payment details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='usd')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Invoice
    invoice_url = models.URLField(blank=True, null=True)  # Added null=True
    invoice_pdf = models.URLField(blank=True, null=True)  # Added null=True
    
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment ${self.amount} - {self.status}"