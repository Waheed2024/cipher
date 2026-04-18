from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # Main Feed & Reading
    path('', views.home, name='home'),
    path('about/', views.about_view, name='about'),
    path('post/<slug:slug>/', views.post_detail, name='detail'),
    path('category/<slug:tag_slug>/', views.tag_filter, name='tag_filter'),
    
    # Creator & Profile
    path('profile/', views.profile_settings, name='profile'),
    path('write/', views.write_post, name='write'),
    path('post/<slug:slug>/edit/', views.edit_post, name='edit_post'),
    
    # Bookmarks & Library
    path('bookmark/<slug:slug>/', views.toggle_bookmark, name='toggle_bookmark'),
    path('library/', views.library, name='library'),
    
    # Search & Newsletter
    path('search/', views.search_perspectives, name='search'),
    path('search-suggestions/', views.search_suggestions, name='search_suggestions'),
    path('subscribe/', views.subscribe_newsletter, name='subscribe'),
    
    # Authentication
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # EXECUTIVE MODERATION HQ
    path('command-hq/', views.admin_dashboard, name='admin_dashboard'),
    path('post/<slug:slug>/delete/', views.delete_post, name='delete_post'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
]