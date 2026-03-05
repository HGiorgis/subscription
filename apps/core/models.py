from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class PremiumCategory(models.Model):
    """Categories for premium content"""
    
    # Define access levels as a class constant so it can be reused
    ACCESS_LEVELS = (
        ('free', 'Free Users'),
        ('pro', 'Pro Users'),
        ('business', 'Business Users'),
    )
    
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, default="fa-star")
    color = models.CharField(max_length=20, default="primary")
    
    # Use the class constant
    min_access_level = models.CharField(max_length=20, choices=ACCESS_LEVELS, default='free')
    
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = "Premium Categories"
    
    def __str__(self):
        return self.name

class PremiumItem(models.Model):
    """Individual premium items with rich media support"""
    
    CONTENT_TYPES = (
        ('article', 'Article'),
        ('video', 'Video Tutorial'),
        ('pdf', 'PDF Guide'),
        ('code', 'Code Bundle'),
        ('template', 'Template Pack'),
        ('tool', 'Software Tool'),
    )
    
    # Define access levels here as well (or reference the one from PremiumCategory)
    ACCESS_LEVELS = (
        ('free', 'Free Users'),
        ('pro', 'Pro Users'),
        ('business', 'Business Users'),
    )
    
    category = models.ForeignKey(PremiumCategory, on_delete=models.CASCADE, related_name='items')
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES, default='article')
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    content = models.TextField(help_text="Main content text", blank=True)
    
    # Media files
    thumbnail = models.ImageField(upload_to='premium/thumbnails/', null=True, blank=True)
    
    # Video content
    video_file = models.FileField(upload_to='premium/videos/', null=True, blank=True)
    video_url = models.URLField(blank=True, help_text="YouTube/Vimeo embed URL")
    video_duration = models.CharField(max_length=20, blank=True, help_text="e.g., '15:30'")
    
    # PDF/Download content
    pdf_file = models.FileField(upload_to='premium/pdfs/', null=True, blank=True)
    code_file = models.FileField(upload_to='premium/code/', null=True, blank=True)
    additional_files = models.JSONField(default=list, blank=True, help_text="List of additional file URLs")
    
    # File metadata
    file_size = models.CharField(max_length=20, blank=True, null=True)
    download_count = models.IntegerField(default=0)
    
    # Access control - Now using the defined ACCESS_LEVELS
    required_plan = models.CharField(max_length=20, choices=ACCESS_LEVELS, default='pro')
    
    # Metadata
    view_count = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_featured', '-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.get_content_type_display()})"
    
    def increment_views(self):
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    def increment_downloads(self):
        self.download_count += 1
        self.save(update_fields=['download_count'])
    
    def get_icon(self):
        icons = {
            'article': 'fa-file-lines',
            'video': 'fa-video',
            'pdf': 'fa-file-pdf',
            'code': 'fa-code',
            'template': 'fa-paintbrush',
            'tool': 'fa-toolbox',
        }
        return icons.get(self.content_type, 'fa-file')

class UserDownload(models.Model):
    """Track user downloads"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='downloads')
    item = models.ForeignKey(PremiumItem, on_delete=models.CASCADE)
    downloaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-downloaded_at']
    
    def __str__(self):
        return f"{self.user.username} downloaded {self.item.title}"

class UserProgress(models.Model):
    """Track user progress through videos/articles"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress')
    item = models.ForeignKey(PremiumItem, on_delete=models.CASCADE)
    progress_percent = models.IntegerField(default=0)
    last_position = models.CharField(max_length=20, blank=True, help_text="Video timestamp or page number")
    completed = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'item']
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.item.title}: {self.progress_percent}%"