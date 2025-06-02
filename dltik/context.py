from django.conf import settings


def global_settings(request):
    return {
        'BASE_URL': settings.BASE_URL,
        'DEBUG': settings.DEBUG,
        'RECAPTCHA_SITE_KEY': settings.RECAPTCHA_SITE_KEY,
        'THEMES': settings.THEMES,

        # Meta SEO
        'SITE_NAME': settings.SITE_NAME,
        'META_TITLE':settings.META_TITLE,
        'META_DESC': settings.META_DESC,
        'META_KEYWORDS': settings.META_KEYWORDS,

        # Google Analytics & Ads
        'GA_ID': settings.GA_ID,
        'GOOGLE_ADSENSE_CLIENT': settings.GOOGLE_ADSENSE_CLIENT,
        'GOOGLE_ADS_ID': settings.GOOGLE_ADS_ID,
        'GOOGLE_ADS_CONVERSION_1': settings.GOOGLE_ADS_CONVERSION_1,
        'GOOGLE_ADS_CONVERSION_2': settings.GOOGLE_ADS_CONVERSION_2,
    }
