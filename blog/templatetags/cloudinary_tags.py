from django import template

register = template.Library()

@register.filter
def cloudinary_transform(url, transforms='w_900,f_auto,q_auto'):
    """
    Insert Cloudinary URL transformations for responsive, optimised images.

    Usage in templates:
        {% load cloudinary_tags %}
        <img src="{{ post.cover_image.url|cloudinary_transform }}">

    For the hero (full-bleed large image):
        <img src="{{ post.cover_image.url|cloudinary_transform:'w_1400,f_auto,q_auto' }}">

    For thumbnails:
        <img src="{{ post.cover_image.url|cloudinary_transform:'w_600,f_auto,q_auto' }}">

    Transforms reference:
        w_900       — resize to 900px wide (height auto)
        f_auto      — serve WebP/AVIF automatically based on browser support
        q_auto      — Cloudinary picks the best quality/size trade-off automatically
        dpr_auto    — serve 2x on retina displays (optional, adds to size)
    """
    if not url or '/upload/' not in str(url):
        return url
    return str(url).replace('/upload/', f'/upload/{transforms}/', 1)