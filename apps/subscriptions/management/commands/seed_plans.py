from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from subscriptions.models import Plan, Subscription, Payment
from django.utils import timezone
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'Seed database with 3 simple plans'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Clear existing data')
        parser.add_argument('--users', type=int, default=3, help='Number of sample users to create')

    def handle(self, *args, **options):
        if options['clear']:
            self.clear_data()
        
        self.create_plans()
        self.stdout.write(self.style.SUCCESS('✅ 3 plans created successfully!'))
        
        if options['users'] > 0:
            self.create_sample_users(options['users'])
            self.stdout.write(self.style.SUCCESS(f'✅ {options["users"]} sample users created!'))

    def clear_data(self):
        """Clear existing data"""
        self.stdout.write('Clearing existing data...')
        Plan.objects.all().delete()
        Subscription.objects.all().delete()
        Payment.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        self.stdout.write(self.style.SUCCESS('✅ Data cleared!'))

    def create_plans(self):
        """Create 3 simple subscription plans"""
        
        plans = [
            {
                'name': 'Free',
                'slug': 'free',
                'description': 'Perfect for getting started',
                'price': 0.00,
                'duration_days': 30,
                'is_active': True,
                'is_popular': False,
                'features': {
                    'projects': 'Up to 3 projects',
                    'storage': '100MB storage',
                    'support': 'Email support (48h)',
                    'team': '1 team member'
                }
            },
            {
                'name': 'Pro',
                'slug': 'pro',
                'description': 'For professionals and small teams',
                'price': 19.99,
                'duration_days': 30,
                'is_active': True,
                'is_popular': True,
                'features': {
                    'projects': 'Unlimited projects',
                    'storage': '50GB storage',
                    'support': 'Priority support (24h)',
                    'team': '5 team members',
                    'analytics': 'Advanced analytics',
                    'api': 'API access'
                }
            },
            {
                'name': 'Business',
                'slug': 'business',
                'description': 'For growing businesses',
                'price': 49.99,
                'duration_days': 30,
                'is_active': True,
                'is_popular': False,
                'features': {
                    'projects': 'Unlimited projects',
                    'storage': '200GB storage',
                    'support': '24/7 Priority support',
                    'team': 'Unlimited members',
                    'analytics': 'Advanced analytics',
                    'api': 'API access',
                    'custom': 'Custom branding',
                    'sla': '99.9% uptime SLA'
                }
            }
        ]

        for plan_data in plans:
            plan, created = Plan.objects.get_or_create(
                slug=plan_data['slug'],
                defaults=plan_data
            )
            if created:
                self.stdout.write(f"  ✅ Created plan: {plan.name}")
            else:
                self.stdout.write(f"  ⏭️  Plan already exists: {plan.name}")

    def create_sample_users(self, count):
        """Create sample users with random subscriptions"""
        
        plans = Plan.objects.filter(is_active=True)
        
        for i in range(count):
            username = f"user{i+1}"
            email = f"user{i+1}@example.com"
            
            # Create user
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': f"Test{i+1}",
                    'last_name': "User",
                    'is_active': True
                }
            )
            
            if created:
                user.set_password('password123')
                user.save()
                
                # Update profile
                profile = user.profile
                profile.phone = f"+1234567{i+1:03d}"
                profile.address = f"{i+1} Main Street, City, Country"
                profile.save()
                
                self.stdout.write(f"  ✅ Created user: {username}")
                
                # Randomly assign subscription (70% chance)
                if random.random() < 0.7:
                    plan = random.choice(plans)
                    self.create_sample_subscription(user, plan)
            else:
                self.stdout.write(f"  ⏭️  User already exists: {username}")

    def create_sample_subscription(self, user, plan):
        """Create a sample subscription for a user"""
        
        # Random start date within last 60 days
        start_date = timezone.now() - timedelta(days=random.randint(1, 60))
        end_date = start_date + timedelta(days=plan.duration_days)
        
        # Random status (mostly active)
        status = random.choices(
            ['active', 'active', 'cancelled', 'expired'],
            weights=[70, 70, 20, 10]
        )[0]
        
        # Create subscription
        subscription = Subscription.objects.create(
            user=user,
            plan=plan,
            stripe_subscription_id=f"sub_{user.id}_{plan.id}",
            stripe_customer_id=f"cus_{user.id}",
            status=status,
            start_date=start_date,
            end_date=end_date if status != 'active' else end_date,
            cancel_at_period_end=(status == 'cancelled')
        )
        
        # Update user profile if active
        if status == 'active':
            user.profile.subscription_status = 'premium'
            user.profile.stripe_subscription_id = subscription.stripe_subscription_id
            user.profile.subscription_end_date = end_date
            user.profile.save()
            
            # Create payment history
            self.create_sample_payments(user, subscription, plan)
        
        self.stdout.write(f"    📋 Created subscription: {user.username} -> {plan.name}")

    def create_sample_payments(self, user, subscription, plan):
        """Create 1-3 sample payments"""
        
        num_payments = random.randint(1, 3)
        
        for i in range(num_payments):
            payment_date = subscription.start_date + timedelta(days=30 * i)
            
            if payment_date > timezone.now():
                continue
            
            Payment.objects.create(
                user=user,
                subscription=subscription,
                stripe_payment_intent_id=f"pi_{user.id}_{i}",
                amount=plan.price,
                currency='usd',
                status='succeeded',
                description=f"{plan.name} plan - {payment_date.strftime('%B %Y')}",
                created_at=payment_date
            )