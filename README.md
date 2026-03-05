# Subscription Showcase - Real SaaS Demo System

A complete subscription-based demo application with Stripe test mode integration, premium content access control, and user dashboard.

## 🚀 Live Demo Features

This is a **working demonstration** of a subscription SaaS platform. All payments are in **Stripe test mode** - no real money is charged.

### Core Functionality

- **3 Subscription Tiers**: Free, Pro ($19.99), Business ($49.99)
- **Stripe Test Payments**: Use `4242 4242 4242 4242` to "pay"
- **Premium Content Hub**: Videos, PDFs, code samples with plan-based access
- **User Dashboard**: Track subscription status, billing history, downloads
- **Subscription Management**: Upgrade, downgrade, cancel anytime

## ⚡ Quick Start (5 Minutes)

```bash
# 1. Clone and enter directory
git clone https://github.com/HGiorgis/subscription.git
cd subscription

# 2. Set up Python environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your Stripe test keys (see below)

# 5. Initialize database
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_plans --users 3
python manage.py seed_premium

# 6. Run server
python manage.py runserver
```

## 🔑 Stripe Test Mode Setup

1. Create free Stripe account: https://stripe.com
2. Go to https://dashboard.stripe.com/test/apikeys
3. Copy your test keys to `.env`:

```
STRIPE_PUBLIC_KEY=pk_test_YOUR_KEY_HERE
STRIPE_SECRET_KEY=sk_test_YOUR_KEY_HERE
STRIPE_WEBHOOK_SECRET=whsec_YOUR_SECRET  # Optional for local testing
```

## 🎯 Test the Full Flow

### 1. Browse as Guest

- Visit http://localhost:8000/premium/
- See locked premium content

### 2. Register/Login

- Create account at http://localhost:8000/accounts/register/
- Dashboard shows "Free Member"

### 3. Upgrade to Pro

- Go to http://localhost:8000/subscriptions/
- Choose "Pro" plan
- Pay with test card: `4242 4242 4242 4242`
  - Any future expiry (12/34)
  - Any CVC (123)
- Redirects to success page

### 4. Access Premium Content

- Visit http://localhost:8000/premium/
- Unlocked content appears
- Download PDFs, watch videos
- Track downloads in "My Downloads"

### 5. Manage Subscription

- View billing: http://localhost:8000/subscriptions/billing/
- Cancel or change plan: http://localhost:8000/subscriptions/manage/

## 📁 Key Files & Structure

```
subscription/
├── .env.example           # Template for environment variables
├── requirements.txt       # Python dependencies
├── manage.py             # Django management script
├── apps/
│   ├── accounts/         # User auth and profiles
│   ├── subscriptions/    # Plans, Stripe, payments
│   └── core/            # Premium content hub
├── templates/            # HTML templates
├── media/               # Uploaded content (videos, PDFs)
└── static/              # CSS, JS, images
```

## 🧪 Test Credentials

After seeding:

- **Test Users**: user1@example.com / password123
- **Admin**: Your created superuser

## 🐛 Common Issues

**Q: Payment doesn't create subscription?**
A: Ensure Stripe webhook is running: `stripe listen --forward-to localhost:8000/subscriptions/webhook/stripe/`

**Q: Can't see premium content after upgrade?**
A: Refresh the page or check billing history for successful payment.

**Q: Media files not showing?**
A: Run `python manage.py collectstatic` and ensure media files are in correct directories.

Update `.env` for production:

```
DEBUG=False
SECRET_KEY=your-secure-key
DATABASE_URL=postgres://user:pass@host/db
```

## 📝 License

MIT - Use freely for demonstrations and learning.

---

**Built with**: Django 5.2, Stripe API, Bootstrap 5, SQLite/PostgreSQL

_All payments are in Stripe test mode - no real transactions occur._
