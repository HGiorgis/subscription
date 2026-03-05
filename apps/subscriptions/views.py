from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from datetime import timedelta
import stripe
import json

from .models import Plan, Subscription, Payment

# Set Stripe API key
stripe.api_key = settings.STRIPE_SECRET_KEY

def plan_list_view(request):
    """Display all available subscription plans"""
    plans = Plan.objects.filter(is_active=True)
    
    # Get current user's subscription if logged in
    current_subscription = None
    if request.user.is_authenticated:
        current_subscription = Subscription.objects.filter(
            user=request.user,
            status='active'
        ).first()
    
    context = {
        'plans': plans,
        'current_subscription': current_subscription,
    }
    return render(request, 'subscriptions/plans.html', context)

@login_required
def checkout_view(request, plan_id):
    """Handle checkout for a specific plan"""
    plan = get_object_or_404(Plan, id=plan_id, is_active=True)
    
    # Check if Stripe is configured
    if not settings.STRIPE_SECRET_KEY:
        messages.error(request, "Payment system is not configured.")
        return redirect('subscriptions:plans')
    
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    # Check if user already has active subscription
    if Subscription.objects.filter(user=request.user, status='active').exists():
        messages.warning(request, "You already have an active subscription.")
        return redirect('subscriptions:manage')
    
    # Handle free plans
    if plan.price == 0:
        return activate_free_plan(request, plan)
    
    try:
        # Create or get Stripe customer
        customer_id = request.user.profile.stripe_customer_id
        
        if not customer_id:
            customer = stripe.Customer.create(
                email=request.user.email,
                name=request.user.get_full_name() or request.user.username,
                metadata={'user_id': request.user.id}
            )
            customer_id = customer.id
            request.user.profile.stripe_customer_id = customer_id
            request.user.profile.save()
        
        success_url = request.build_absolute_uri(
            reverse('subscriptions:success')
        ) + '?session_id={CHECKOUT_SESSION_ID}'
        
        cancel_url = request.build_absolute_uri(reverse('subscriptions:cancel'))
        
        print(f"🔗 Success URL being sent to Stripe: {success_url}")
        
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
                'user_id': str(request.user.id),
                'plan_id': str(plan.id),
                'plan_name': plan.name
            }
        )
        
        print(f"✅ Checkout session created: {session.id}")
        print(f"✅ Checkout URL: {session.url}")
        
        return redirect(session.url, code=303)
        
    except stripe.error.StripeError as e:
        print(f"❌ Stripe error: {e}")
        messages.error(request, f"Payment error: {str(e)}")
        return redirect('subscriptions:plans')
    except Exception as e:
        print(f"❌ Error: {e}")
        messages.error(request, f"Error: {str(e)}")
        return redirect('subscriptions:plans')


def activate_free_plan(request, plan):
    """Activate free plan"""
    # Create subscription
    end_date = timezone.now() + timedelta(days=plan.duration_days)
    
    subscription = Subscription.objects.create(
        user=request.user,
        plan=plan,
        stripe_subscription_id=f"free_{request.user.id}_{plan.id}",
        stripe_customer_id=request.user.profile.stripe_customer_id or f"free_cus_{request.user.id}",
        status='active',
        start_date=timezone.now(),
        end_date=end_date
    )
    
    # Update user profile
    request.user.profile.subscription_status = 'premium'
    request.user.profile.stripe_subscription_id = subscription.stripe_subscription_id
    request.user.profile.subscription_end_date = end_date
    request.user.profile.save()
    
    messages.success(request, f"Successfully activated {plan.name} plan!")
    return redirect('subscriptions:success')

@login_required
def success_view(request):
    """Payment success page"""
    session_id = request.GET.get('session_id')
    plan_id = request.GET.get('plan_id')
    
    print(f"🔍 Success view called")
    print(f"🔍 Session ID from URL: {session_id}")
    print(f"🔍 Plan ID from URL: {plan_id}")
    
    # Check if this is a real session ID (not the placeholder)
    if session_id and session_id != '{CHECKOUT_SESSION_ID}':
        print(f"✅ Valid session ID detected: {session_id[:15]}...")
        
        try:
            # Retrieve the session from Stripe
            stripe.api_key = settings.STRIPE_SECRET_KEY
            session = stripe.checkout.Session.retrieve(session_id)
            
            print(f"✅ Session retrieved from Stripe")
            print(f"✅ Payment status: {session.payment_status}")
            print(f"✅ Session metadata: {session.metadata}")
            
            # Check if payment was successful
            if session.payment_status == 'paid' or session.payment_status == 'complete':
                # Get plan from metadata or URL
                if not plan_id and session.metadata:
                    plan_id = session.metadata.get('plan_id')
                
                if plan_id:
                    from .models import Plan, Subscription, Payment
                    from django.utils import timezone
                    from datetime import timedelta
                    
                    plan = Plan.objects.get(id=plan_id)
                    
                    # Check if subscription already exists
                    existing_sub = Subscription.objects.filter(
                        user=request.user,
                        plan=plan,
                        status='active'
                    ).first()
                    
                    if not existing_sub:
                        # Calculate end date
                        end_date = timezone.now() + timedelta(days=plan.duration_days)
                        
                        # Create subscription
                        subscription = Subscription.objects.create(
                            user=request.user,
                            plan=plan,
                            stripe_subscription_id=session.get('subscription', f'temp_{session.id[:8]}'),
                            stripe_customer_id=session.customer,
                            status='active',
                            start_date=timezone.now(),
                            end_date=end_date
                        )
                        
                        # Update user profile
                        profile = request.user.profile
                        profile.subscription_status = 'premium'
                        profile.stripe_subscription_id = subscription.stripe_subscription_id
                        profile.subscription_end_date = end_date
                        profile.save()
                        
                        # Create payment record
                        Payment.objects.create(
                            user=request.user,
                            subscription=subscription,
                            stripe_payment_intent_id=session.get('payment_intent', ''),
                            amount=plan.price,
                            status='succeeded',
                            description=f"Subscription to {plan.name} plan"
                        )
                        
                        messages.success(request, f"Successfully subscribed to {plan.name} plan!")
                        print(f"✅ Subscription created for user {request.user.username}")
                    else:
                        print(f"ℹ️ Subscription already exists")
                else:
                    print(f"❌ No plan_id found in request or metadata")
            else:
                print(f"❌ Payment not successful: {session.payment_status}")
                
        except Exception as e:
            print(f"❌ Error retrieving session: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"❌ Invalid session ID: {session_id}")
        print(f"   This is the Stripe placeholder - waiting for redirect with real ID")
    
    # Get the user's active subscription
    subscription = Subscription.objects.filter(
        user=request.user,
        status='active'
    ).first()
    
    context = {
        'subscription': subscription
    }
    return render(request, 'subscriptions/success.html', context)

@login_required
def cancel_view(request):
    """Payment cancelled page"""
    return render(request, 'subscriptions/cancel.html')

@login_required
def billing_history_view(request):
    """View payment history"""
    payments = Payment.objects.filter(user=request.user).select_related('subscription', 'subscription__plan')
    
    # Get active subscription
    active_subscription = Subscription.objects.filter(
        user=request.user,
        status='active'
    ).first()
    
    context = {
        'payments': payments,
        'active_subscription': active_subscription
    }
    return render(request, 'subscriptions/billing_history.html', context)

@login_required
def subscription_manage_view(request):
    """Manage current subscription"""
    subscription = Subscription.objects.filter(
        user=request.user,
        status='active'
    ).first()
    
    if not subscription:
        messages.info(request, "You don't have an active subscription.")
        return redirect('subscriptions:plans')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'cancel':
            try:
                # Cancel in Stripe
                stripe.Subscription.modify(
                    subscription.stripe_subscription_id,
                    cancel_at_period_end=True
                )
                
                # Update local
                subscription.cancel_at_period_end = True
                subscription.save()
                
                # Update profile
                request.user.profile.subscription_status = 'cancelled'
                request.user.profile.save()
                
                messages.success(request, "Your subscription has been cancelled. It will end at the current period.")
            except Exception as e:
                messages.error(request, f"Error cancelling subscription: {str(e)}")
            
            return redirect('subscriptions:billing_history')
    
    context = {
        'subscription': subscription,
        'days_left': subscription.days_remaining(),
    }
    return render(request, 'subscriptions/manage.html', context)

@login_required
def invoice_view(request, payment_id):
    """View/download invoice"""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    if payment.invoice_pdf:
        return redirect(payment.invoice_pdf)
    else:
        messages.info(request, "Invoice PDF is not available yet.")
        return redirect('subscriptions:billing_history')
@csrf_exempt
def stripe_webhook_view(request):
    """Handle Stripe webhooks"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET
    
    print(f"📨 Webhook received at {request.build_absolute_uri()}")
    print(f"🔍 Signature header exists: {bool(sig_header)}")
    print(f"🔑 Webhook secret exists: {bool(webhook_secret)}")
    
    if not webhook_secret:
        print("❌ Webhook secret not configured!")
        return HttpResponse("Webhook secret not configured", status=500)
    
    try:
        # Verify the webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
        print(f"✅ Webhook verified: {event['type']}")
        
    except ValueError as e:
        print(f"❌ Invalid payload: {e}")
        return HttpResponse(f"Invalid payload: {e}", status=400)
    except stripe.error.SignatureVerificationError as e:
        print(f"❌ Invalid signature: {e}")
        return HttpResponse(f"Invalid signature: {e}", status=400)
    
    # Handle specific event types
    event_type = event['type']
    event_data = event['data']['object']
    
    print(f"🔄 Processing event: {event_type}")
    
    if event_type == 'checkout.session.completed':
        # Handle successful checkout
        session = event_data
        print(f"💰 Checkout completed: {session.get('id')}")
        print(f"   Customer: {session.get('customer')}")
        print(f"   Amount: {session.get('amount_total')}")
        
        # Your logic here...
        
    elif event_type == 'customer.subscription.updated':
        subscription = event_data
        print(f"🔄 Subscription updated: {subscription.get('id')}")
        print(f"   Status: {subscription.get('status')}")
        
    elif event_type == 'customer.subscription.deleted':
        subscription = event_data
        print(f"❌ Subscription deleted: {subscription.get('id')}")
        
    elif event_type == 'invoice.paid':
        invoice = event_data
        print(f"💰 Invoice paid: {invoice.get('id')}")
        print(f"   Amount: {invoice.get('amount_paid')}")
        
    elif event_type == 'invoice.payment_failed':
        invoice = event_data
        print(f"⚠️ Invoice payment failed: {invoice.get('id')}")
        
    elif event_type in ['product.created', 'price.created']:
        # Just acknowledge these events
        print(f"✅ {event_type} - acknowledged")
        
    else:
        print(f"ℹ️ Unhandled event type: {event_type}")
    
    # Always return 200 to acknowledge receipt
    return HttpResponse("Webhook received", status=200)

