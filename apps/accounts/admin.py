from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_subscription_status', 'is_staff')
    list_select_related = ('profile',)
    
    def get_subscription_status(self, instance):
        return instance.profile.subscription_status
    get_subscription_status.short_description = 'Subscription'
    get_subscription_status.admin_order_field = 'profile__subscription_status'
    
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'subscription_status', 'stripe_customer_id', 'created_at')
    list_filter = ('subscription_status', 'created_at')
    search_fields = ('user__username', 'user__email', 'stripe_customer_id')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'profile_picture', 'phone', 'address')
        }),
        ('Subscription Information', {
            'fields': ('subscription_status', 'stripe_customer_id', 'stripe_subscription_id', 'subscription_end_date')
        }),
        ('Metadata', {
            'fields': ('email_verified', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )