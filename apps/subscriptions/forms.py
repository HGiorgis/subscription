from django import forms
from .models import Plan

class PlanForm(forms.ModelForm):
    """Form for creating/editing plans (admin only)"""
    class Meta:
        model = Plan
        fields = ['name', 'slug', 'description', 'price', 'stripe_price_id', 
                 'stripe_product_id', 'features', 'duration_days', 'is_active', 'is_popular']
        widgets = {
            'features': forms.Textarea(attrs={'rows': 5, 'placeholder': '{"feature1": "Description", "feature2": "Description"}'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }