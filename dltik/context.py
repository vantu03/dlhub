from django.conf import settings

def themes_context(request):
    return {
        'THEMES': getattr(settings, 'THEMES', [])
    }