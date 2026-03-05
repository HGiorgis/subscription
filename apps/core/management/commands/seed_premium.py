from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
from core.models import PremiumCategory, PremiumItem
import os
import random
from pathlib import Path

class Command(BaseCommand):
    help = 'Seed premium content with real media files'

    def handle(self, *args, **options):
        self.stdout.write('Creating premium categories...')
        
        # Create categories
        categories = [
            {
                'name': 'Video Tutorials',
                'slug': 'video-tutorials',
                'description': 'Professional video tutorials to master our platform',
                'icon': 'fa-video',
                'color': 'primary',
                'min_access_level': 'free',
                'order': 1
            },
            {
                'name': 'PDF Guides & E-Books',
                'slug': 'pdf-guides',
                'description': 'In-depth PDF guides and e-books from industry experts',
                'icon': 'fa-book',
                'color': 'success',
                'min_access_level': 'pro',
                'order': 2
            },
            {
                'name': 'Code Libraries',
                'slug': 'code-libraries',
                'description': 'Ready-to-use code snippets and libraries',
                'icon': 'fa-code',
                'color': 'info',
                'min_access_level': 'pro',
                'order': 3
            },
            {
                'name': 'Premium Templates',
                'slug': 'premium-templates',
                'description': 'Professional templates for rapid development',
                'icon': 'fa-paintbrush',
                'color': 'warning',
                'min_access_level': 'business',
                'order': 4
            },
            {
                'name': 'Development Tools',
                'slug': 'dev-tools',
                'description': 'Custom tools and utilities for developers',
                'icon': 'fa-toolbox',
                'color': 'danger',
                'min_access_level': 'business',
                'order': 5
            },
            {
                'name': 'Free Resources',
                'slug': 'free-resources',
                'description': 'Free resources for everyone',
                'icon': 'fa-gift',
                'color': 'secondary',
                'min_access_level': 'free',
                'order': 6
            },
        ]
        
        for cat_data in categories:
            cat, created = PremiumCategory.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            self.stdout.write(f"  {'✅' if created else '⏭️'}  {cat.name}")
        
        # Get base media path
        media_root = Path(settings.MEDIA_ROOT)
        
        # ===== VIDEO TUTORIALS =====
        self.stdout.write('\n📹 Creating Video Tutorials...')
        video_cat = PremiumCategory.objects.get(slug='video-tutorials')
        
        # Find video files
        video_dir = media_root / 'premium' / 'videos'
        video_files = list(video_dir.glob('*.mp4')) if video_dir.exists() else []
        
        videos = [
            {
                'title': 'Getting Started with Our Platform',
                'slug': 'getting-started-video',
                'description': 'A complete beginner\'s guide to our platform',
                'content': '''
                    <h2>Welcome to Our Platform!</h2>
                    <p>In this comprehensive tutorial, you'll learn:</p>
                    <ul>
                        <li>Setting up your account</li>
                        <li>Navigating the dashboard</li>
                        <li>Creating your first project</li>
                        <li>Basic configuration tips</li>
                    </ul>
                    <p>Watch the video below to get started quickly!</p>
                ''',
                'content_type': 'video',
                'video_duration': '12:30',
                'required_plan': 'free',
                'is_featured': True,
            },
            {
                'title': 'Advanced Features Masterclass',
                'slug': 'advanced-features-masterclass',
                'description': 'Take your skills to the next level',
                'content': '''
                    <h2>Master Advanced Features</h2>
                    <p>This advanced tutorial covers:</p>
                    <ul>
                        <li>Advanced configuration options</li>
                        <li>Performance optimization</li>
                        <li>Custom integrations</li>
                        <li>Best practices from experts</li>
                    </ul>
                ''',
                'content_type': 'video',
                'video_duration': '45:20',
                'required_plan': 'pro',
                'is_featured': True,
            },
        ]
        
        for i, video_data in enumerate(videos):
            # Get file size if we have a video file
            file_size = None
            video_file_path = None
            
            if i < len(video_files):
                video_file_path = video_files[i]
                file_stats = os.stat(video_file_path)
                file_size_mb = file_stats.st_size / (1024 * 1024)
                file_size = f"{file_size_mb:.1f} MB"
            
            # Create or update item
            item, created = PremiumItem.objects.get_or_create(
                slug=video_data['slug'],
                defaults={
                    'category': video_cat,
                    'content_type': video_data['content_type'],
                    'title': video_data['title'],
                    'description': video_data['description'],
                    'content': video_data['content'],
                    'video_duration': video_data['video_duration'],
                    'file_size': file_size,
                    'required_plan': video_data['required_plan'],
                    'is_featured': video_data['is_featured'],
                }
            )
            
            # Attach video file if exists and not already attached
            if video_file_path and not item.video_file:
                with open(video_file_path, 'rb') as f:
                    filename = os.path.basename(video_file_path)
                    item.video_file.save(filename, File(f), save=True)
                self.stdout.write(f"  ✅ Attached video: {filename}")
            
            self.stdout.write(f"  {'✅' if created else '⏭️'}  {item.title} ({item.file_size or 'No file'})")
        
        # ===== PDF GUIDES =====
        self.stdout.write('\n📚 Creating PDF Guides...')
        pdf_cat = PremiumCategory.objects.get(slug='pdf-guides')
        
        # Find PDF files
        pdf_dir = media_root / 'premium' / 'pdfs'
        pdf_files = list(pdf_dir.glob('*.pdf')) if pdf_dir.exists() else []
        pdf_files.extend(pdf_dir.glob('*.PDF'))  # Also check for uppercase
        
        pdfs = [
            {
                'title': 'Complete Django Guide 2024',
                'slug': 'complete-django-guide',
                'description': '300+ pages of Django best practices',
                'content': '''
                    <h2>Master Django Development</h2>
                    <p>This comprehensive guide includes:</p>
                    <ul>
                        <li>Django fundamentals</li>
                        <li>Advanced models and queries</li>
                        <li>REST API development</li>
                        <li>Deployment strategies</li>
                        <li>Security best practices</li>
                    </ul>
                    <p>Download the PDF to get instant access!</p>
                ''',
                'content_type': 'pdf',
                'required_plan': 'pro',
                'is_featured': True,
            },
            {
                'title': 'React & Django: The Ultimate Stack',
                'slug': 'react-django-ultimate',
                'description': 'Build full-stack applications',
                'content': '''
                    <h2>Full-Stack Development with React & Django</h2>
                    <p>Learn to build modern web applications with:</p>
                    <ul>
                        <li>React frontend development</li>
                        <li>Django REST Framework</li>
                        <li>Authentication with JWT</li>
                        <li>Real-time features with WebSockets</li>
                    </ul>
                ''',
                'content_type': 'pdf',
                'required_plan': 'business',
            },
            {
                'title': 'Python Best Practices Handbook',
                'slug': 'python-best-practices',
                'description': 'Write cleaner, more efficient Python code',
                'content': '''
                    <h2>Python Excellence</h2>
                    <p>Topics covered:</p>
                    <ul>
                        <li>Code organization</li>
                        <li>Design patterns</li>
                        <li>Testing strategies</li>
                        <li>Performance optimization</li>
                    </ul>
                ''',
                'content_type': 'pdf',
                'required_plan': 'free',
            },
        ]
        
        for i, pdf_data in enumerate(pdfs):
            # Get file size if we have a PDF file
            file_size = None
            pdf_file_path = None
            
            if i < len(pdf_files):
                pdf_file_path = pdf_files[i]
                file_stats = os.stat(pdf_file_path)
                file_size_mb = file_stats.st_size / (1024 * 1024)
                file_size = f"{file_size_mb:.1f} MB"
            
            # Create or update item
            item, created = PremiumItem.objects.get_or_create(
                slug=pdf_data['slug'],
                defaults={
                    'category': pdf_cat,
                    'content_type': pdf_data['content_type'],
                    'title': pdf_data['title'],
                    'description': pdf_data['description'],
                    'content': pdf_data['content'],
                    'file_size': file_size,
                    'required_plan': pdf_data['required_plan'],
                    'is_featured': pdf_data.get('is_featured', False),
                }
            )
            
            # Attach PDF file if exists and not already attached
            if pdf_file_path and not item.pdf_file:
                with open(pdf_file_path, 'rb') as f:
                    filename = os.path.basename(pdf_file_path)
                    item.pdf_file.save(filename, File(f), save=True)
                self.stdout.write(f"  ✅ Attached PDF: {filename}")
            
            self.stdout.write(f"  {'✅' if created else '⏭️'}  {item.title} ({item.file_size or 'No file'})")
        
        # ===== ICON PACK (using your icon images) =====
        self.stdout.write('\n🎁 Creating Icon Pack...')
        free_cat = PremiumCategory.objects.get(slug='free-resources')
        
        # Get icon files
        icon_dir = media_root / 'premium' / 'icon'
        icon_files = list(icon_dir.glob('*.png')) if icon_dir.exists() else []
        
        if icon_files:
            # Calculate total size
            total_size = sum(os.stat(f).st_size for f in icon_files)
            total_size_mb = total_size / (1024 * 1024)
            
            icon_names = [f.stem.replace('-', ' ').replace('_', ' ').title() for f in icon_files]
            icon_list_html = ''.join([f'<li>{name}</li>' for name in icon_names])
            
            icon_pack, created = PremiumItem.objects.get_or_create(
                slug='premium-icon-pack',
                defaults={
                    'category': free_cat,
                    'content_type': 'template',
                    'title': f'Premium Icon Pack ({len(icon_files)} Icons)',
                    'description': f'High-quality icons for your projects',
                    'content': f'''
                        <h2>Complete Icon Set</h2>
                        <p>Includes {len(icon_files)} professional icons:</p>
                        <ul>
                            {icon_list_html}
                        </ul>
                        <p>Perfect for web and mobile applications.</p>
                    ''',
                    'file_size': f'{total_size_mb:.1f} MB',
                    'required_plan': 'free',
                    'is_featured': True,
                }
            )
            self.stdout.write(f"  {'✅' if created else '⏭️'}  Icon Pack with {len(icon_files)} icons")
        
        # ===== THUMBNAILS FOR PREMIUM ITEMS =====
        self.stdout.write('\n🖼️ Adding Thumbnails...')
        thumb_dir = media_root / 'premium' / 'thumbnails'
        thumb_files = list(thumb_dir.glob('*.png')) + list(thumb_dir.glob('*.jpg')) if thumb_dir.exists() else []
        
        # Assign thumbnails to items
        items = PremiumItem.objects.all()
        for i, item in enumerate(items):
            if i < len(thumb_files) and not item.thumbnail:
                thumb_path = thumb_files[i]
                with open(thumb_path, 'rb') as f:
                    filename = os.path.basename(thumb_path)
                    item.thumbnail.save(filename, File(f), save=True)
                self.stdout.write(f"  ✅ Added thumbnail to: {item.title}")
        
        # ===== CODE LIBRARIES =====
        self.stdout.write('\n💻 Creating Code Libraries...')
        code_cat = PremiumCategory.objects.get(slug='code-libraries')
        
        code_items = [
            {
                'title': 'Authentication Boilerplate',
                'slug': 'auth-boilerplate',
                'description': 'Complete authentication system with JWT',
                'content': '''
                    <h2>Ready-to-Use Authentication System</h2>
                    <p>Includes:</p>
                    <ul>
                        <li>JWT authentication</li>
                        <li>Social login integration</li>
                        <li>Password reset flow</li>
                        <li>Email verification</li>
                        <li>2FA implementation</li>
                    </ul>
                    <p>Compatible with Django 4.2+</p>
                ''',
                'content_type': 'code',
                'file_size': '2.3 MB',
                'required_plan': 'pro',
                'is_featured': True,
            },
            {
                'title': 'E-commerce Starter Kit',
                'slug': 'ecommerce-starter',
                'description': 'Complete e-commerce solution',
                'content': '''
                    <h2>Full E-commerce Implementation</h2>
                    <p>Features:</p>
                    <ul>
                        <li>Product management</li>
                        <li>Shopping cart</li>
                        <li>Payment integration</li>
                        <li>Order management</li>
                        <li>Admin dashboard</li>
                    </ul>
                ''',
                'content_type': 'code',
                'file_size': '5.7 MB',
                'required_plan': 'business',
            },
        ]
        
        for code_data in code_items:
            item, created = PremiumItem.objects.get_or_create(
                slug=code_data['slug'],
                defaults={
                    'category': code_cat,
                    'content_type': code_data['content_type'],
                    'title': code_data['title'],
                    'description': code_data['description'],
                    'content': code_data['content'],
                    'file_size': code_data['file_size'],
                    'required_plan': code_data['required_plan'],
                    'is_featured': code_data.get('is_featured', False),
                }
            )
            self.stdout.write(f"  {'✅' if created else '⏭️'}  {item.title}")
        
        # ===== TEMPLATES =====
        self.stdout.write('\n🎨 Creating Templates...')
        template_cat = PremiumCategory.objects.get(slug='premium-templates')
        
        templates = [
            {
                'title': 'Modern Admin Dashboard',
                'slug': 'modern-admin-dashboard',
                'description': 'Professional admin template with dark mode',
                'content': '''
                    <h2>Admin Dashboard Template</h2>
                    <p>Includes:</p>
                    <ul>
                        <li>5 color schemes</li>
                        <li>Dark/light mode</li>
                        <li>Charts and analytics</li>
                        <li>Responsive design</li>
                        <li>20+ pre-built pages</li>
                    </ul>
                ''',
                'content_type': 'template',
                'file_size': '4.2 MB',
                'required_plan': 'business',
                'is_featured': True,
            },
            {
                'title': 'Landing Page Collection',
                'slug': 'landing-page-collection',
                'description': '10 modern landing page templates',
                'content': '''
                    <h2>Conversion-Optimized Landing Pages</h2>
                    <p>Perfect for:</p>
                    <ul>
                        <li>SaaS products</li>
                        <li>Mobile apps</li>
                        <li>Course sales</li>
                        <li>Event registration</li>
                    </ul>
                ''',
                'content_type': 'template',
                'file_size': '3.8 MB',
                'required_plan': 'pro',
            },
        ]
        
        for template in templates:
            item, created = PremiumItem.objects.get_or_create(
                slug=template['slug'],
                defaults={
                    'category': template_cat,
                    'content_type': template['content_type'],
                    'title': template['title'],
                    'description': template['description'],
                    'content': template['content'],
                    'file_size': template['file_size'],
                    'required_plan': template['required_plan'],
                    'is_featured': template.get('is_featured', False),
                }
            )
            self.stdout.write(f"  {'✅' if created else '⏭️'}  {item.title}")
        
        # ===== DEVELOPMENT TOOLS =====
        self.stdout.write('\n🛠️ Creating Development Tools...')
        tool_cat = PremiumCategory.objects.get(slug='dev-tools')
        
        # Use images as tool previews
        image_dir = media_root / 'premium' / 'images'
        image_files = list(image_dir.glob('*.png')) if image_dir.exists() else []
        
        tools = [
            {
                'title': 'Database Optimization Tool',
                'slug': 'db-optimizer',
                'description': 'Analyze and optimize your database performance',
                'content': f'''
                    <h2>Database Performance Tool</h2>
                    <img src="/media/premium/images/{image_files[0].name if image_files else ''}" class="img-fluid mb-3" alt="Tool Preview">
                    <p>Features:</p>
                    <ul>
                        <li>Query analyzer</li>
                        <li>Index recommendations</li>
                        <li>Performance reports</li>
                        <li>Migration helper</li>
                    </ul>
                ''',
                'content_type': 'tool',
                'file_size': '8.1 MB',
                'required_plan': 'business',
            },
            {
                'title': 'API Testing Suite',
                'slug': 'api-tester',
                'description': 'Comprehensive API testing tool',
                'content': f'''
                    <h2>API Testing Made Easy</h2>
                    <img src="/media/premium/images/{image_files[1].name if len(image_files) > 1 else ''}" class="img-fluid mb-3" alt="Tool Preview">
                    <p>Includes:</p>
                    <ul>
                        <li>Request builder</li>
                        <li>Response analyzer</li>
                        <li>Load testing</li>
                        <li>Documentation generator</li>
                    </ul>
                ''',
                'content_type': 'tool',
                'file_size': '5.3 MB',
                'required_plan': 'business',
            },
        ]
        
        for tool in tools:
            item, created = PremiumItem.objects.get_or_create(
                slug=tool['slug'],
                defaults={
                    'category': tool_cat,
                    'content_type': tool['content_type'],
                    'title': tool['title'],
                    'description': tool['description'],
                    'content': tool['content'],
                    'file_size': tool['file_size'],
                    'required_plan': tool['required_plan'],
                }
            )
            self.stdout.write(f"  {'✅' if created else '⏭️'}  {item.title}")
        
        # Summary
        total_items = PremiumItem.objects.count()
        self.stdout.write(self.style.SUCCESS(f'\n✅ Premium content seeded successfully! Total items: {total_items}'))