from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
import os

def is_staff(user):
    """
    Vérifie si l'utilisateur est un membre du staff
    """
    return user.is_staff

@login_required
@user_passes_test(is_staff)
def view_email_logs(request):
    """
    Vue pour afficher les logs d'emails
    Accessible uniquement par les membres du staff
    """
    log_file = os.path.join(settings.BASE_DIR, 'logs', 'email_logs.txt')
    
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            content = f.read()
    else:
        content = "Aucun log d'email disponible."
    
    return render(request, 'core/admin/email_logs.html', {
        'content': content,
        'title': 'Logs d\'emails',
    })
