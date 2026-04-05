from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
import logging
import os
from .models import Utilisateur, Service

# Configurer le logger pour les emails
logger = logging.getLogger('email_logger')
logger.setLevel(logging.INFO)

# Créer un gestionnaire de fichier pour les logs d'emails
log_dir = os.path.join(settings.BASE_DIR, 'logs')
os.makedirs(log_dir, exist_ok=True)
email_log_file = os.path.join(log_dir, 'email_logs.txt')

# Créer un gestionnaire de fichier
file_handler = logging.FileHandler(email_log_file)
file_handler.setLevel(logging.INFO)

# Créer un formateur
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Ajouter le gestionnaire au logger
logger.addHandler(file_handler)

def send_notification_email(subject, template_name, context, recipient_list):
    """
    Fonction utilitaire pour envoyer des emails de notification
    """
    # Rendre le contenu HTML à partir du template
    html_message = render_to_string(template_name, context)
    
    # Version texte brut du message
    plain_message = strip_tags(html_message)
    
    # Journaliser l'envoi d'email
    logger.info(f"Envoi d'email: Sujet: {subject}, Destinataires: {', '.join(recipient_list)}")
    
    try:
        # Envoi de l'email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Email envoyé avec succès: {subject}")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de l'email: {str(e)}")
        return False

def notify_fuel_managers_new_request(demande):
    """
    Envoie une notification aux gestionnaires carburant du service concerné
    lorsqu'une nouvelle demande de carte carburant est créée
    """
    # Récupérer le service de la demande
    service = demande.service
    
    # Récupérer tous les gestionnaires carburant de ce service
    gestionnaires = Utilisateur.objects.filter(
        service=service,
        groupe__nom_groupe='Gestionnaire Carburant'
    )
    
    # Si aucun gestionnaire n'est trouvé pour ce service, notifier tous les gestionnaires
    if not gestionnaires.exists():
        gestionnaires = Utilisateur.objects.filter(
            groupe__nom_groupe='Gestionnaire Carburant'
        )
    
    # Récupérer les emails des gestionnaires
    recipient_list = [g.email for g in gestionnaires if g.email]
    
    # Si aucun email n'est disponible, ne pas envoyer de notification
    if not recipient_list:
        return
    
    # Construire l'URL de la demande
    url = f"{settings.BASE_URL}{reverse('demande_carte_carburant_detail', kwargs={'pk': demande.id_demande})}"
    
    # Contexte pour le template d'email
    context = {
        'demande': demande,
        'chauffeur': demande.utilisateur_demandeur,
        'vehicule': demande.vehicule,
        'service': service,
        'url': url,
    }
    
    # Sujet de l'email
    subject = f"Nouvelle demande de carte de carburant - {demande.id_demande}"
    
    # Envoi de la notification
    send_notification_email(
        subject=subject,
        template_name='core/emails/new_request_notification.html',
        context=context,
        recipient_list=recipient_list
    )

def notify_driver_request_processed(demande):
    """
    Envoie une notification au chauffeur lorsque sa demande est traitée
    (acceptée ou rejetée) par un gestionnaire carburant
    """
    # Récupérer l'email du chauffeur
    recipient_email = demande.utilisateur_demandeur.email
    
    # Si aucun email n'est disponible, ne pas envoyer de notification
    if not recipient_email:
        return
    
    # Construire l'URL de la demande
    url = f"{settings.BASE_URL}{reverse('demande_carte_carburant_detail', kwargs={'pk': demande.id_demande})}"
    
    # Contexte pour le template d'email
    context = {
        'demande': demande,
        'gestionnaire': demande.utilisateur_traitant,
        'vehicule': demande.vehicule,
        'service': demande.service,
        'url': url,
        'statut': demande.statut_demande,
    }
    
    # Sujet de l'email
    if demande.statut_demande == 'Acceptée':
        subject = f"Demande de carte carburant acceptée - {demande.id_demande}"
        template_name = 'core/emails/request_accepted_notification.html'
    else:
        subject = f"Demande de carte carburant rejetée - {demande.id_demande}"
        template_name = 'core/emails/request_rejected_notification.html'
    
    # Envoi de la notification
    send_notification_email(
        subject=subject,
        template_name=template_name,
        context=context,
        recipient_list=[recipient_email]
    )

def notify_driver_principal_course(demande):
    """
    Notifie le Driver Principal du service associé à la demande de course.
    """
    service = demande.id_service
    driver_principal = service.utilisateur_set.filter(groupe__nom_groupe="Driver Principal").first()
    logger.info(f"[TRACE] notify_driver_principal_course: demande_id={getattr(demande, 'id', getattr(demande, 'pk', None))}, service={service.nom_service}, driver_principal={getattr(driver_principal, 'email', None)}")
    print(f"[PRINT] notify_driver_principal_course: demande_id={getattr(demande, 'id', getattr(demande, 'pk', None))}, service={service.nom_service}, driver_principal={getattr(driver_principal, 'email', None)}")
    if driver_principal and driver_principal.email:
        subject = "Nouvelle demande de course à traiter"
        context = {
            'driver_principal': driver_principal,
            'demande': demande,
            'service': service,
        }
        logger.info(f"[TRACE] Appel send_notification_email: to={driver_principal.email}, subject={subject}, demande_id={getattr(demande, 'id', getattr(demande, 'pk', None))}")
        print(f"[PRINT] Appel send_notification_email: to={driver_principal.email}, subject={subject}, demande_id={getattr(demande, 'id', getattr(demande, 'pk', None))}")
        try:
            send_notification_email(
                subject=subject,
                template_name='core/emails/nouvelle_demande_course.html',
                context=context,
                recipient_list=[driver_principal.email]
            )
            logger.info(f"[TRACE] Email envoyé avec succès au Driver Principal: {driver_principal.email} pour demande_id={getattr(demande, 'id', getattr(demande, 'pk', None))}")
            print(f"[PRINT] Email envoyé avec succès au Driver Principal: {driver_principal.email} pour demande_id={getattr(demande, 'id', getattr(demande, 'pk', None))}")
        except Exception as e:
            logger.error(f"[ERROR] Echec d'envoi email au Driver Principal: {driver_principal.email} pour demande_id={getattr(demande, 'id', getattr(demande, 'pk', None))} : {e}")
            print(f"[ERROR] Echec d'envoi email au Driver Principal: {driver_principal.email} pour demande_id={getattr(demande, 'id', getattr(demande, 'pk', None))} : {e}")

def notify_course_rejected(demande):
    """
    Notifie l'auteur de la demande en cas de rejet.
    """
    auteur = demande.id_auteur or demande.id_utilisateur
    if auteur and auteur.email:
        subject = "Votre demande de course a été rejetée"
        context = {
            'demande': demande,
            'auteur': auteur,
            'service': demande.id_service,
            'justification': demande.justification_rejet,
        }
        send_notification_email(
            subject=subject,
            template_name='core/emails/demande_course_rejetee.html',
            context=context,
            recipient_list=[auteur.email]
        )

def notify_course_affectation(demande, chauffeur, vehicule):
    """
    Notifie le chauffeur affecté et l'auteur de la demande après affectation.
    """
    auteur = demande.id_auteur or demande.id_utilisateur
    # Email au chauffeur
    if chauffeur and chauffeur.email:
        subject = "Vous avez été affecté à une course"
        context = {
            'demande': demande,
            'chauffeur': chauffeur,
            'vehicule': vehicule,
            'service': demande.id_service,
        }
        send_notification_email(
            subject=subject,
            template_name='core/emails/affectation_chauffeur_course.html',
            context=context,
            recipient_list=[chauffeur.email]
        )
    # Email à l'auteur
    if auteur and auteur.email:
        subject = "Votre demande de course a été planifiée"
        context = {
            'demande': demande,
            'chauffeur': chauffeur,
            'vehicule': vehicule,
            'service': demande.id_service,
        }
        send_notification_email(
            subject=subject,
            template_name='core/emails/affectation_auteur_course.html',
            context=context,
            recipient_list=[auteur.email]
        )

def get_french_month_name(month_number):
    """
    Retourne le nom du mois en français avec le bon encodage
    
    Args:
        month_number (int): Numéro du mois (1-12)
        
    Returns:
        str: Nom du mois en français
    """
    french_months = {
        1: 'Janvier',
        2: 'Février',
        3: 'Mars',
        4: 'Avril',
        5: 'Mai',
        6: 'Juin',
        7: 'Juillet',
        8: 'Août',
        9: 'Septembre',
        10: 'Octobre',
        11: 'Novembre',
        12: 'Décembre'
    }
    return french_months.get(month_number, '')

def generate_pdf_from_template(template_name, context, output_filename):
    """
    Génère un PDF à partir d'un template HTML.
    
    Args:
        template_name (str): Nom du template HTML à utiliser
        context (dict): Contexte à passer au template
        output_filename (str): Nom du fichier PDF à générer
        
    Returns:
        str: Chemin vers le fichier PDF généré
    """
    from django.template.loader import get_template
    from django.conf import settings
    from xhtml2pdf import pisa
    from io import BytesIO
    import os
    import base64
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # Par défaut, on n'utilise pas de logo
        context['logo_base64'] = ''
        
        # Tenter d'ajouter le logo PNUD en base64
        logo_path = os.path.join(settings.STATIC_ROOT, 'core/img/logo_pnud.jpg')
        logger.info(f"Recherche du logo à l'emplacement: {logo_path}")
        
        if os.path.exists(logo_path) and os.path.getsize(logo_path) > 0:
            try:
                with open(logo_path, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                    context['logo_base64'] = encoded_string
                    logger.info("Logo PNUD chargé avec succès")
            except Exception as e:
                logger.warning(f"Erreur lors du chargement du logo: {str(e)}")
        else:
            logger.warning(f"Logo PNUD non trouvé ou vide à l'emplacement: {logo_path}")
        
        # Générer le HTML
        template = get_template(template_name)
        html = template.render(context)
        
        # Créer le répertoire de sortie s'il n'existe pas
        output_dir = os.path.join(settings.MEDIA_ROOT, 'fiches_ravitaillement')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Chemin complet du fichier de sortie
        output_path = os.path.join(output_dir, output_filename)
        logger.info(f"Tentative de génération du PDF à: {output_path}")
        
        # Générer le PDF
        with open(output_path, "w+b") as result_file:
            pisa_status = pisa.CreatePDF(html, dest=result_file)
        
        # Retourner le chemin vers le fichier généré
        if pisa_status.err:
            logger.error(f"Erreur lors de la génération du PDF: {pisa_status.err}")
            return None
        
        logger.info(f"PDF généré avec succès: {output_path}")
        return output_path
    
    except Exception as e:
        logger.error(f"Exception lors de la génération du PDF: {str(e)}")
        return None
