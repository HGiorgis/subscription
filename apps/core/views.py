from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import UserProgress, PremiumItem
from django.contrib import messages
from django.db import connections
from django.db.utils import OperationalError
import redis
from django.conf import settings
from django.http import HttpResponse
from .models import PremiumCategory, PremiumItem, UserDownload
from subscriptions.models import Subscription
import os



def health_check(request):
    """Health check endpoint for Docker/Render"""
    status = {
        'status': 'healthy',
        'database': 'ok',
        'redis': 'ok'
    }
    
    # Check database
    try:
        connections['default'].cursor().execute('SELECT 1')
    except OperationalError:
        status['database'] = 'error'
        status['status'] = 'unhealthy'
    
    # Check Redis
    try:
        redis_client = redis.from_url(settings.REDIS_URL)
        redis_client.ping()
    except:
        status['redis'] = 'error'
        status['status'] = 'unhealthy'
    
    http_status = 200 if status['status'] == 'healthy' else 500
    return JsonResponse(status, status=http_status)

def premium_hub_view(request):
    """Main premium resources hub"""
    categories = PremiumCategory.objects.all().prefetch_related('items')
    
    # Get featured items
    featured_items = PremiumItem.objects.filter(is_featured=True, is_active=True)[:6]
    
    # Get user's subscription status
    user_plan = 'free'
    if request.user.is_authenticated:
        subscription = Subscription.objects.filter(
            user=request.user,
            status='active'
        ).first()
        if subscription and subscription.plan:
            # Extract plan slug and clean it
            plan_slug = subscription.plan.slug.lower()
            if 'business' in plan_slug:
                user_plan = 'business'
            elif 'pro' in plan_slug:
                user_plan = 'pro'
            else:
                user_plan = 'free'
    
    context = {
        'categories': categories,
        'featured_items': featured_items,
        'user_plan': user_plan,
    }
    return render(request, 'core/premium_hub.html', context)

def category_detail_view(request, slug):
    """View items in a specific category"""
    category = get_object_or_404(PremiumCategory, slug=slug)
    items = category.items.filter(is_active=True)
    
    context = {
        'category': category,
        'items': items,
    }
    return render(request, 'core/category_detail.html', context)

def premium_item_detail_view(request, category_slug, item_slug):
    """View individual premium item"""
    item = get_object_or_404(
        PremiumItem, 
        slug=item_slug,
        category__slug=category_slug,
        is_active=True
    )
    
    # Check access
    user_plan = 'free'
    if request.user.is_authenticated:
        subscription = Subscription.objects.filter(
            user=request.user,
            status='active'
        ).first()
        if subscription and subscription.plan:
            plan_slug = subscription.plan.slug.lower()
            if 'business' in plan_slug:
                user_plan = 'business'
            elif 'pro' in plan_slug:
                user_plan = 'pro'
    
    # Check if user can access
    can_access = False
    if user_plan == 'business':
        can_access = True
    elif user_plan == 'pro' and item.required_plan in ['pro', 'free']:
        can_access = True
    elif user_plan == 'free' and item.required_plan == 'free':
        can_access = True
    
    if not can_access:
        messages.error(request, f"This content requires a {item.get_required_plan_display()} subscription.")
        return redirect('core:premium_hub')
    
    # Increment view count
    item.increment_views()
    
    # Get related items (excluding current item)
    related_items = PremiumItem.objects.filter(
        category=item.category,
        is_active=True
    ).exclude(id=item.id)[:3]  # Limit to 3 items
    
    context = {
        'item': item,
        'user_plan': user_plan,
        'related_items': related_items,  # Pass to template
    }
    return render(request, 'core/premium_item_detail.html', context)
@login_required
def download_premium_item(request, item_id):
    """Handle file downloads for premium items"""
    item = get_object_or_404(PremiumItem, id=item_id, is_active=True)
    
    # Check access (same logic as before)
    user_plan = 'free'
    subscription = Subscription.objects.filter(
        user=request.user,
        status='active'
    ).first()
    if subscription and subscription.plan:
        plan_slug = subscription.plan.slug.lower()
        if 'business' in plan_slug:
            user_plan = 'business'
        elif 'pro' in plan_slug:
            user_plan = 'pro'
    
    can_access = False
    if user_plan == 'business':
        can_access = True
    elif user_plan == 'pro' and item.required_plan in ['pro', 'free']:
        can_access = True
    elif user_plan == 'free' and item.required_plan == 'free':
        can_access = True
    
    if not can_access:
        messages.error(request, f"This download requires a {item.get_required_plan_display()} subscription.")
        return redirect('core:premium_hub')
    
    # Determine which file to serve
    file_type = request.GET.get('type', '')
    file_field = None
    filename = ""
    
    if file_type == 'pdf' and item.pdf_file:
        file_field = item.pdf_file
        filename = f"{item.slug}.pdf"
    elif file_type == 'video' and item.video_file:
        file_field = item.video_file
        filename = f"{item.slug}.mp4"
    elif file_type == 'code' and item.code_file:
        file_field = item.code_file
        filename = f"{item.slug}.zip"
    elif item.pdf_file:
        file_field = item.pdf_file
        filename = f"{item.slug}.pdf"
    elif item.video_file:
        file_field = item.video_file
        filename = f"{item.slug}.mp4"
    elif item.code_file:
        file_field = item.code_file
        filename = f"{item.slug}.zip"
    else:
        messages.error(request, "No file available for this item.")
        return redirect('core:premium_item_detail', category_slug=item.category.slug, item_slug=item.slug)
    
    # Record download
    UserDownload.objects.create(user=request.user, item=item)
    item.increment_downloads()
    
    # Serve file
    response = HttpResponse(file_field, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

def my_downloads_view(request):
    """View user's download history"""
    downloads = UserDownload.objects.filter(user=request.user).select_related('item', 'item__category')
    
    context = {
        'downloads': downloads,
    }
    return render(request, 'core/my_downloads.html', context)

@login_required
def mark_complete(request, item_id):
    """Mark a premium item as completed"""
    if request.method == 'POST':
        try:
            item = get_object_or_404(PremiumItem, id=item_id)
            
            # Get or create progress record
            progress, created = UserProgress.objects.get_or_create(
                user=request.user,
                item=item,
                defaults={
                    'progress_percent': 100,
                    'completed': True
                }
            )
            
            # If it exists but not completed, update it
            if not created and not progress.completed:
                progress.progress_percent = 100
                progress.completed = True
                progress.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Resource marked as complete!'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

