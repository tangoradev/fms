from django.conf import settings

def media_variables(request):
    """
    Ajoute les variables liées aux médias au contexte de tous les templates.
    """
    return {
        'MEDIA_URL': settings.MEDIA_URL,
        'STATIC_URL': settings.STATIC_URL,
    }
