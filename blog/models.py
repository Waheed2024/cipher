import math
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.html import strip_tags
from django.utils.text import slugify
from cloudinary.models import CloudinaryField

# =========================================================
# 1. CUSTOM IDENTITY MODEL
# =========================================================
class User(AbstractUser):
    """Overrides the default Django user to add custom platform clearance and UI elements."""
    avatar = CloudinaryField('avatar', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    is_author = models.BooleanField(default=False, help_text="Designates whether the user can publish to the feed.")

    def __str__(self):
        return self.username


# =========================================================
# 2. TAXONOMY ENGINE
# =========================================================
class Tag(models.Model):
    """Categorization architecture for filtering the Live Feed."""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# =========================================================
# 3. CORE EDITORIAL ENGINE
# =========================================================
class Post(models.Model):
    """The central document model for CIPHER publications."""
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    cover_image = models.ImageField(upload_to='covers/', null=True, blank=True)
    content = models.TextField()
    
    # Relationships
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
    bookmarks = models.ManyToManyField(User, blank=True, related_name='bookmarked_posts')
    
    # Metadata
    read_time = models.IntegerField(default=1)
    published_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """Intercepts the save protocol to auto-calculate exact reading time."""
        if self.content:
            # Strip out all HTML tags so we only count raw text
            plain_text = strip_tags(self.content)
            # Count the total number of words
            word_count = len(plain_text.split())
            # Divide by average reading speed (200 wpm) and round up
            minutes = math.ceil(word_count / 200.0)
            # Set the read time (ensure it is always at least 1 minute)
            self.read_time = max(1, minutes)
            
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


# =========================================================
# 4. GLOBAL COMMUNICATIONS
# =========================================================
class Comment(models.Model):
    """Records user perspectives attached to specific documents."""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Perspective by {self.author.username} on {self.post.title}"


# =========================================================
# 5. THE MANIFEST (NEWSLETTER)
# =========================================================
class Subscriber(models.Model):
    """Database of users opted into direct communications."""
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email