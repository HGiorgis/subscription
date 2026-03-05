from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('', views.plan_list_view, name='plans'),
    path('checkout/<int:plan_id>/', views.checkout_view, name='checkout'),
    path('success/', views.success_view, name='success'),
    path('cancel/', views.cancel_view, name='cancel'),
    path('billing/', views.billing_history_view, name='billing_history'),
    path('manage/', views.subscription_manage_view, name='manage'),
    path('invoice/<int:payment_id>/', views.invoice_view, name='invoice'),
    path('webhook/stripe/', views.stripe_webhook_view, name='stripe_webhook'),
]