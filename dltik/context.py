
from django.conf import settings

def current_url(request):
    return {
        'curr_url': request.build_absolute_uri()
    }

def themes_context(request):
    return {
        'THEMES': getattr(settings, 'THEMES', [])
    }