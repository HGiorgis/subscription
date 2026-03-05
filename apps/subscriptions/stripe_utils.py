import stripe
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import Subscription, Payment
from accounts.models import UserProfile

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_checkout_session(user, plan, success_url, cancel_url):
    """Create a Stripe checkout session"""
    try:
        # Get or create Stripe customer
        customer_id = user.profile.stripe_customer_id
        
        if not customer_id:
            customer = stripe.Customer.create(
                email=user.email,
                name=user.get_full_name() or user.username,
                metadata={'user_id': user.id}
            )
            customer_id = customer.id
            user.profile.stripe_customer_id = customer_id
            user.profile.save()
        
        # Create checkout session
        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': plan.name,
                        'description': plan.description,
                    },
                    'unit_amount': int(plan.price * 100),
                    'recurring': {
                        'interval': 'month',
                    },
                },
                'quantity': 1,
            }],
            mode='subscription',
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                'user_id': user.id,
                'plan_id': plan.id,
                'plan_name': plan.name
            }
        )
        
        return session
        
    except stripe.error.StripeError as e:
        print(f"Stripe error: {e}")
        return None

def handle_successful_checkout(session):
    """Handle successful checkout from webhook"""
    try:
        # Get metadata
        user_id = session['metadata']['user_id']
        plan_id = session['metadata']['plan_id']
        subscription_id = session['subscription']
        customer_id = session['customer']
        
        # Get user and plan
        from django.contrib.auth import get_user_model
        from .models import Plan
        
        User = get_user_model()
        user = User.objects.get(id=user_id)
        plan = Plan.objects.get(id=plan_id)
        
        # Get subscription details from Stripe
        stripe_subscription = stripe.Subscription.retrieve(subscription_id)
        
        # Calculate end date
        current_period_end = datetime.fromtimestamp(stripe_subscription.current_period_end)
        end_date = timezone.make_aware(current_period_end)
        
        # Create subscription in database
        subscription = Subscription.objects.create(
            user=user,
            plan=plan,
            stripe_subscription_id=subscription_id,
            stripe_customer_id=customer_id,
            status='active',
            start_date=timezone.now(),
            end_date=end_date
        )
        
        # Update user profile
        profile = user.profile
        profile.subscription_status = 'premium'
        profile.stripe_subscription_id = subscription_id
        profile.subscription_end_date = end_date
        profile.save()
        
        # Create payment record
        Payment.objects.create(
            user=user,
            subscription=subscription,
            stripe_payment_intent_id=session.get('payment_intent', ''),
            amount=plan.price,
            status='succeeded',
            description=f"Subscription to {plan.name} plan"
        )
        
        print(f"✅ Successfully created subscription for {user.username}")
        
    except Exception as e:
        print(f"Error in handle_successful_checkout: {e}")

def handle_subscription_updated(event):
    """Handle subscription updates from Stripe"""
    try:
        stripe_sub = event['data']['object']
        
        # Find subscription in database
        subscription = Subscription.objects.get(
            stripe_subscription_id=stripe_sub['id']
        )
        
        # Update status
        status_map = {
            'active': 'active',
            'past_due': 'past_due',
            'canceled': 'cancelled',
            'incomplete': 'incomplete',
            'incomplete_expired': 'expired',
            'trialing': 'active'
        }
        
        new_status = status_map.get(stripe_sub['status'], 'active')
        subscription.status = new_status
        
        # Update end date
        if stripe_sub.get('current_period_end'):
            end_date = datetime.fromtimestamp(stripe_sub['current_period_end'])
            subscription.end_date = timezone.make_aware(end_date)
        
        subscription.save()
        
        # Update user profile
        profile = subscription.user.profile
        if new_status == 'active':
            profile.subscription_status = 'premium'
        elif new_status in ['cancelled', 'expired']:
            profile.subscription_status = 'cancelled'
        
        profile.subscription_end_date = subscription.end_date
        profile.save()
        
        print(f"✅ Updated subscription {stripe_sub['id']} to {new_status}")
        
    except Exception as e:
        print(f"Error in handle_subscription_updated: {e}")

def handle_invoice_paid(event):
    """Handle successful invoice payment"""
    try:
        invoice = event['data']['object']
        subscription_id = invoice['subscription']
        
        # Find subscription
        subscription = Subscription.objects.get(
            stripe_subscription_id=subscription_id
        )
        
        # Create payment record
        Payment.objects.create(
            user=subscription.user,
            subscription=subscription,
            stripe_payment_intent_id=invoice.get('payment_intent', ''),
            stripe_invoice_id=invoice['id'],
            amount=invoice['total'] / 100,
            status='succeeded',
            invoice_url=invoice.get('hosted_invoice_url', ''),
            invoice_pdf=invoice.get('invoice_pdf', ''),
            description=f"Subscription renewal - {invoice['date']}"
        )
        
        print(f"✅ Recorded payment for subscription {subscription_id}")
        
    except Exception as e:
        print(f"Error in handle_invoice_paid: {e}")

def cancel_subscription(subscription_id):
    """Cancel a subscription"""
    try:
        subscription = Subscription.objects.get(id=subscription_id)
        
        # Cancel in Stripe
        stripe.Subscription.modify(
            subscription.stripe_subscription_id,
            cancel_at_period_end=True
        )
        
        # Update local
        subscription.cancel_at_period_end = True
        subscription.save()
        
        # Update profile
        subscription.user.profile.subscription_status = 'cancelled'
        subscription.user.profile.save()
        
        return True
    except Exception as e:
        print(f"Error cancelling subscription: {e}")
        return False