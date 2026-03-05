import stripe
from django.conf import settings

# Initialize Stripe with the secret key
if settings.STRIPE_SECRET_KEY:
    stripe.api_key = settings.STRIPE_SECRET_KEY
    print(f"✅ Stripe initialized (key ends with ...{settings.STRIPE_SECRET_KEY[-8:]})")
else:
    print("❌ WARNING: Stripe secret key not found!")