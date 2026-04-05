# Script à copier/coller dans le shell Django
from django.core.mail import send_mail
from django.conf import settings

send_mail(
    'Test Email Notification',
    "Ceci est un test d'envoi d'email depuis FMS.",
    settings.DEFAULT_FROM_EMAIL,
    ['soungalo.tangora@undp.org'],
    fail_silently=False
)
print('Email de test envoyé à soungalo.tangora@undp.org')
