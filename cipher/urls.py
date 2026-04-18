from django.contrib import admin
from django.urls import path, include
from django.conf import settings             # <-- ADD THIS
from django.conf.urls.static import static   # <-- ADD THIS

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls')), # Or whatever your blog include is called
]

# --- ADD THIS BLOCK AT THE BOTTOM ---
# This serves the media files locally while you are building the app
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)