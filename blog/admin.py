from django.contrib import admin
from .models import User, Post, Comment, Tag, Subscriber

# 1. THE USER MODEL
# We keep this standard so it inherits Django's built-in password management UI
admin.site.register(User)

# 2. THE POST MODEL
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    # This creates a clean table showing the title, author, and date side-by-side
    list_display = ('title', 'author', 'published_date')
    # Adds a search bar at the top to quickly find perspectives
    search_fields = ('title', 'content')
    # Adds a sidebar to filter by date or author
    list_filter = ('published_date', 'author')

# 3. THE SUBSCRIBER MODEL
@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_at')
    search_fields = ('email',)

# 4. THE COMMENT MODEL
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'created_at')
    list_filter = ('created_at',)

# 5. THE TAG MODEL
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')