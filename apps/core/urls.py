from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('premium/', views.premium_hub_view, name='premium_hub'),
    path('category/<slug:slug>/', views.category_detail_view, name='category_detail'),
    path('category/<slug:category_slug>/<slug:item_slug>/', views.premium_item_detail_view, name='premium_item_detail'),
    path('download/<int:item_id>/', views.download_premium_item, name='download_item'),
    path('my-downloads/', views.my_downloads_view, name='my_downloads'),
    path('mark-complete/<int:item_id>/', views.mark_complete, name='mark_complete'),  
    path('health/', views.health_check, name='health_check'),
]