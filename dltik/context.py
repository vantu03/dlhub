from django.conf import settings

def global_settings(request):
    return {
        'BASE_URL': settings.BASE_URL,
        'DEBUG': settings.DEBUG,
        'RECAPTCHA_SITE_KEY': settings.RECAPTCHA_SITE_KEY,
        'THEMES': settings.THEMES,
        # Thêm biến nào bạn cần
    }
