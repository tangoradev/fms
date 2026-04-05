# Ajouter cet import au début du fichier views.py
from django.conf import settings

# Assurez-vous que les autres imports nécessaires sont présents :
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail

# Voici comment utiliser settings.EMAIL_HOST_USER dans la fonction demande_carte_carburant_create :

'''
for gestionnaire in gestionnaires:
    if gestionnaire.email:
        subject = f"Nouvelle demande de carte carburant #{demande.id_demande}"
        html_message = render_to_string('core/emails/nouvelle_demande_email.html', {
            'demande': demande,
            'gestionnaire': gestionnaire,
        })
        plain_message = strip_tags(html_message)
        from_email = settings.EMAIL_HOST_USER
        to = gestionnaire.email
        
        try:
            send_mail(subject, plain_message, from_email, [to], html_message=html_message)
            EmailLog.objects.create(
                sujet=subject,
                destinataire=to,
                contenu=plain_message,
                statut='Envoyé',
                date_envoi=timezone.now()
            )
        except Exception as e:
            EmailLog.objects.create(
                sujet=subject,
                destinataire=to,
                contenu=plain_message,
                statut='Échec',
                date_envoi=timezone.now(),
                erreur=str(e)
            )
'''
