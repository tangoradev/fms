from django.core.mail import send_mail
from django.conf import settings

def test_send_mail():
    subject = 'Test Email Notification'
    message = 'Ceci est un test d\'envoi d\'email depuis FMS.'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = ['votre.email@exemple.com']  # Remplacez par votre adresse email de test
    try:
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        print('Email de test envoyé avec succès.')
    except Exception as e:
        print(f'Erreur lors de l\'envoi de l\'email : {e}')

if __name__ == '__main__':
    test_send_mail()
