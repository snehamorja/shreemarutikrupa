from core.models import BrandingSettings

def branding_context(request):
    """
    Context processor to make branding settings globally available across all templates.
    """
    try:
        settings = BrandingSettings.get_solo()
    except Exception:
        settings = None
    return {'branding': settings}
