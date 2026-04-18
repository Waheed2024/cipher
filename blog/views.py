from .forms import CipherRegistrationForm
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.mail import send_mail
from .models import Post, User, Comment, Tag, Subscriber
from django.utils.text import slugify
import uuid


# =========================================================
# SECTOR 1: THE MAIN FEED & FILTERS
# =========================================================

def home(request):
    """Loads the main editorial feed."""
    posts = Post.objects.all().order_by('-published_date')
    return render(request, 'blog/home.html', {'posts': posts})

def tag_filter(request, tag_slug):
    """Filters the feed by a specific clicked category/tag."""
    tag = get_object_or_404(Tag, slug=tag_slug)
    posts = Post.objects.filter(tags=tag).order_by('-published_date')
    
    return render(request, 'blog/home.html', {
        'posts': posts,
        'is_tag_page': True,
        'current_tag': tag
    })


# =========================================================
# SECTOR 2: READING & ENGAGEMENT
# =========================================================

def post_detail(request, slug):
    """Loads a specific document and handles new comment submissions."""
    post = get_object_or_404(Post, slug=slug)
    
    if request.method == 'POST' and request.user.is_authenticated:
        content = request.POST.get('content')
        if content:
            Comment.objects.create(post=post, author=request.user, content=content)
            messages.success(request, "PERSPECTIVE ADDED TO DISCUSSION.")
            return redirect('blog:detail', slug=slug)

    return render(request, 'blog/detail.html', {'post': post})


# =========================================================
# SECTOR 3: PERSONAL LIBRARY (BOOKMARKS)
# =========================================================

@login_required
def library(request):
    """Loads the user's saved perspectives."""
    posts = Post.objects.filter(bookmarks=request.user).order_by('-published_date')
    
    return render(request, 'blog/library.html', {
        'posts': posts,
        'is_bookmarks_page': True
    })

@login_required
def toggle_bookmark(request, slug):
    """Adds or removes a document from the user's library."""
    post = get_object_or_404(Post, slug=slug)
    
    if request.user in post.bookmarks.all():
        post.bookmarks.remove(request.user)
        messages.success(request, "DOCUMENT REMOVED FROM LIBRARY.")
    else:
        post.bookmarks.add(request.user)
        messages.success(request, "DOCUMENT SECURED IN LIBRARY.")
        
    return redirect(request.META.get('HTTP_REFERER', 'blog:home'))


# =========================================================
# SECTOR 4: OMNI-SEARCH & NEWSLETTER
# =========================================================

def search_perspectives(request):
    """The main search engine for full results."""
    query = request.GET.get('q', '')
    if query:
        posts = Post.objects.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct().order_by('-published_date')
    else:
        posts = Post.objects.none()

    return render(request, 'blog/home.html', {
        'posts': posts, 
        'search_query': query, 
        'is_search_page': True
    })

def search_suggestions(request):
    """The live API that powers the dropdown autocomplete menu."""
    query = request.GET.get('q', '')
    if query:
        posts = Post.objects.filter(
            Q(title__icontains=query) | 
            Q(tags__name__icontains=query)
        ).distinct()[:5]
        
        results = [{'title': post.title, 'url': f"/post/{post.slug}/"} for post in posts]
        return JsonResponse({'results': results})
    return JsonResponse({'results': []})

def subscribe_newsletter(request):
    """Saves a user's email to the manifest database OR loads the subscribe page."""
    
    # 1. If a form was submitted (like from the footer)
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            Subscriber.objects.get_or_create(email=email)
            messages.success(request, "YOU HAVE BEEN ADDED TO THE MANIFEST.")
        return redirect(request.META.get('HTTP_REFERER', 'blog:home'))
        
    # 2. If the user just clicked the Navbar link, render the page
    return render(request, 'blog/subscribe.html')

# =========================================================
# SECTOR 5: EXECUTIVE COMMAND HQ
# =========================================================

@login_required
def admin_dashboard(request):
    """The central hub for superusers to manage the platform."""
    if not request.user.is_superuser:
        messages.error(request, "ACCESS DENIED. CLEARANCE LEVEL INSUFFICIENT.")
        return redirect('blog:home')
    
    posts = Post.objects.all().order_by('-published_date')
    comments = Comment.objects.all().order_by('-created_at')
    
    return render(request, 'blog/admin_dashboard.html', {
        'posts': posts,
        'comments': comments
    })

@login_required
def delete_post(request, slug):
    """Permanently destroys a published document."""
    post = get_object_or_404(Post, slug=slug)
    
    if request.user.is_superuser or request.user == post.author:
        if request.method == 'POST':
            post.delete()
            messages.success(request, "DOCUMENT PERMANENTLY EXPUNGED.")
            return redirect('blog:admin_dashboard')
    else:
        messages.error(request, "ACCESS DENIED. INSUFFICIENT CLEARANCE.")
        
    return redirect('blog:detail', slug=slug)

@login_required
def delete_comment(request, comment_id):
    """Destroys an intercepted communication (comment)."""
    comment = get_object_or_404(Comment, id=comment_id)
    post_slug = comment.post.slug
    
    if request.user.is_superuser:
        if request.method == 'POST':
            comment.delete()
            messages.success(request, "COMMUNICATION EXPUNGED FROM RECORD.")
    else:
        messages.error(request, "ACCESS DENIED. INSUFFICIENT CLEARANCE.")
        
    if 'command-hq' in request.META.get('HTTP_REFERER', ''):
        return redirect('blog:admin_dashboard')
    return redirect('blog:detail', slug=post_slug)


# =========================================================
# SECTOR 6: THE PUBLISHING ENGINE (CREATE & UPDATE)
# =========================================================

@login_required
def write_post(request):
    """The frontend publishing engine for authorized users."""
    if not (request.user.is_superuser or getattr(request.user, 'is_author', False)):
        messages.error(request, "ACCESS DENIED. PUBLISHING CLEARANCE REQUIRED.")
        return redirect('blog:home')

    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        tags_string = request.POST.get('tags', '')
        cover_image = request.FILES.get('cover_image')

        if title and content:
            base_slug = slugify(title)
            unique_slug = f"{base_slug}-{str(uuid.uuid4())[:6]}"

            post = Post.objects.create(
                title=title, slug=unique_slug, content=content,
                author=request.user, cover_image=cover_image
            )

            if tags_string:
                tag_names = [t.strip() for t in tags_string.split(',') if t.strip()]
                for tag_name in tag_names:
                    tag_slug = slugify(tag_name)
                    tag, created = Tag.objects.get_or_create(
                        slug=tag_slug,
                        defaults={'name': tag_name.upper()}
                    )
                    post.tags.add(tag)

            messages.success(request, "DOCUMENT SECURELY PUBLISHED TO THE FEED.")
            return redirect('blog:detail', slug=post.slug)
        else:
            messages.error(request, "SYSTEM ERROR: TITLE AND CONTENT ARE REQUIRED.")

    return render(request, 'blog/write.html')

@login_required
def edit_post(request, slug):
    """The frontend revision engine for existing documents."""
    post = get_object_or_404(Post, slug=slug)

    if not (request.user.is_superuser or request.user == post.author):
        messages.error(request, "ACCESS DENIED. INSUFFICIENT CLEARANCE TO MODIFY THIS DOCUMENT.")
        return redirect('blog:detail', slug=slug)

    if request.method == 'POST':
        post.title = request.POST.get('title')
        post.content = request.POST.get('content')
        tags_string = request.POST.get('tags', '')
        
        if request.FILES.get('cover_image'):
            post.cover_image = request.FILES.get('cover_image')

        if post.title and post.content:
            post.save() 

            if tags_string is not None:
                post.tags.clear() 
                tag_names = [t.strip() for t in tags_string.split(',') if t.strip()]
                for tag_name in tag_names:
                    tag_slug = slugify(tag_name)
                    tag, created = Tag.objects.get_or_create(
                        slug=tag_slug,
                        defaults={'name': tag_name.upper()}
                    )
                    post.tags.add(tag)

            messages.success(request, "DOCUMENT REVISIONS SECURELY LOGGED.")
            return redirect('blog:detail', slug=post.slug)
        else:
            messages.error(request, "SYSTEM ERROR: TITLE AND CONTENT ARE REQUIRED.")

    existing_tags = ", ".join([tag.name for tag in post.tags.all()])

    return render(request, 'blog/edit.html', {
        'post': post, 
        'existing_tags': existing_tags
    })


# =========================================================
# SECTOR 7: PLATFORM OPERATIONS (AUTH & PROFILE)
# =========================================================

def login_view(request):
    """Handles user authentication."""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"CONNECTION ESTABLISHED. WELCOME, {user.username.upper()}.")
            return redirect('blog:home')
        else:
            messages.error(request, "AUTHENTICATION FAILED. INVALID CREDENTIALS.")
    else:
        form = AuthenticationForm()
    return render(request, 'blog/login.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = CipherRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log the user in immediately so they don't have to sign in again
            login(request, user)
            return redirect('blog:home')
        # If it's NOT valid, the code skips to the bottom and 
        # re-renders the page with the errors attached to the form object
    else:
        form = CipherRegistrationForm()
    
    return render(request, 'blog/register.html', {'form': form})

def logout_view(request):
    """Safely terminates the user session."""
    if request.method == 'POST':
        logout(request)
        messages.success(request, "CONNECTION TERMINATED.")
    return redirect('blog:home')

@login_required
def profile_settings(request):
    """Manages user identity credentials and avatars."""
    if request.method == 'POST':
        user = request.user
        
        # Update core details
        user.username = request.POST.get('username', user.username)
        user.email = request.POST.get('email', user.email)
        
        # Safely handle bio if it exists on your custom User model
        if hasattr(user, 'bio'):
            user.bio = request.POST.get('bio', '')

        # Process Avatar Upload
        if request.FILES.get('avatar'):
            user.avatar = request.FILES.get('avatar')

        user.save()
        messages.success(request, "IDENTITY CREDENTIALS UPDATED.")
        return redirect('blog:profile')

    return render(request, 'blog/profile.html')

def about_view(request):
    """Loads the platform's manifesto and information page."""
    return render(request, 'blog/about.html')