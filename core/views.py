from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect, FileResponse
from django.urls import reverse, reverse_lazy
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView, View
from django.contrib import messages
from django.db.models import Sum, F, Q, Count, Avg
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.db.models import Sum, Count, Q, F, Avg
from django.urls import reverse
from django.utils import timezone
from django.core.paginator import Paginator
from django.db import transaction
from django.conf import settings
from django.core.mail import send_mail
from django.utils.html import strip_tags
from core.utils import notify_driver_principal_course
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseServerError, FileResponse, Http404
from datetime import datetime, date, timedelta
from io import BytesIO
from xhtml2pdf import pisa
from .models import (
    Service, Groupe, Utilisateur, Vehicule, Carte_Carburant,
    Fournisseur, Achat_Stock_Carburant_HT, Achat_Carburant_TTC,
    Rechargement_Carte_Carburant_HT, Rechargement_Carte_Carburant_TTC, Demande_Carte_Carburant, EmailLog,
    TypeMaintenance, Maintenance, Planification, DemandeCourse, PlanificationCourse,
    VehiculeAffectation, VehiculeDocument
)
from .forms import (
    LoginForm, ServiceForm, GroupeForm, UtilisateurCreationForm, UtilisateurUpdateForm,
    VehiculeForm, CarteCarburantCreateForm, FournisseurForm, AchatStockCarburantHTForm,
    AchatCarburantTTCForm, RechargementCarteCarburantHTForm, RechargementCarteCarburantTTCForm, DemandeCarteCarburantCreateForm,
    DemandeCarteCarburantTraitementForm, DemandeCarteCarburantClotureForm, CarteCarburantForm,
    TypeMaintenanceForm, MaintenanceForm, PlanificationForm, DemandeCourseFormAmeliore, DemandeCourseTraitementForm,
    PlanificationCourseForm, VehiculeStatusForm, VehiculeAffectationForm, VehiculeDocumentForm
)
from .utils import notify_fuel_managers_new_request, notify_driver_request_processed, get_french_month_name, notify_driver_principal_course, notify_course_rejected, notify_course_affectation, generate_pdf_from_template
from .services import build_releve_consommation_context, close_demande, reject_demande, validate_demande
import json
import calendar
import xlsxwriter
import io

# Create your views here.

def home_view(request, template_name='core/home.html'):
    """
    Vue pour la page d'accueil
    Redirige les utilisateurs vers leur tableau de bord spécifique en fonction de leur rôle
    """
    context = {}  # Initialiser le contexte pour tous les cas
    
    # Si l'utilisateur est connecté, vérifier son rôle et le rediriger vers le tableau de bord approprié
    if request.user.is_authenticated:
        # Récupérer les groupes de l'utilisateur
        user_groupes = request.user.groupe.all().values_list('nom_groupe', flat=True)
        
        # Rediriger vers la page appropriée en fonction du rôle
        if 'Driver' in user_groupes:
            return redirect('demandes_carte_carburant_list')
        elif 'Gestionnaire Carburant' in user_groupes:
            return redirect('demandes_carte_carburant_list')
        
        # Pour les autres rôles, afficher le tableau de bord général
        # Statistiques pour le tableau de bord
        vehicules_count = Vehicule.objects.count()
        cartes_count = Carte_Carburant.objects.count()
        fournisseurs_count = Fournisseur.objects.count()
        achats_count = Achat_Carburant_TTC.objects.count() + Achat_Stock_Carburant_HT.objects.count()
        services_count = Service.objects.count()
        utilisateurs_count = Utilisateur.objects.count()
        
        # Récupérer les dernières activités (achats récents)
        recent_activities = []
        
        # Achats TTC récents
        achats_ttc = Achat_Carburant_TTC.objects.all().order_by('-date_achat')[:5]
        for achat in achats_ttc:
            recent_activities.append({
                'date': achat.date_achat,
                'type': 'achat_ttc',
                'get_type_display': 'Achat Carburant TTC',
                'description': f"Achat de {achat.volume} L de {achat.get_type_carburant_display()} chez {achat.fournisseur}",
                'user': request.user,  # À remplacer par l'utilisateur réel qui a effectué l'achat
            })
        
        # Achats HT récents
        achats_ht = Achat_Stock_Carburant_HT.objects.all().order_by('-date_achat')[:5]
        for achat in achats_ht:
            recent_activities.append({
                'date': achat.date_achat,
                'type': 'achat_ht',
                'get_type_display': 'Achat Stock Carburant HT',
                'description': f"Achat de {achat.volume} L de {achat.get_type_carburant_display()} chez {achat.fournisseur}",
                'user': request.user,  # À remplacer par l'utilisateur réel qui a effectué l'achat
            })
        
        # Trier les activités par date (les plus récentes d'abord)
        recent_activities.sort(key=lambda x: x['date'], reverse=True)
        recent_activities = recent_activities[:10]  # Limiter à 10 activités
        
        context = {
            'vehicules_count': vehicules_count,
            'cartes_count': cartes_count,
            'fournisseurs_count': fournisseurs_count,
            'achats_count': achats_count,
            'services_count': services_count,
            'utilisateurs_count': utilisateurs_count,
            'recent_activities': recent_activities,
        }
    
    return render(request, template_name, context)

@csrf_protect
def login_view(request):
    """
    Vue pour la page de connexion
    """
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        remember = request.POST.get('remember')
        
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Bienvenue, {user.get_full_name()} !')
            
            # Si "Se souvenir de moi" n'est pas coché, la session expire à la fermeture du navigateur
            if not remember:
                request.session.set_expiry(0)
                
            return redirect('home')
        else:
            messages.error(request, 'Email ou mot de passe incorrect.')
    
    return render(request, 'core/login.html')

def logout_view(request):
    """
    Vue pour la déconnexion
    """
    logout(request)
    messages.info(request, 'Vous avez été déconnecté avec succès.')
    return redirect('login')

@login_required
def profile_view(request):
    """
    Vue pour la page de profil utilisateur
    """
    return render(request, 'core/profile.html')

@login_required
def services_view(request):
    """
    Vue pour la liste des services
    """
    services = Service.objects.all().order_by('nom_service')
    return render(request, 'core/services.html', {'services': services})

@login_required
def service_edit(request, pk):
    """
    Vue pour modifier un service
    """
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, f'Le service {service.nom_service} a été modifié avec succès.')
            return redirect('services_view')
    else:
        form = ServiceForm(instance=service)
    
    return render(request, 'core/service_form.html', {
        'form': form,
        'service': service,
        'title': 'Modifier un service',
        'submit_text': 'Enregistrer',
    })

@login_required
def service_delete(request, pk):
    """
    Vue pour supprimer un service
    """
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        nom_service = service.nom_service
        service.delete()
        messages.success(request, f'Le service {nom_service} a été supprimé avec succès.')
        return redirect('services_view')
    
    return render(request, 'core/service_confirm_delete.html', {
        'service': service,
    })

@login_required
def service_create(request):
    """
    Vue pour créer un nouveau service
    """
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save()
            messages.success(request, f'Le service {service.nom_service} a été créé avec succès.')
            return redirect('services_view')
    else:
        form = ServiceForm()
    
    return render(request, 'core/service_form.html', {
        'form': form,
        'title': 'Ajouter un service',
        'submit_text': 'Ajouter',
    })

@login_required
def groupes_view(request):
    """
    Vue pour la liste des groupes
    """
    groupes = Groupe.objects.all().order_by('nom_groupe')
    return render(request, 'core/groupes.html', {'groupes': groupes})

@login_required
def groupe_create(request):
    """
    Vue pour créer un nouveau groupe
    """
    if request.method == 'POST':
        form = GroupeForm(request.POST)
        if form.is_valid():
            groupe = form.save()
            messages.success(request, f'Le groupe {groupe.nom_groupe} a été créé avec succès.')
            return redirect('groupes_view')
    else:
        form = GroupeForm()
    
    return render(request, 'core/groupe_form.html', {
        'form': form,
        'title': 'Ajouter un groupe',
        'submit_text': 'Ajouter',
    })

@login_required
def groupe_edit(request, pk):
    """
    Vue pour modifier un groupe
    """
    groupe = get_object_or_404(Groupe, pk=pk)
    if request.method == 'POST':
        form = GroupeForm(request.POST, instance=groupe)
        if form.is_valid():
            form.save()
            messages.success(request, f'Le groupe {groupe.nom_groupe} a été modifié avec succès.')
            return redirect('groupes_view')
    else:
        form = GroupeForm(instance=groupe)
    
    return render(request, 'core/groupe_form.html', {
        'form': form,
        'groupe': groupe,
        'title': 'Modifier un groupe',
        'submit_text': 'Enregistrer',
    })

@login_required
def groupe_delete(request, pk):
    """
    Vue pour supprimer un groupe
    """
    groupe = get_object_or_404(Groupe, pk=pk)
    if request.method == 'POST':
        nom_groupe = groupe.nom_groupe
        groupe.delete()
        messages.success(request, f'Le groupe {nom_groupe} a été supprimé avec succès.')
        return redirect('groupes_view')
    
    return render(request, 'core/groupe_confirm_delete.html', {
        'groupe': groupe,
    })

@login_required
def utilisateurs_view(request):
    """
    Vue pour la liste des utilisateurs
    """
    utilisateurs = Utilisateur.objects.all().order_by('nom_complet')
    return render(request, 'core/utilisateurs.html', {'utilisateurs': utilisateurs})

@login_required
def utilisateur_create(request):
    """
    Vue pour créer un nouvel utilisateur
    """
    if request.method == 'POST':
        form = UtilisateurCreationForm(request.POST)
        if form.is_valid():
            utilisateur = form.save()
            messages.success(request, f"L'utilisateur {utilisateur.get_full_name()} a été créé avec succès.")
            return redirect('utilisateurs_view')
    else:
        form = UtilisateurCreationForm()
    
    return render(request, 'core/utilisateur_form.html', {
        'form': form,
        'title': 'Ajouter un utilisateur',
        'submit_text': 'Créer'
    })

@login_required
def utilisateur_update(request, pk):
    """
    Vue pour modifier un utilisateur existant
    """
    utilisateur = get_object_or_404(Utilisateur, pk=pk)
    
    if request.method == 'POST':
        form = UtilisateurUpdateForm(request.POST, instance=utilisateur)
        if form.is_valid():
            utilisateur = form.save()
            messages.success(request, f"L'utilisateur {utilisateur.get_full_name()} a été modifié avec succès.")
            return redirect('utilisateurs_view')
    else:
        form = UtilisateurUpdateForm(instance=utilisateur)
    
    return render(request, 'core/utilisateur_form.html', {
        'form': form,
        'utilisateur': utilisateur,
        'title': f'Modifier l\'utilisateur {utilisateur.get_full_name()}',
        'submit_text': 'Enregistrer'
    })

@login_required
def utilisateur_delete(request, pk):
    """
    Vue pour supprimer un utilisateur
    """
    utilisateur = get_object_or_404(Utilisateur, pk=pk)
    
    if request.method == 'POST':
        nom_complet = utilisateur.get_full_name()
        utilisateur.delete()
        messages.success(request, f"L'utilisateur {nom_complet} a été supprimé avec succès.")
        return redirect('utilisateurs_view')
    
    return render(request, 'core/utilisateur_confirm_delete.html', {
        'utilisateur': utilisateur
    })

# Vues pour les véhicules
@login_required
def vehicules_list(request):
    """
    Vue pour la liste des véhicules.
    Filtrage par service pour les utilisateurs non administrateurs.
    """
    vehicules = Vehicule.objects.select_related('service').all().order_by('immatriculation')
    if not request.user.is_staff and not request.user.is_superuser:
        vehicules = vehicules.filter(service__in=request.user.service.all())

    statut_filter = request.GET.get('statut')
    service_filter = request.GET.get('service')
    if statut_filter:
        vehicules = vehicules.filter(statut=statut_filter)
    if service_filter:
        vehicules = vehicules.filter(service_id=service_filter)

    services = Service.objects.all().order_by('nom_service') if request.user.is_staff or request.user.is_superuser else request.user.service.all().order_by('nom_service')

    context = {
        'vehicules': vehicules,
        'services': services,
        'statut_filter': statut_filter,
        'service_filter': service_filter,
        'statut_choices': Vehicule.STATUT_CHOICES,
    }
    return render(request, 'core/vehicules/list.html', context)


@login_required
def fleet_dashboard(request):
    vehicules_qs = Vehicule.objects.all()
    if not request.user.is_staff and not request.user.is_superuser:
        vehicules_qs = vehicules_qs.filter(service__in=request.user.service.all())

    total = vehicules_qs.count()
    dispo = vehicules_qs.filter(statut='Disponible').count()
    maintenance = vehicules_qs.filter(statut='En maintenance').count()
    indispo = vehicules_qs.filter(statut__in=['Non Disponible', 'Réformé']).count()

    docs = VehiculeDocument.objects.filter(est_actif=True, vehicule__in=vehicules_qs)
    today = timezone.now().date()
    docs_expires = docs.filter(date_expiration__lt=today).select_related('vehicule')
    docs_soon = docs.filter(date_expiration__gte=today, date_expiration__lte=today + timedelta(days=30)).select_related('vehicule')

    context = {
        'total_vehicules': total,
        'vehicules_disponibles': dispo,
        'vehicules_maintenance': maintenance,
        'vehicules_indisponibles': indispo,
        'taux_disponibilite': round((dispo / total) * 100, 1) if total else 0,
        'documents_expired': docs_expires[:15],
        'documents_soon': docs_soon[:15],
        'recent_affectations': VehiculeAffectation.objects.select_related('vehicule', 'service', 'chauffeur').order_by('-date_creation')[:10],
    }
    return render(request, 'core/vehicules/dashboard.html', context)

@login_required
def vehicule_detail(request, pk):
    """
    Vue pour les détails d'un véhicule
    """
    vehicule = get_object_or_404(Vehicule.objects.select_related('service'), pk=pk)
    if not request.user.is_staff and not request.user.is_superuser and vehicule.service not in request.user.service.all():
        messages.error(request, "Vous n'êtes pas autorisé à consulter ce véhicule.")
        return redirect('vehicules_list')

    affectations = vehicule.affectations.select_related('service', 'chauffeur').all()[:20]
    documents = vehicule.documents.filter(est_actif=True).order_by('date_expiration', '-date_creation')
    maintenances = vehicule.maintenances.select_related('type_maintenance').order_by('-date')[:10]
    cartes = vehicule.cartes_carburant.all()

    return render(request, 'core/vehicules/detail.html', {
        'object': vehicule,
        'affectations': affectations,
        'documents': documents,
        'maintenances': maintenances,
        'cartes': cartes,
    })

@login_required
def vehicule_create(request):
    """
    Vue pour la création d'un véhicule
    """
    if request.method == 'POST':
        form = VehiculeForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            vehicule = form.save()
            messages.success(request, f'Le véhicule {vehicule.immatriculation} a été créé avec succès.')
            return redirect('vehicules_list')
    else:
        form = VehiculeForm(user=request.user)
    
    return render(request, 'core/vehicules/form.html', {
        'form': form,
        'title': 'Ajouter un véhicule',
        'submit_text': 'Ajouter'
    })

@login_required
def vehicule_update(request, pk):
    """
    Vue pour la modification d'un véhicule
    """
    vehicule = get_object_or_404(Vehicule, pk=pk)
    if not request.user.is_staff and not request.user.is_superuser and vehicule.service not in request.user.service.all():
        messages.error(request, "Vous n'êtes pas autorisé à modifier ce véhicule.")
        return redirect('vehicules_list')
    
    if request.method == 'POST':
        form = VehiculeForm(request.POST, request.FILES, instance=vehicule, user=request.user)
        if form.is_valid():
            vehicule = form.save()
            messages.success(request, f'Le véhicule {vehicule.immatriculation} a été modifié avec succès.')
            return redirect('vehicule_detail', pk=vehicule.pk)
    else:
        form = VehiculeForm(instance=vehicule, user=request.user)
    
    return render(request, 'core/vehicules/form.html', {
        'form': form,
        'vehicule': vehicule,
        'title': f'Modifier le véhicule {vehicule.immatriculation}',
        'submit_text': 'Modifier'
    })

@login_required
def vehicule_delete(request, pk):
    """
    Vue pour la suppression d'un véhicule
    """
    vehicule = get_object_or_404(Vehicule, pk=pk)

    if Maintenance.objects.filter(vehicule=vehicule).exists() or PlanificationCourse.objects.filter(vehicule=vehicule).exists():
        messages.error(request, "Suppression impossible: ce véhicule est référencé dans des maintenances ou des courses. Changez son statut (ex: Réformé).")
        return redirect('vehicule_detail', pk=vehicule.pk)
    
    if request.method == 'POST':
        immatriculation = vehicule.immatriculation
        vehicule.delete()
        messages.success(request, f'Le véhicule {immatriculation} a été supprimé avec succès.')
        return redirect('vehicules_list')
    
    return render(request, 'core/vehicules/delete.html', {'vehicule': vehicule})


@login_required
def vehicule_change_status(request, pk):
    vehicule = get_object_or_404(Vehicule, pk=pk)
    if not request.user.is_staff and not request.user.is_superuser and vehicule.service not in request.user.service.all():
        messages.error(request, "Vous n'êtes pas autorisé à modifier le statut de ce véhicule.")
        return redirect('vehicules_list')

    if request.method == 'POST':
        form = VehiculeStatusForm(request.POST, instance=vehicule)
        if form.is_valid():
            form.save()
            messages.success(request, f"Statut du véhicule {vehicule.immatriculation} mis à jour.")
            return redirect('vehicule_detail', pk=vehicule.pk)
    else:
        form = VehiculeStatusForm(instance=vehicule)

    return render(request, 'core/vehicules/status_form.html', {'form': form, 'vehicule': vehicule})


@login_required
def vehicule_affectation_create(request, pk):
    vehicule = get_object_or_404(Vehicule, pk=pk)
    if not request.user.is_staff and not request.user.is_superuser and vehicule.service not in request.user.service.all():
        messages.error(request, "Vous n'êtes pas autorisé à affecter ce véhicule.")
        return redirect('vehicules_list')

    if request.method == 'POST':
        form = VehiculeAffectationForm(request.POST, user=request.user)
        if form.is_valid():
            affectation = form.save(commit=False)
            affectation.vehicule = vehicule
            affectation.cree_par = request.user
            affectation.save()
            vehicule.service = affectation.service
            if vehicule.statut == 'Non Disponible':
                vehicule.statut = 'Disponible'
            vehicule.save(update_fields=['service', 'statut'])
            messages.success(request, "Affectation enregistrée avec succès.")
            return redirect('vehicule_detail', pk=vehicule.pk)
    else:
        form = VehiculeAffectationForm(user=request.user, initial={'service': vehicule.service})

    return render(request, 'core/vehicules/affectation_form.html', {'form': form, 'vehicule': vehicule})


@login_required
def vehicule_affectation_close(request, affectation_id):
    affectation = get_object_or_404(VehiculeAffectation, pk=affectation_id)
    vehicule = affectation.vehicule
    if not request.user.is_staff and not request.user.is_superuser and vehicule.service not in request.user.service.all():
        messages.error(request, "Vous n'êtes pas autorisé à clôturer cette affectation.")
        return redirect('vehicules_list')

    if affectation.date_fin is None:
        affectation.date_fin = timezone.now().date()
        affectation.est_active = False
        affectation.save(update_fields=['date_fin', 'est_active'])
        messages.success(request, "Affectation clôturée.")
    return redirect('vehicule_detail', pk=vehicule.pk)


@login_required
def vehicule_document_create(request, pk):
    vehicule = get_object_or_404(Vehicule, pk=pk)
    if not request.user.is_staff and not request.user.is_superuser and vehicule.service not in request.user.service.all():
        messages.error(request, "Vous n'êtes pas autorisé à gérer les documents de ce véhicule.")
        return redirect('vehicules_list')

    if request.method == 'POST':
        form = VehiculeDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.vehicule = vehicule
            document.save()
            messages.success(request, "Document véhicule ajouté avec succès.")
            return redirect('vehicule_detail', pk=vehicule.pk)
    else:
        form = VehiculeDocumentForm()

    return render(request, 'core/vehicules/document_form.html', {'form': form, 'vehicule': vehicule})

# Vues pour les cartes carburant
@login_required
def cartes_carburant_list(request):
    """
    Vue pour la liste des cartes carburant
    """
    cartes = Carte_Carburant.objects.select_related('service', 'vehicule').all().order_by('numero_carte')
    if not request.user.is_staff and not request.user.is_superuser:
        cartes = cartes.filter(service__in=request.user.service.all())
    context = {
        'object_list': cartes,
        'title': 'Cartes Carburant',
        'icon_class': 'fas fa-credit-card',
        'add_url': reverse('carte_carburant_create')
    }
    return render(request, 'core/cartes_carburant/list.html', context)

@login_required
def carte_carburant_detail(request, pk):
    """
    Vue pour les détails d'une carte carburant
    """
    carte = get_object_or_404(Carte_Carburant, pk=pk)
    if not request.user.is_staff and not request.user.is_superuser and carte.service not in request.user.service.all():
        messages.error(request, "Vous n'êtes pas autorisé à consulter cette carte.")
        return redirect('cartes_carburant_list')

    rechargements_ht = carte.rechargements_ht.select_related('achat_stock_carburant_ht').order_by('-date_rechargement')
    rechargements_ttc = carte.rechargements_ttc.select_related('achat_carburant_ttc').order_by('-date_rechargement')
    rechargements = list(rechargements_ht) + list(rechargements_ttc)
    rechargements.sort(key=lambda r: r.date_rechargement, reverse=True)

    return render(request, 'core/cartes_carburant/detail.html', {
        'carte': carte,
        'rechargements': rechargements
    })

@login_required
def carte_carburant_create(request):
    """
    Vue pour la création d'une carte carburant
    """
    if request.method == 'POST':
        form = CarteCarburantCreateForm(request.POST)
        if form.is_valid():
            carte = form.save(commit=False)
            carte.statut = 'Disponible'  # Définir le statut par défaut
            carte.save()
            messages.success(request, f'La carte carburant {carte.numero_carte} a été créée avec succès.')
            return redirect('cartes_carburant_list')
    else:
        form = CarteCarburantCreateForm()
    
    return render(request, 'core/cartes_carburant/form.html', {
        'form': form,
        'title': 'Ajouter une carte carburant',
        'submit_text': 'Ajouter',
        'cancel_url': reverse('cartes_carburant_list'),
        'icon_class': 'fas fa-credit-card'
    })

@login_required
def carte_carburant_update(request, pk):
    """
    Vue pour la modification d'une carte carburant
    """
    carte = get_object_or_404(Carte_Carburant, pk=pk)
    
    if request.method == 'POST':
        form = CarteCarburantForm(request.POST, instance=carte)
        if form.is_valid():
            carte = form.save()
            messages.success(request, f'La carte carburant {carte.numero_carte} a été modifiée avec succès.')
            return redirect('carte_carburant_detail', pk=carte.pk)
    else:
        form = CarteCarburantForm(instance=carte)
    
    return render(request, 'core/cartes_carburant/form.html', {
        'form': form,
        'carte': carte,
        'title': f'Modifier la carte carburant {carte.numero_carte}',
        'submit_text': 'Modifier'
    })

@login_required
def carte_carburant_delete(request, pk):
    """
    Vue pour la suppression d'une carte carburant
    """
    carte = get_object_or_404(Carte_Carburant, pk=pk)
    
    if request.method == 'POST':
        numero_carte = carte.numero_carte
        carte.delete()
        messages.success(request, f'La carte carburant {numero_carte} a été supprimée avec succès.')
        return redirect('cartes_carburant_list')
    
    return render(request, 'core/cartes_carburant/delete.html', {'carte': carte})

# Vues pour les fournisseurs
@login_required
def fournisseurs_list(request):
    """
    Vue pour la liste des fournisseurs
    """
    fournisseurs_list = Fournisseur.objects.all().order_by('nom_fournisseur')
    return render(request, 'core/fournisseurs/list.html', {'fournisseurs_list': fournisseurs_list})

@login_required
def fournisseur_detail(request, pk):
    """
    Vue pour les détails d'un fournisseur
    """
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    achats_ht = fournisseur.achats_stock_carburant_ht.all().order_by('-date_achat')
    achats_ttc = fournisseur.achats_carburant_ttc.all().order_by('-date_achat')
    return render(request, 'core/fournisseurs/detail.html', {'object': fournisseur})

@login_required
def fournisseur_create(request):
    """
    Vue pour la création d'un fournisseur
    """
    if request.method == 'POST':
        form = FournisseurForm(request.POST)
        if form.is_valid():
            fournisseur = form.save()
            messages.success(request, f'Le fournisseur {fournisseur.nom_fournisseur} a été créé avec succès.')
            return redirect('fournisseurs_list')
    else:
        form = FournisseurForm()
    
    return render(request, 'core/fournisseurs/form.html', {
        'form': form,
        'title': 'Ajouter un fournisseur',
        'submit_text': 'Ajouter'
    })

@login_required
def fournisseur_update(request, pk):
    """
    Vue pour la modification d'un fournisseur
    """
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    
    if request.method == 'POST':
        form = FournisseurForm(request.POST, instance=fournisseur)
        if form.is_valid():
            fournisseur = form.save()
            messages.success(request, f'Le fournisseur {fournisseur.nom_fournisseur} a été modifié avec succès.')
            return redirect('fournisseur_detail', pk=fournisseur.pk)
    else:
        form = FournisseurForm(instance=fournisseur)
    
    return render(request, 'core/fournisseurs/form.html', {
        'form': form,
        'fournisseur': fournisseur,
        'title': f'Modifier le fournisseur {fournisseur.nom_fournisseur}',
        'submit_text': 'Modifier'
    })

@login_required
def fournisseur_delete(request, pk):
    """
    Vue pour la suppression d'un fournisseur
    """
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    
    if request.method == 'POST':
        nom_fournisseur = fournisseur.nom_fournisseur
        fournisseur.delete()
        messages.success(request, f'Le fournisseur {nom_fournisseur} a été supprimé avec succès.')
        return redirect('fournisseurs_list')
    
    return render(request, 'core/fournisseurs/delete.html', {'fournisseur': fournisseur})

# Vues pour les achats de carburant HT
@login_required
def achats_carburant_ht_list(request):
    """
    Vue pour la liste des achats de carburant HT
    """
    achats = Achat_Stock_Carburant_HT.objects.all().order_by('-date_achat')
    context = {
        'object_list': achats,
        'title': 'Achats de Carburant HT',
        'icon_class': 'fas fa-gas-pump',
        'add_url': reverse('achat_carburant_ht_create')
    }
    return render(request, 'core/achats_carburant_ht/list.html', context)

@login_required
def achat_carburant_ht_detail(request, pk):
    """
    Vue pour les détails d'un achat de carburant HT
    """
    achat = get_object_or_404(Achat_Stock_Carburant_HT, pk=pk)
    return render(request, 'core/achats_carburant_ht/detail.html', {'achat': achat})

@login_required
def achat_carburant_ht_create(request):
    """
    Vue pour la création d'un achat de carburant HT
    """
    if request.method == 'POST':
        form = AchatStockCarburantHTForm(request.POST, request.FILES)
        if form.is_valid():
            achat = form.save()
            messages.success(request, f'L\'achat de carburant HT {achat.voucher} a été créé avec succès.')
            return redirect('achats_carburant_ht_list')
    else:
        form = AchatStockCarburantHTForm()
    
    return render(request, 'core/achats_carburant_ht/form.html', {
        'form': form,
        'title': 'Ajouter un achat de carburant HT',
        'submit_text': 'Ajouter',
        'cancel_url': reverse('achats_carburant_ht_list'),
        'icon_class': 'fas fa-gas-pump'
    })

@login_required
def achat_carburant_ht_update(request, pk):
    """
    Vue pour la modification d'un achat de carburant HT
    """
    achat = get_object_or_404(Achat_Stock_Carburant_HT, pk=pk)
    
    if request.method == 'POST':
        form = AchatStockCarburantHTForm(request.POST, request.FILES, instance=achat)
        if form.is_valid():
            achat = form.save()
            messages.success(request, f'L\'achat de carburant HT {achat.voucher} a été modifié avec succès.')
            return redirect('achat_carburant_ht_detail', pk=achat.pk)
    else:
        form = AchatStockCarburantHTForm(instance=achat)
    
    return render(request, 'core/achats_carburant_ht/form.html', {
        'form': form,
        'achat': achat,
        'title': f'Modifier l\'achat de carburant HT {achat.voucher}',
        'submit_text': 'Modifier'
    })

@login_required
def achat_carburant_ht_delete(request, pk):
    """
    Vue pour la suppression d'un achat de carburant HT
    """
    achat = get_object_or_404(Achat_Stock_Carburant_HT, pk=pk)
    
    if request.method == 'POST':
        voucher = achat.voucher
        achat.delete()
        messages.success(request, f'L\'achat de carburant HT {voucher} a été supprimé avec succès.')
        return redirect('achats_carburant_ht_list')
    
    return render(request, 'core/achats_carburant_ht/delete.html', {'achat': achat})

# Vues pour les achats de carburant TTC
@login_required
def achats_carburant_ttc_list(request):
    """
    Vue pour la liste des achats de carburant TTC
    """
    achats = Achat_Carburant_TTC.objects.all().order_by('-date_achat')
    context = {
        'object_list': achats,
        'title': 'Achats de Carburant TTC',
        'icon_class': 'fas fa-gas-pump',
        'add_url': reverse('achat_carburant_ttc_create')
    }
    return render(request, 'core/achats_carburant_ttc/list.html', context)

@login_required
def achat_carburant_ttc_detail(request, pk):
    """
    Vue pour les détails d'un achat de carburant TTC
    """
    achat = get_object_or_404(Achat_Carburant_TTC, pk=pk)
    return render(request, 'core/achats_carburant_ttc/detail.html', {'achat': achat})

@login_required
def achat_carburant_ttc_create(request):
    """
    Vue pour la création d'un achat de carburant TTC
    """
    if request.method == 'POST':
        form = AchatCarburantTTCForm(request.POST, request.FILES)
        if form.is_valid():
            achat = form.save()
            messages.success(request, f'L\'achat de carburant TTC {achat.voucher} a été créé avec succès.')
            return redirect('achats_carburant_ttc_list')
    else:
        form = AchatCarburantTTCForm()
    
    return render(request, 'core/achats_carburant_ttc/form.html', {
        'form': form,
        'title': 'Ajouter un achat de carburant TTC',
        'submit_text': 'Ajouter',
        'cancel_url': reverse('achats_carburant_ttc_list'),
        'icon_class': 'fas fa-gas-pump'
    })

@login_required
def achat_carburant_ttc_update(request, pk):
    """
    Vue pour la modification d'un achat de carburant TTC
    """
    achat = get_object_or_404(Achat_Carburant_TTC, pk=pk)
    
    if request.method == 'POST':
        form = AchatCarburantTTCForm(request.POST, request.FILES, instance=achat)
        if form.is_valid():
            achat = form.save()
            messages.success(request, f'L\'achat de carburant TTC {achat.voucher} a été modifié avec succès.')
            return redirect('achat_carburant_ttc_detail', pk=achat.pk)
    else:
        form = AchatCarburantTTCForm(instance=achat)
    
    return render(request, 'core/achats_carburant_ttc/form.html', {
        'form': form,
        'achat': achat,
        'title': f'Modifier l\'achat de carburant TTC {achat.voucher}',
        'submit_text': 'Modifier'
    })

@login_required
def achat_carburant_ttc_delete(request, pk):
    """
    Vue pour la suppression d'un achat de carburant TTC
    """
    achat = get_object_or_404(Achat_Carburant_TTC, pk=pk)
    
    if request.method == 'POST':
        voucher = achat.voucher
        achat.delete()
        messages.success(request, f'L\'achat de carburant TTC {voucher} a été supprimé avec succès.')
        return redirect('achats_carburant_ttc_list')
    
    return render(request, 'core/achats_carburant_ttc/delete.html', {'achat': achat})

# Vues pour les rechargements de cartes carburant
@login_required
@user_passes_test(lambda u: u.groupe.filter(nom_groupe__in=['Administrateur', 'Gestionnaire Carburant']).exists())
def rechargements_carte_carburant_list(request):
    """
    Vue pour la liste des rechargements de cartes carburant
    """
    rechargements_ht = Rechargement_Carte_Carburant_HT.objects.all().order_by('-date_rechargement')
    rechargements_ttc = Rechargement_Carte_Carburant_TTC.objects.all().order_by('-date_rechargement')
    return render(request, 'core/rechargements_carte_carburant/list.html', {
        'rechargements_ht': rechargements_ht,
        'rechargements_ttc': rechargements_ttc,
    })

@login_required
def rechargement_carte_carburant_detail(request, pk):
    """
    Vue pour les détails d'un rechargement de carte carburant
    """
    # Essayer de trouver le rechargement dans les rechargements HT
    try:
        rechargement = Rechargement_Carte_Carburant_HT.objects.get(pk=pk)
    except Rechargement_Carte_Carburant_HT.DoesNotExist:
        # Si non trouvé, essayer dans les rechargements TTC
        try:
            rechargement = Rechargement_Carte_Carburant_TTC.objects.get(pk=pk)
        except Rechargement_Carte_Carburant_TTC.DoesNotExist:
            # Si non trouvé dans les deux, retourner une erreur 404
            from django.http import Http404
            raise Http404("Rechargement non trouvé")
    
    return render(request, 'core/rechargements_carte_carburant/detail.html', {
        'object': rechargement,
    })

@login_required
@user_passes_test(lambda u: u.groupe.filter(nom_groupe__in=['Administrateur', 'Gestionnaire Carburant']).exists())
def rechargement_carte_carburant_create(request):
    """
    Vue pour la création d'un rechargement de carte carburant
    """
    if request.method == 'POST':
        form = RechargementCarteCarburantHTForm(request.POST)
        if form.is_valid():
            rechargement = form.save(commit=False)
            # Récupérer l'achat de stock de carburant HT sélectionné
            achat_stock_id = request.POST.get('achat_stock_carburant_ht')
            achat_stock = get_object_or_404(Achat_Stock_Carburant_HT, pk=achat_stock_id)
            rechargement.achat_stock_carburant_ht = achat_stock
            
            # Vérifier si cette carte a déjà été rechargée avec ce stock
            carte_deja_rechargee = Rechargement_Carte_Carburant_HT.objects.filter(
                achat_stock_carburant_ht=achat_stock,
                carte_carburant=form.cleaned_data['carte_carburant']
            ).exists()
            
            if carte_deja_rechargee:
                messages.error(request, "Cette carte a déjà été rechargée avec ce stock de carburant.")
            else:
                try:
                    with transaction.atomic():
                        rechargement.save()
                    
                    messages.success(request, f'Le rechargement de carte a été créé avec succès.')
                    return redirect('rechargements_carte_carburant_list')
                except Exception as e:
                    messages.error(request, f"Erreur lors de l'enregistrement du rechargement: {str(e)}")
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = RechargementCarteCarburantHTForm(initial={'date_rechargement': timezone.now().date()})
    
    # Récupérer la liste des achats de stock de carburant HT disponibles
    achats_stock = Achat_Stock_Carburant_HT.objects.all().order_by('-date_achat')
    
    return render(request, 'core/rechargements_carte_carburant/form.html', {
        'form': form,
        'achats_stock': achats_stock,
        'title': 'Ajouter un rechargement de carte',
        'submit_text': 'Ajouter',
        'safe': True
    })

@login_required
@user_passes_test(lambda u: u.groupe.filter(nom_groupe__in=['Administrateur', 'Gestionnaire Carburant']).exists())
def rechargement_carte_carburant_update(request, pk):
    """
    Vue pour la modification d'un rechargement de carte carburant
    """
    rechargement = get_object_or_404(Rechargement_Carte_Carburant_HT, pk=pk)
    ancienne_carte = rechargement.carte_carburant
    ancien_achat_stock = rechargement.achat_stock_carburant_ht
    
    if request.method == 'POST':
        form = RechargementCarteCarburantHTForm(request.POST, instance=rechargement)
        if form.is_valid():
            # Récupérer l'achat de stock de carburant HT sélectionné
            achat_stock_id = request.POST.get('achat_stock_carburant_ht')
            nouvel_achat_stock = get_object_or_404(Achat_Stock_Carburant_HT, pk=achat_stock_id)
            
            # Vérifier si la carte a déjà été rechargée avec ce stock (sauf si c'est le même rechargement)
            if nouvel_achat_stock != ancien_achat_stock or form.cleaned_data['carte_carburant'] != ancienne_carte:
                carte_deja_rechargee = Rechargement_Carte_Carburant_HT.objects.filter(
                    achat_stock_carburant_ht=nouvel_achat_stock,
                    carte_carburant=form.cleaned_data['carte_carburant']
                ).exclude(pk=pk).exists()
                
                if carte_deja_rechargee:
                    messages.error(request, "Cette carte a déjà été rechargée avec ce stock de carburant.")
                    return render(request, 'core/rechargements_carte_carburant/form.html', {
                        'form': form,
                        'achats_stock': Achat_Stock_Carburant_HT.objects.all().order_by('-date_achat'),
                        'title': 'Modifier le rechargement de carte',
                        'submit_text': 'Modifier',
                        'rechargement': rechargement,
                        'safe': True
                    })
            
            try:
                # Mettre à jour l'achat de stock
                rechargement.achat_stock_carburant_ht = nouvel_achat_stock
                
                # Enregistrer le rechargement (la logique modèle recalcule les soldes)
                with transaction.atomic():
                    rechargement = form.save()
                
                messages.success(request, f'Le rechargement de carte a été modifié avec succès.')
                return redirect('rechargement_carte_carburant_detail', pk=rechargement.pk)
            except Exception as e:
                messages.error(request, f"Erreur lors de la modification du rechargement: {str(e)}")
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = RechargementCarteCarburantHTForm(instance=rechargement)
    
    # Récupérer la liste des achats de stock de carburant HT disponibles
    achats_stock = Achat_Stock_Carburant_HT.objects.all().order_by('-date_achat')
    
    return render(request, 'core/rechargements_carte_carburant/form.html', {
        'form': form,
        'achats_stock': achats_stock,
        'title': 'Modifier le rechargement de carte',
        'submit_text': 'Modifier',
        'rechargement': rechargement,
        'safe': True
    })

@login_required
@user_passes_test(lambda u: u.groupe.filter(nom_groupe__in=['Administrateur', 'Gestionnaire Carburant']).exists())
def rechargement_carte_carburant_delete(request, pk):
    """
    Vue pour la suppression d'un rechargement de carte carburant
    """
    rechargement = get_object_or_404(Rechargement_Carte_Carburant_HT, pk=pk)
    
    if request.method == 'POST':
        rechargement.delete()
        messages.success(request, f'Le rechargement de carte a été supprimé avec succès.')
        return redirect('rechargements_carte_carburant_list')
    
    return render(request, 'core/confirm_delete.html', {
        'object': rechargement,
        'title': 'Supprimer un rechargement de carte',
        'cancel_url': 'rechargements_carte_carburant_list',
    })

@login_required
@user_passes_test(lambda u: u.groupe.filter(nom_groupe__in=['Administrateur', 'Gestionnaire Carburant']).exists())
def achat_stock_carburant_rechargement(request, pk):
    """
    Vue pour la page de gestion des rechargements de cartes à partir d'un achat de stock de carburant HT
    """
    achat_stock = get_object_or_404(Achat_Stock_Carburant_HT, pk=pk)
    rechargements = Rechargement_Carte_Carburant_HT.objects.filter(achat_stock_carburant_ht=achat_stock).order_by('-date_rechargement')
    
    # Calculer le volume total rechargé
    volume_total_recharge = rechargements.aggregate(total=Sum('volume'))['total'] or 0
    volume_restant = achat_stock.volume - volume_total_recharge
    
    # Calculer le montant total rechargé
    montant_total_recharge = rechargements.aggregate(total=Sum('montant_ttc'))['total'] or 0
    montant_restant = achat_stock.montant_ttc - montant_total_recharge
    
    # Pour chaque rechargement, calculer le volume restant et le solde restant
    # en tenant compte des ravitaillements effectués
    for rechargement in rechargements:
        # Récupérer les demandes de ravitaillement associées à ce rechargement
        demandes = Demande_Carte_Carburant.objects.filter(
            rechargement_ht=rechargement,
            statut_demande='Close',
        )
        
        # Calculer le volume et le montant consommés par les ravitaillements
        volume_consomme = demandes.aggregate(total=Sum('volume'))['total'] or 0
        montant_consomme = demandes.aggregate(total=Sum('montant_ttc'))['total'] or 0
        
        # Calculer le volume et le solde restants
        rechargement.volume_restant = rechargement.volume - volume_consomme
        rechargement.solde_restant = rechargement.montant_ttc - montant_consomme
    
    if request.method == 'POST':
        form = RechargementCarteCarburantHTForm(request.POST)
        if form.is_valid():
            rechargement = form.save(commit=False)
            rechargement.achat_stock_carburant_ht = achat_stock
            
            # Vérifier si cette carte a déjà été rechargée avec ce stock
            carte_deja_rechargee = Rechargement_Carte_Carburant_HT.objects.filter(
                achat_stock_carburant_ht=achat_stock,
                carte_carburant=form.cleaned_data['carte_carburant']
            ).exists()
            
            if carte_deja_rechargee:
                messages.error(request, "Cette carte a déjà été rechargée avec ce stock de carburant.")
            else:
                try:
                    with transaction.atomic():
                        rechargement.save()
                    
                    messages.success(request, f'Le rechargement de carte a été créé avec succès.')
                    return redirect('achat_stock_carburant_rechargement', pk=pk)
                except Exception as e:
                    messages.error(request, f"Erreur lors de l'enregistrement du rechargement: {str(e)}")
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = RechargementCarteCarburantHTForm(initial={'date_rechargement': timezone.now().date()})
    
    # Récupérer la liste des achats de stock de carburant HT disponibles
    achats_stock = Achat_Stock_Carburant_HT.objects.all().order_by('-date_achat')
    
    return render(request, 'core/rechargements_carte_carburant/master_detail.html', {
        'achat_stock': achat_stock,
        'rechargements': rechargements,
        'form': form,
        'volume_total_recharge': volume_total_recharge,
        'volume_restant': volume_restant,
        'montant_total_recharge': montant_total_recharge,
        'montant_restant': montant_restant,
        'is_ht': True,  # Indiquer qu'il s'agit de rechargements HT
        'is_ttc': False,
        'safe': True
    })

@login_required
@user_passes_test(lambda u: u.groupe.filter(nom_groupe__in=['Administrateur', 'Gestionnaire Carburant']).exists())
def achat_carburant_ttc_rechargement(request, pk):
    """
    Vue pour la page de gestion des rechargements de cartes à partir d'un achat de carburant TTC
    """
    achat_ttc = get_object_or_404(Achat_Carburant_TTC, pk=pk)
    
    # Récupérer les rechargements TTC associés à cet achat
    rechargements = Rechargement_Carte_Carburant_TTC.objects.filter(achat_carburant_ttc=achat_ttc).order_by('-date_rechargement')
    
    # Calculer le volume total rechargé
    volume_total_recharge = rechargements.aggregate(total=Sum('volume'))['total'] or 0
    volume_restant = achat_ttc.volume - volume_total_recharge
    
    # Calculer le montant total rechargé
    montant_total_recharge = rechargements.aggregate(total=Sum('montant_ttc'))['total'] or 0
    montant_restant = achat_ttc.montant_ttc - montant_total_recharge
    
    # Pour chaque rechargement, calculer le volume restant et le solde restant
    # en tenant compte des ravitaillements effectués
    for rechargement in rechargements:
        # Récupérer les demandes de ravitaillement associées à ce rechargement
        demandes = Demande_Carte_Carburant.objects.filter(
            rechargement_ttc=rechargement,
            statut_demande='Close',
        )
        
        # Calculer le volume et le montant consommés par les ravitaillements
        volume_consomme = demandes.aggregate(total=Sum('volume'))['total'] or 0
        montant_consomme = demandes.aggregate(total=Sum('montant_ttc'))['total'] or 0
        
        # Calculer le volume et le solde restants
        rechargement.volume_restant = rechargement.volume - volume_consomme
        rechargement.solde_restant = rechargement.montant_ttc - montant_consomme
    
    if request.method == 'POST':
        form = RechargementCarteCarburantTTCForm(request.POST)
        if form.is_valid():
            rechargement = form.save(commit=False)
            rechargement.achat_carburant_ttc = achat_ttc
            
            # Vérifier si cette carte a déjà été rechargée avec cet achat
            carte_deja_rechargee = Rechargement_Carte_Carburant_TTC.objects.filter(
                achat_carburant_ttc=achat_ttc,
                carte_carburant=form.cleaned_data['carte_carburant']
            ).exists()
            
            if carte_deja_rechargee:
                messages.error(request, "Cette carte a déjà été rechargée avec cet achat de carburant.")
            else:
                try:
                    with transaction.atomic():
                        rechargement.save()
                    
                    messages.success(request, f'Le rechargement de carte a été créé avec succès.')
                    return redirect('achat_carburant_ttc_rechargement', pk=pk)
                except Exception as e:
                    messages.error(request, f"Erreur lors de l'enregistrement du rechargement: {str(e)}")
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = RechargementCarteCarburantTTCForm(initial={'date_rechargement': timezone.now().date()})
    
    return render(request, 'core/rechargements_carte_carburant/master_detail.html', {
        'achat_ttc': achat_ttc,
        'rechargements': rechargements,
        'form': form,
        'volume_total_recharge': volume_total_recharge,
        'volume_restant': volume_restant,
        'montant_total_recharge': montant_total_recharge,
        'montant_restant': montant_restant,
        'is_ht': False,  # Indiquer qu'il s'agit de rechargements TTC
        'is_ttc': True,
        'safe': True
    })

# Vues pour les demandes de carte carburant
@login_required
def demandes_carte_carburant_list(request):
    """
    Vue pour la liste des demandes de carte carburant
    """
    # Filtrer les demandes selon le groupe de l'utilisateur
    user_groupes = request.user.groupe.all().values_list('nom_groupe', flat=True)
    user_services = request.user.service.all()
    
    if 'Gestionnaire Carburant' in user_groupes:
        # Les gestionnaires de carburant voient uniquement les demandes des véhicules de leurs services
        demandes = Demande_Carte_Carburant.objects.filter(vehicule__service__in=user_services).order_by('-date_demande')
    elif 'Driver' in user_groupes:
        # Les chauffeurs ne voient que leurs propres demandes
        demandes = Demande_Carte_Carburant.objects.filter(utilisateur_demandeur=request.user).order_by('-date_demande')
    else:
        # Les autres utilisateurs ne voient rien
        demandes = Demande_Carte_Carburant.objects.none()
    
    # Pagination - 10 demandes par page
    paginator = Paginator(demandes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'core/demandes_carte_carburant/list.html', {
        'demandes': page_obj,
        'title': 'Liste des demandes de carte carburant',
        'page_obj': page_obj,  # Ajouter l'objet page pour la pagination
    })

@login_required
def demande_carte_carburant_create(request):
    """
    Vue pour créer une nouvelle demande de carte carburant
    """
    # Vérifier si l'utilisateur est un chauffeur
    if 'Driver' not in request.user.groupe.all().values_list('nom_groupe', flat=True):
        messages.error(request, "Vous n'êtes pas autorisé à créer une demande de carte carburant.")
        return redirect('demandes_carte_carburant_list')
    
    if request.method == 'POST':
        form = DemandeCarteCarburantCreateForm(request.POST, user=request.user)
        if form.is_valid():
            demande = form.save(commit=False)
            demande.utilisateur_demandeur = request.user
            # Le service est déjà sélectionné dans le formulaire, pas besoin de l'assigner ici
            demande.statut_demande = 'En attente'
            
            demande.save()
            
            # Envoyer une notification par email aux gestionnaires carburant
            gestionnaires = Utilisateur.objects.filter(
                groupe__nom_groupe='Gestionnaire Carburant',
                service=demande.service
            )
            
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
            
            messages.success(request, "Votre demande de carte carburant a été créée avec succès.")
            return redirect('demandes_carte_carburant_list')
    else:
        form = DemandeCarteCarburantCreateForm(user=request.user)
    
    return render(request, 'core/demandes_carte_carburant/form.html', {
        'form': form,
        'title': 'Nouvelle demande de carte carburant',
        'submit_text': 'Créer la demande',
        'safe': True
    })

@login_required
def demande_carte_carburant_detail(request, pk):
    """
    Vue pour afficher les détails d'une demande de carte carburant
    """
    try:
        demande = Demande_Carte_Carburant.objects.get(pk=pk)
    except Demande_Carte_Carburant.DoesNotExist:
        messages.error(request, "La demande spécifiée n'existe pas.")
        return redirect('demandes_carte_carburant_list')
    
    # Vérifier les permissions
    user_groupes = request.user.groupe.all().values_list('nom_groupe', flat=True)
    if 'Gestionnaire Carburant' not in user_groupes and demande.utilisateur_demandeur != request.user:
        messages.error(request, "Vous n'êtes pas autorisé à voir cette demande.")
        return redirect('demandes_carte_carburant_list')
    
    return render(request, 'core/demandes_carte_carburant/detail.html', {
        'demande': demande,
        'title': f'Détails de la demande #{demande.id_demande}',
        'safe': True
    })

@login_required
def demande_carte_carburant_traitement(request, pk):
    """
    Vue pour traiter une demande de carte carburant (accepter ou rejeter)
    """
    from core.models import Achat_Stock_Carburant_HT, Achat_Carburant_TTC
    
    try:
        demande = Demande_Carte_Carburant.objects.get(pk=pk)
    except Demande_Carte_Carburant.DoesNotExist:
        messages.error(request, "La demande spécifiée n'existe pas.")
        return redirect('demandes_carte_carburant_list')
    
    # Vérifier les permissions
    if demande.utilisateur_demandeur != request.user and not request.user.groupe.filter(nom_groupe='Gestionnaire Carburant').exists():
        messages.error(request, "Vous n'êtes pas autorisé à traiter cette demande.")
        return redirect('demande_carte_carburant_detail', pk=pk)
    
    if demande.statut_demande != 'En attente':
        messages.error(request, "Cette demande a déjà été traitée.")
        return redirect('demande_carte_carburant_detail', pk=pk)
    
    if request.method == 'POST':
        # Passe explicitement le service lié à la demande pour filtrer les dotations
        form = DemandeCarteCarburantTraitementForm(request.POST, instance=demande, service=demande.service)
        if form.is_valid():
            demande = form.save(commit=False)

            try:
                if demande.statut_demande == 'Acceptée':
                    validate_demande(
                        demande,
                        utilisateur_traitant=request.user,
                        commentaire=demande.commentaire,
                    )
                elif demande.statut_demande == 'Rejetée':
                    reject_demande(
                        demande,
                        utilisateur_traitant=request.user,
                        commentaire=demande.commentaire,
                    )
                else:
                    demande.utilisateur_traitant = request.user
                    demande.date_traitement = timezone.now()
                    demande.save()
            except Exception as e:
                messages.error(request, str(e))
                return render(request, 'core/demandes_carte_carburant/traitement.html', {
                    'form': form,
                    'demande': demande,
                    'title': f'Traitement de la demande #{demande.id_demande}',
                    'safe': True
                })
            
            # Générer la fiche de ravitaillement si elle n'existe pas déjà
            if not demande.fiche_ravitaillement:
                fiche_html = render_to_string('core/demandes_carte_carburant/fiche_ravitaillement.html', {
                    'demande': demande,
                    # S'assurer que la carte carburant est définie
                    'carte_carburant': demande.get_carte_carburant,
                    'service': demande.service,
                    'vehicule': demande.vehicule,
                })
                
                # Créer un fichier PDF temporaire
                pdf_file = BytesIO()
                pisa.CreatePDF(fiche_html, dest=pdf_file)
                
                # Sauvegarder le PDF dans le champ fiche_ravitaillement
                pdf_file.seek(0)
                demande.fiche_ravitaillement.save(
                    f'fiche_ravitaillement_{demande.id_demande}.pdf',
                    ContentFile(pdf_file.read()),
                    save=False
                )
                
                demande.save()
            
            # Envoyer un email au chauffeur
            if demande.utilisateur_demandeur and demande.utilisateur_demandeur.email:
                subject = f'Traitement de votre demande de carte carburant #{demande.id_demande}'
                from_email = settings.DEFAULT_FROM_EMAIL
                to = demande.utilisateur_demandeur.email
                
                solde_formate = None
                if demande.rechargement_ht:
                    if demande.rechargement_ht.solde_restant is None:
                        demande.rechargement_ht.solde_restant = demande.rechargement_ht.montant_ttc
                        demande.rechargement_ht.save()
                    solde_formate = f"{demande.rechargement_ht.solde_restant:,} FCFA".replace(",", " ")
                elif demande.rechargement_ttc:
                    if demande.rechargement_ttc.solde_restant is None:
                        demande.rechargement_ttc.solde_restant = demande.rechargement_ttc.montant_ttc
                        demande.rechargement_ttc.save()
                    solde_formate = f"{demande.rechargement_ttc.solde_restant:,} FCFA".replace(",", " ")
                
                context = {
                    'demande': demande,
                    'solde_formate': solde_formate,
                    'statut': 'Acceptée' if demande.statut_demande == 'Acceptée' else 'Rejetée'
                }
                
                html_message = render_to_string('core/emails/traitement_demande_email.html', context)
                plain_message = strip_tags(html_message)
                
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
            
            # Envoyer une notification aux gestionnaires de cartes si la demande est acceptée
            if demande.statut_demande == 'Acceptée':
                gestionnaires_cartes = Utilisateur.objects.filter(groupe__nom_groupe='Gestionnaire Cartes')
                
                for gestionnaire in gestionnaires_cartes:
                    if gestionnaire.email:
                        subject = f'Nouvelle demande de carte carburant acceptée #{demande.id_demande}'
                        from_email = settings.DEFAULT_FROM_EMAIL
                        to = gestionnaire.email
                        
                        context = {
                            'demande': demande,
                            'gestionnaire': gestionnaire,
                            'chauffeur': demande.utilisateur_demandeur,
                            'vehicule': demande.vehicule,
                            'service': demande.service
                        }
                        
                        html_message = render_to_string('core/emails/traitement_demande_gestionnaire_cartes_email.html', context)
                        plain_message = strip_tags(html_message)
                        
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
            
            messages.success(request, f"La demande #{demande.id_demande} a été traitée avec succès.")
            return redirect('demandes_carte_carburant_list')
    else:
        # Passe explicitement le service lié à la demande pour filtrer les dotations
        form = DemandeCarteCarburantTraitementForm(instance=demande, service=demande.service)
    
    return render(request, 'core/demandes_carte_carburant/traitement.html', {
        'form': form,
        'demande': demande,
        'title': f'Traitement de la demande #{demande.id_demande}',
        'safe': True
    })

@login_required
def demande_carte_carburant_cloture(request, pk):
    """
    Vue pour clôturer une demande de carte carburant (après ravitaillement)
    """
    try:
        demande = Demande_Carte_Carburant.objects.get(pk=pk)
    except Demande_Carte_Carburant.DoesNotExist:
        messages.error(request, "La demande spécifiée n'existe pas.")
        return redirect('demandes_carte_carburant_list')
    
    # Vérifier les permissions
    if demande.utilisateur_demandeur != request.user:
        messages.error(request, "Vous n'êtes pas autorisé à clôturer cette demande.")
        return redirect('demande_carte_carburant_detail', pk=pk)
    
    if demande.statut_demande != 'Acceptée':
        messages.error(request, "Seules les demandes acceptées peuvent être clôturées.")
        return redirect('demande_carte_carburant_detail', pk=pk)
    
    if request.method == 'POST':
        form = DemandeCarteCarburantClotureForm(request.POST, request.FILES, instance=demande)
        if form.is_valid():
            demande = form.save(commit=False)
            demande.statut_demande = 'Close'
            demande.date_cloture = timezone.now()
            
            # Vérifier que le kilométrage n'est pas le même que celui d'une demande précédente pour le même véhicule
            if demande.vehicule:
                derniere_demande = Demande_Carte_Carburant.objects.filter(
                    vehicule=demande.vehicule,
                    statut_demande='Close',
                    km_vehicule=demande.km_vehicule
                ).exclude(pk=demande.pk).first()
                
                if derniere_demande:
                    messages.error(request, f"Le kilométrage {demande.km_vehicule} a déjà été utilisé pour un ravitaillement précédent de ce véhicule. Veuillez saisir le kilométrage actuel.")
                    return render(request, 'core/demandes_carte_carburant/cloture.html', {
                        'form': form,
                        'demande': demande,
                        'title': f'Clôture de la demande #{demande.id_demande}',
                        'safe': True
                    })
            
            # Récupérer le rechargement et la carte associés à la demande
            rechargement = None
            carte = None
            
            if demande.rechargement_ht:
                rechargement = demande.rechargement_ht
                carte = rechargement.carte_carburant
            elif demande.rechargement_ttc:
                rechargement = demande.rechargement_ttc
                carte = rechargement.carte_carburant
            
            # S'assurer que la carte carburant est définie
            if carte is None and hasattr(demande, 'get_carte_carburant') and demande.get_carte_carburant:
                carte = demande.get_carte_carburant
            
            # Vérifier que toutes les données nécessaires sont présentes
            if demande.montant_ttc is None or demande.montant_ttc <= 0:
                messages.error(request, "Le montant TTC doit être supérieur à zéro.")
                return render(request, 'core/demandes_carte_carburant/cloture.html', {
                    'form': form,
                    'demande': demande,
                    'title': f'Clôturer la demande #{demande.id_demande}',
                    'safe': True
                })
            
            if demande.volume is None or demande.volume <= 0:
                messages.error(request, "Le volume doit être supérieur à zéro.")
                return render(request, 'core/demandes_carte_carburant/cloture.html', {
                    'form': form,
                    'demande': demande,
                    'title': f'Clôture de la demande #{demande.id_demande}',
                    'safe': True
                })
            
            if demande.km_vehicule is None or demande.km_vehicule <= 0:
                messages.error(request, "Le kilométrage doit être supérieur à zéro.")
                return render(request, 'core/demandes_carte_carburant/cloture.html', {
                    'form': form,
                    'demande': demande,
                    'title': f'Clôture de la demande #{demande.id_demande}',
                    'safe': True
                })
            
            if not demande.station_service:
                messages.error(request, "Veuillez spécifier la station service.")
                return render(request, 'core/demandes_carte_carburant/cloture.html', {
                    'form': form,
                    'demande': demande,
                    'title': f'Clôture de la demande #{demande.id_demande}',
                    'safe': True
                })
            
            try:
                close_demande(demande, rechargement=rechargement)
            except Exception as e:
                messages.error(request, str(e))
                return render(request, 'core/demandes_carte_carburant/cloture.html', {
                    'form': form,
                    'demande': demande,
                    'title': f'Clôture de la demande #{demande.id_demande}',
                    'safe': True
                })
            
            # Envoyer une notification par email aux gestionnaires carburant
            gestionnaires = Utilisateur.objects.filter(
                groupe__nom_groupe='Gestionnaire Carburant',
                service=demande.service
            )
            
            for gestionnaire in gestionnaires:
                if gestionnaire.email:
                    subject = f"Demande de carte carburant #{demande.id_demande} clôturée"
                    html_message = render_to_string('core/emails/cloture_demande_email.html', {
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
            
            messages.success(request, "La demande a été clôturée avec succès.")
            return redirect('demandes_carte_carburant_list')
    else:
        form = DemandeCarteCarburantClotureForm(instance=demande)
    
    # Récupérer le solde correct en fonction de la dotation
    solde_carte = None
    solde_formate = None
    carte_carburant = None
    if demande.rechargement_ht:
        rechargement = demande.rechargement_ht
        if rechargement:
            carte_carburant = rechargement.carte_carburant
            # Initialiser solde_restant s'il est None
            if rechargement.solde_restant is None:
                rechargement.solde_restant = rechargement.montant_ttc
                rechargement.save()
            solde_carte = rechargement.solde_restant
            solde_formate = f"{solde_carte:,} FCFA".replace(",", " ")
    elif demande.rechargement_ttc:
        rechargement = demande.rechargement_ttc
        if rechargement:
            carte_carburant = rechargement.carte_carburant
            # Initialiser solde_restant s'il est None
            if rechargement.solde_restant is None:
                rechargement.solde_restant = rechargement.montant_ttc
                rechargement.save()
            solde_carte = rechargement.solde_restant
            solde_formate = f"{solde_carte:,} FCFA".replace(",", " ")
    
    # Si aucun solde n'a été trouvé, utiliser l'ancien solde
    if solde_carte is None and demande.ancien_solde_carte:
        solde_carte = demande.ancien_solde_carte
        from core.models import Achat_Stock_Carburant_HT
        solde_formate = Achat_Stock_Carburant_HT.format_montant(solde_carte)
    
    return render(request, 'core/demandes_carte_carburant/cloture.html', {
        'form': form,
        'demande': demande,
        'solde_carte': solde_carte,
        'solde_formate': solde_formate,
        'title': f'Clôturer la demande #{demande.id_demande}',
        'safe': True
    })

@login_required
def demande_carte_carburant_delete(request, pk):
    """
    Vue pour supprimer une demande de carte carburant
    """
    try:
        demande = Demande_Carte_Carburant.objects.get(pk=pk)
    except Demande_Carte_Carburant.DoesNotExist:
        messages.error(request, "La demande spécifiée n'existe pas.")
        return redirect('demandes_carte_carburant_list')
    
    # Vérifier les permissions
    if demande.utilisateur_demandeur != request.user and not request.user.groupe.filter(nom_groupe='Gestionnaire Carburant').exists():
        messages.error(request, "Vous n'êtes pas autorisé à supprimer cette demande.")
        return redirect('demandes_carte_carburant_list')
    
    # Empêcher la suppression des demandes acceptées
    if demande.statut_demande == 'Acceptée':
        messages.error(request, "Les demandes acceptées ne peuvent pas être supprimées.")
        return redirect('demande_carte_carburant_detail', pk=pk)
    
    if request.method == 'POST':
        demande.delete()
        messages.success(request, "La demande a été supprimée avec succès.")
        return redirect('demandes_carte_carburant_list')
    
    return render(request, 'core/demandes_carte_carburant/delete.html', {
        'demande': demande,
        'title': f'Supprimer la demande #{demande.id_demande}',
        'safe': True
    })

# Fonction temporaire pour éviter les erreurs de NoReverseMatch
def rapport_mensuel_consommation(request):
    from django.shortcuts import render
    context = {
        'title': 'Rapport Mensuel de Consommation',
        'dotations': [],
        'date_debut': None,
        'dotation': {'libelle': 'Non disponible', 'id_achat_stock_carburant_ht': None}
    }
    return render(request, 'core/rapports/rapport_mensuel_form.html', context)

@login_required
def suivi_dotations(request):
    """
    Vue pour suivre l'utilisation des dotations de carburant (HT et TTC)
    """
    # Vérifier les permissions
    if not request.user.groupe.filter(nom_groupe='Gestionnaire Carburant').exists():
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return redirect('home')
    
    # Récupérer les achats HT avec calcul du montant utilisé et du pourcentage
    achats_ht = Achat_Stock_Carburant_HT.objects.all().order_by('-date_achat')
    for achat in achats_ht:
        # Calculer le montant utilisé via les rechargements de cartes
        montant_utilise = Rechargement_Carte_Carburant_HT.objects.filter(
            achat_stock_carburant_ht=achat
        ).aggregate(total=Sum('montant_ttc'))['total'] or 0
        
        achat.montant_utilise = montant_utilise
        achat.solde_restant = achat.montant_ttc - montant_utilise
        achat.pourcentage_utilisation = round((montant_utilise / achat.montant_ttc) * 100) if achat.montant_ttc > 0 else 0
    
    # Récupérer les achats TTC avec calcul du montant utilisé et du pourcentage
    achats_ttc = Achat_Carburant_TTC.objects.all().order_by('-date_achat')
    for achat in achats_ttc:
        # Calculer le montant utilisé via les rechargements de cartes
        montant_utilise = Rechargement_Carte_Carburant_TTC.objects.filter(
            achat_carburant_ttc=achat
        ).aggregate(total=Sum('montant_ttc'))['total'] or 0
        
        achat.montant_utilise = montant_utilise
        achat.solde_restant = achat.montant_ttc - montant_utilise
        achat.pourcentage_utilisation = round((montant_utilise / achat.montant_ttc) * 100) if achat.montant_ttc > 0 else 0
    
    return render(request, 'core/dotations/suivi_dotations.html', {
        'achats_ht': achats_ht,
        'achats_ttc': achats_ttc,
        'title': 'Suivi des dotations de carburant',
        'safe': True
    })

@login_required
def get_cartes_by_dotation(request):
    """
    Vue AJAX pour obtenir les cartes carburant disponibles en fonction de la dotation sélectionnée
    """
    if request.method == 'GET' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        dotation_source = request.GET.get('dotation_source', '')
        service_id = request.GET.get('service_id', None)
        
        if not service_id:
            return JsonResponse({'error': 'Paramètre service_id manquant'}, status=400)
        
        try:
            service = Service.objects.get(pk=service_id)
        except Service.DoesNotExist:
            return JsonResponse({'error': 'Service non trouvé'}, status=404)
        
        cartes = []
        
        # Traiter la dotation sélectionnée si elle est fournie
        if dotation_source.startswith('HT_'):
            dotation_id = int(dotation_source.split('_')[1])
            try:
                dotation = Achat_Stock_Carburant_HT.objects.get(pk=dotation_id)
                # Récupérer UNIQUEMENT les cartes qui ont été rechargées à partir de cette dotation
                rechargements = Rechargement_Carte_Carburant_HT.objects.filter(
                    achat_stock_carburant_ht=dotation
                )
                
                # Récupérer les IDs des cartes rechargées
                cartes_rechargees_ids = rechargements.values_list('carte_carburant', flat=True).distinct()
                
                # Récupérer uniquement les cartes qui ont été rechargées avec cette dotation
                if cartes_rechargees_ids:
                    cartes_query = Carte_Carburant.objects.filter(
                        id_carte_carburant__in=cartes_rechargees_ids,
                        service=service,
                        statut='Disponible'
                    ).order_by('numero_carte')
                    
                    # Préparer les données des cartes avec le solde correct
                    for carte in cartes_query:
                        # Récupérer le montant du rechargement pour cette carte et cette dotation
                        rechargement = rechargements.filter(carte_carburant=carte).first()
                        if not rechargement:
                            continue
                        
                        # Utiliser le solde restant du rechargement comme solde
                        solde = rechargement.solde_restant if rechargement.solde_restant is not None else rechargement.montant_ttc
                        cartes.append({
                            'id': carte.id_carte_carburant,
                            'text': f"{carte.numero_carte} - Solde: {solde:,} FCFA".replace(",", " ")
                        })
                
            except Achat_Stock_Carburant_HT.DoesNotExist:
                return JsonResponse({'error': 'Dotation non trouvée'}, status=404)
        elif dotation_source.startswith('TTC_'):
            dotation_id = int(dotation_source.split('_')[1])
            try:
                dotation = Achat_Carburant_TTC.objects.get(pk=dotation_id)
                # Récupérer UNIQUEMENT les cartes qui ont été rechargées à partir de cette dotation
                rechargements = Rechargement_Carte_Carburant_TTC.objects.filter(
                    achat_carburant_ttc=dotation
                )
                
                # Récupérer les IDs des cartes rechargées
                cartes_rechargees_ids = rechargements.values_list('carte_carburant', flat=True).distinct()
                
                # Récupérer uniquement les cartes qui ont été rechargées avec cette dotation
                if cartes_rechargees_ids:
                    cartes_query = Carte_Carburant.objects.filter(
                        id_carte_carburant__in=cartes_rechargees_ids,
                        service=service,
                        statut='Disponible'
                    ).order_by('numero_carte')
                    
                    # Préparer les données des cartes avec le solde correct
                    for carte in cartes_query:
                        # Récupérer le montant du rechargement pour cette carte et cette dotation
                        rechargement = rechargements.filter(carte_carburant=carte).first()
                        if not rechargement:
                            continue
                        
                        # Utiliser le montant du rechargement comme solde
                        solde = rechargement.montant_ttc
                        cartes.append({
                            'id': carte.id_carte_carburant,
                            'text': f"{carte.numero_carte} - Solde: {solde:,} FCFA".replace(",", " ")
                        })
                
            except Achat_Carburant_TTC.DoesNotExist:
                return JsonResponse({'error': 'Dotation non trouvée'}, status=404)
        else:
            # Si aucune dotation n'est sélectionnée, récupérer toutes les cartes disponibles du service
            cartes_query = Carte_Carburant.objects.filter(
                service=service,
                statut='Disponible'
            ).order_by('numero_carte')
            
            # Préparer les données des cartes
            for carte in cartes_query:
                cartes.append({
                    'id': carte.id_carte_carburant,
                    'text': f"{carte.numero_carte} - Solde: {carte.format_solde()}"
                })
        
        return JsonResponse({'cartes': cartes})
    
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

@login_required
def telecharger_fiche_ravitaillement(request, pk):
    """Vue pour télécharger la fiche de ravitaillement d'une demande"""
    try:
        demande = Demande_Carte_Carburant.objects.get(pk=pk)
        
        # Vérifier si l'utilisateur a le droit d'accéder à cette demande
        is_gestionnaire_carburant = request.user.groupe.filter(nom_groupe='Gestionnaire Carburant').exists()
        is_same_service = request.user.service.filter(id_service=demande.service.id_service).exists()
        
        if not (is_gestionnaire_carburant or request.user == demande.utilisateur_demandeur or is_same_service):
            return HttpResponseForbidden("Vous n'avez pas l'autorisation d'accéder à cette ressource.")
        
        # Vérifier si la fiche existe
        if not demande.fiche_ravitaillement:
            # Générer la fiche de ravitaillement en PDF
            fiche_html = render_to_string('core/demandes_carte_carburant/fiche_ravitaillement.html', {
                'demande': demande,
                # S'assurer que la carte carburant est définie
                'carte_carburant': demande.get_carte_carburant,
                'service': demande.service,
                'vehicule': demande.vehicule,
            })
            
            # Créer un fichier PDF temporaire
            pdf_file = BytesIO()
            pisa.CreatePDF(fiche_html, dest=pdf_file)
            
            # Sauvegarder le PDF dans le champ fiche_ravitaillement
            pdf_file.seek(0)
            demande.fiche_ravitaillement.save(
                f'fiche_ravitaillement_{demande.id_demande}.pdf',
                ContentFile(pdf_file.read()),
                save=False
            )
            
            demande.save()
            
            # Recharger la demande pour obtenir le chemin du fichier mis à jour
            demande.refresh_from_db()
        
        # Ouvrir le fichier pour le téléchargement
        response = FileResponse(
            demande.fiche_ravitaillement.open('rb'),
            content_type='application/pdf'
        )
        response['Content-Disposition'] = f'attachment; filename="fiche_ravitaillement_{demande.id_demande}.pdf"'
        return response
    
    except Demande_Carte_Carburant.DoesNotExist:
        raise Http404("La demande spécifiée n'existe pas.")
    except Exception as e:
        return HttpResponseServerError(f"Une erreur s'est produite lors de la génération de la fiche: {str(e)}")

@login_required
def regenerer_fiche_ravitaillement(request, pk):
    """
    Vue pour régénérer la fiche de ravitaillement d'une demande existante
    """
    try:
        # Récupérer la demande avec toutes ses relations
        demande = Demande_Carte_Carburant.objects.select_related(
            'vehicule', 'service', 'utilisateur_demandeur', 'utilisateur_traitant',
            'rechargement_ht', 'rechargement_ttc'
        ).get(pk=pk)
        
        # Vérifier si l'utilisateur a le droit d'accéder à cette demande
        is_gestionnaire_carburant = request.user.groupe.filter(nom_groupe='Gestionnaire Carburant').exists()
        is_same_service = request.user.service.filter(id_service=demande.service.id_service).exists()
        
        if not (is_gestionnaire_carburant or request.user == demande.utilisateur_demandeur or is_same_service):
            messages.error(request, "Vous n'avez pas l'autorisation d'accéder à cette ressource.")
            return redirect('demande_carte_carburant_detail', pk=pk)
        
        # Vérifier que la demande est close
        if demande.statut_demande != 'Close':
            messages.error(request, "La fiche de ravitaillement ne peut être régénérée que pour une demande clôturée.")
            return redirect('demande_carte_carburant_detail', pk=pk)
        
        # Vérifier que les champs nécessaires sont remplis
        if not demande.montant_ttc or not demande.volume:
            messages.error(request, "Les informations de ravitaillement sont incomplètes. Impossible de régénérer la fiche.")
            return redirect('demande_carte_carburant_detail', pk=pk)
        
        # Récupérer le rechargement et la carte associés à la demande
        rechargement = None
        carte = None
        
        if demande.rechargement_ht:
            rechargement = demande.rechargement_ht
            carte = rechargement.carte_carburant
        elif demande.rechargement_ttc:
            rechargement = demande.rechargement_ttc
            carte = rechargement.carte_carburant
        
        # S'assurer que la carte carburant est définie
        if carte is None and hasattr(demande, 'get_carte_carburant') and demande.get_carte_carburant:
            carte = demande.get_carte_carburant
        
        # Régénérer la fiche de ravitaillement en PDF
        # Préparer le contexte avec toutes les valeurs nécessaires
        context = {
            'demande': demande,
            'carte_carburant': carte,
            'service': demande.service,
            'vehicule': demande.vehicule,
        }
        
        fiche_html = render_to_string('core/demandes_carte_carburant/fiche_ravitaillement.html', context)
        
        # Créer un fichier PDF temporaire
        pdf_file = BytesIO()
        pisa.CreatePDF(fiche_html, dest=pdf_file)
        
        # Supprimer l'ancien PDF s'il existe
        if demande.fiche_ravitaillement:
            try:
                storage, path = demande.fiche_ravitaillement.storage, demande.fiche_ravitaillement.path
                if storage.exists(path):
                    storage.delete(path)
            except Exception as e:
                # Continuer même si la suppression échoue
                pass
        
        # Sauvegarder le PDF dans le champ fiche_ravitaillement
        pdf_file.seek(0)
        demande.fiche_ravitaillement.save(
            f'fiche_ravitaillement_{demande.id_demande}.pdf',
            ContentFile(pdf_file.read()),
            save=True
        )
        
        demande.save()
        
        messages.success(request, "La fiche de ravitaillement a été régénérée avec succès.")
        return redirect('demande_carte_carburant_detail', pk=pk)
    
    except Demande_Carte_Carburant.DoesNotExist:
        messages.error(request, "La demande spécifiée n'existe pas.")
        return redirect('demandes_carte_carburant_list')
    except Exception as e:
        messages.error(request, f"Une erreur s'est produite lors de la régénération de la fiche: {str(e)}")
        return redirect('demande_carte_carburant_detail', pk=pk)

@login_required
def dotation_detail(request, dotation_type, dotation_id):
    """
    Vue pour afficher les détails d'une dotation spécifique
    """
    # Vérifier les permissions
    if not request.user.groupe.filter(nom_groupe='Gestionnaire Carburant').exists():
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return redirect('home')
    
    dotation = None
    rechargements = []
    demandes_list = []
    montant_utilise = 0
    solde_restant = 0
    pourcentage_utilisation = 0
    total_volume = 0
    
    if dotation_type == 'ht':
        try:
            dotation = Achat_Stock_Carburant_HT.objects.get(id_achat_stock_carburant_ht=dotation_id)
            
            # Récupérer les rechargements associés
            rechargements = Rechargement_Carte_Carburant_HT.objects.filter(achat_stock_carburant_ht=dotation).order_by('-date_rechargement')
            
            # Calculer le montant utilisé
            montant_utilise = rechargements.aggregate(total=Sum('montant_ttc'))['total'] or 0
            total_volume = rechargements.aggregate(total=Sum('volume'))['total'] or 0
            
            # Récupérer les demandes associées
            demandes_list = Demande_Carte_Carburant.objects.filter(rechargement_ht__achat_stock_carburant_ht=dotation).order_by('-date_demande')
            
        except Achat_Stock_Carburant_HT.DoesNotExist:
            messages.error(request, "La dotation spécifiée n'existe pas.")
            return redirect('suivi_dotations')
    
    elif dotation_type == 'ttc':
        try:
            dotation = Achat_Carburant_TTC.objects.get(id_achat_carburant_ttc=dotation_id)
            
            # Récupérer les rechargements associés
            rechargements = Rechargement_Carte_Carburant_TTC.objects.filter(achat_carburant_ttc=dotation).order_by('-date_rechargement')
            
            # Calculer le montant utilisé
            montant_utilise = rechargements.aggregate(total=Sum('montant_ttc'))['total'] or 0
            total_volume = rechargements.aggregate(total=Sum('volume'))['total'] or 0
            
            # Récupérer les demandes associées
            demandes_list = Demande_Carte_Carburant.objects.filter(rechargement_ttc__achat_carburant_ttc=dotation).order_by('-date_demande')
            
        except Achat_Carburant_TTC.DoesNotExist:
            messages.error(request, "La dotation spécifiée n'existe pas.")
            return redirect('suivi_dotations')
    
    else:
        messages.error(request, "Type de dotation invalide.")
        return redirect('suivi_dotations')
    
    # Calculer les statistiques
    solde_restant = dotation.montant_ttc - montant_utilise
    pourcentage_utilisation = round((montant_utilise / dotation.montant_ttc) * 100) if dotation.montant_ttc > 0 else 0
    
    # Pagination des demandes - 10 par page
    paginator = Paginator(demandes_list, 10)
    page_number = request.GET.get('page')
    demandes = paginator.get_page(page_number)
    
    # Calculer le solde des rechargements de cartes
    total_rechargements = rechargements.aggregate(total=Sum('montant_ttc'))['total'] or 0
    total_demandes_ravitaillement = demandes_list.filter(statut_demande__in=['Acceptée', 'Close']).aggregate(total=Sum('montant_ttc'))['total'] or 0
    solde_rechargements = total_rechargements - total_demandes_ravitaillement
    
    return render(request, 'core/dotations/dotation_detail.html', {
        'dotation': dotation,
        'dotation_type': dotation_type,
        'rechargements': rechargements,
        'demandes': demandes,
        'demandes_list': demandes_list,  # Pour les calculs qui nécessitent toutes les demandes
        'montant_utilise': montant_utilise,
        'solde_restant': solde_restant,
        'pourcentage_utilisation': pourcentage_utilisation,
        'total_volume': total_volume,
        'total_rechargements': total_rechargements,
        'total_demandes_ravitaillement': total_demandes_ravitaillement,
        'solde_rechargements': solde_rechargements,
        'title': f'Détails de la dotation: {dotation.libelle}',
        'safe': True
    })

@login_required
def releve_consommation_carburant(request):
    """
    Vue pour générer un relevé de consommation de carburant pour une dotation et un mois donnés
    """
    # Vérifier les permissions
    if not request.user.groupe.filter(nom_groupe='Gestionnaire Carburant').exists():
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return redirect('home')
    
    # Préparer les données des dotations pour le formulaire
    dotations_ht = Achat_Stock_Carburant_HT.objects.all().order_by('-date_achat')
    dotations_ttc = Achat_Carburant_TTC.objects.all().order_by('-date_achat')
    
    # Convertir les dotations en JSON pour JavaScript
    dotations_ht_json = json.dumps([{
        'id': dotation.id_achat_stock_carburant_ht,
        'libelle': dotation.libelle,
        'montant_ttc': float(dotation.montant_ttc)
    } for dotation in dotations_ht])
    
    dotations_ttc_json = json.dumps([{
        'id': dotation.id_achat_carburant_ttc,
        'libelle': dotation.libelle,
        'montant_ttc': float(dotation.montant_ttc)
    } for dotation in dotations_ttc])
    
    # Si la méthode est POST, générer le relevé
    if request.method == 'POST':
        # Récupérer les données du formulaire
        dotation_type = request.POST.get('dotation_type')
        dotation_id = request.POST.get('dotation_id')
        mois = int(request.POST.get('mois'))
        annee = int(request.POST.get('annee'))
        service_id = request.POST.get('service')
        
        # Convertir les variables
        dotation_id = int(dotation_id)
        mois = int(mois)
        annee = int(annee)

        try:
            context = build_releve_consommation_context(
                dotation_type=dotation_type,
                dotation_id=dotation_id,
                mois=mois,
                annee=annee,
                service_id=service_id,
            )
            return render(request, 'core/dotations/releve_consommation.html', context)
        except Exception as e:
            messages.error(request, str(e))
            return redirect('suivi_dotations')
        
        # Déterminer les dates de début et fin du mois
        import datetime
        from calendar import monthrange
        
        debut_mois = datetime.date(annee, mois, 1)
        _, nb_jours = monthrange(annee, mois)
        fin_mois = datetime.date(annee, mois, nb_jours)
        
        dotation = None
        rechargements = []
        cartes = []
        soldes_ouverture = {}
        consommations = {}
        soldes_cloture = {}
        total_volume_ouverture = 0
        total_montant_ouverture = 0
        total_volume_consommation = 0
        total_montant_consommation = 0
        total_volume_cloture = 0
        total_montant_cloture = 0
        service_obj = None
        
        if service_id:
            try:
                service_obj = Service.objects.get(pk=service_id)
            except Service.DoesNotExist:
                messages.error(request, "Le service spécifié n'existe pas.")
                return redirect('suivi_dotations')
        
        if dotation_type == 'ht':
            try:
                dotation = Achat_Stock_Carburant_HT.objects.get(pk=dotation_id)
                rechargements = Rechargement_Carte_Carburant_HT.objects.filter(achat_stock_carburant_ht=dotation)
                
                # Récupérer toutes les cartes associées
                cartes_query = Carte_Carburant.objects.filter(rechargements_ht__achat_stock_carburant_ht=dotation)
                
                # Filtrer par service si spécifié
                if service_obj:
                    cartes_query = cartes_query.filter(vehicule__service=service_obj)
                
                cartes = cartes_query.distinct()
                
                for carte in cartes:
                    # Trouver le rechargement associé à cette carte
                    rechargement = rechargements.filter(carte_carburant=carte).first()
                    if not rechargement:
                        continue
                    
                    # Calculer le solde d'ouverture (avant le premier ravitaillement du mois)
                    demandes_avant_mois = Demande_Carte_Carburant.objects.filter(rechargement_ht=rechargement, date_ravitaillement__lt=debut_mois).order_by('-date_ravitaillement')
                    
                    # Si aucune demande avant le mois, le solde d'ouverture est le montant total du rechargement
                    if not demandes_avant_mois.exists():
                        solde_ouverture_montant = rechargement.montant_ttc
                        solde_ouverture_volume = rechargement.volume
                    else:
                        # Sinon, c'est le solde après la dernière demande avant le mois
                        derniere_demande = demandes_avant_mois.first()
                        solde_ouverture_montant = derniere_demande.nouveau_solde_carte or 0
                        # Calculer le volume restant proportionnellement au montant
                        ratio = solde_ouverture_montant / rechargement.montant_ttc if rechargement.montant_ttc > 0 else 0
                        # Conversion sécuritaire via string
                        from decimal import Decimal
                        ratio_decimal = Decimal(str(ratio))
                        solde_ouverture_volume = rechargement.volume * ratio_decimal
                    
                    # Calculer la consommation pendant le mois
                    demandes_du_mois = Demande_Carte_Carburant.objects.filter(rechargement_ht=rechargement, date_ravitaillement__gte=debut_mois, date_ravitaillement__lte=fin_mois).order_by('date_ravitaillement')
                    
                    volume_consommation = sum(demande.volume or 0 for demande in demandes_du_mois)
                    montant_consommation = sum(demande.montant_ttc or 0 for demande in demandes_du_mois)
                    
                    # Calculer le solde de clôture
                    solde_cloture_montant = solde_ouverture_montant - montant_consommation
                    solde_cloture_volume = solde_ouverture_volume - volume_consommation
                    
                    # Stocker les résultats
                    soldes_ouverture[carte.numero_carte] = {
                        'volume': solde_ouverture_volume,
                        'montant': solde_ouverture_montant
                    }
                    consommations[carte.numero_carte] = {
                        'volume': volume_consommation,
                        'montant': montant_consommation
                    }
                    soldes_cloture[carte.numero_carte] = {
                        'volume': solde_cloture_volume,
                        'montant': solde_cloture_montant
                    }
                    
                    # Ajouter aux totaux
                    total_volume_ouverture += solde_ouverture_volume
                    total_montant_ouverture += solde_ouverture_montant
                    total_volume_consommation += volume_consommation
                    total_montant_consommation += montant_consommation
                    total_volume_cloture += solde_cloture_volume
                    total_montant_cloture += solde_cloture_montant
                
            except Achat_Stock_Carburant_HT.DoesNotExist:
                messages.error(request, "La dotation spécifiée n'existe pas.")
                return redirect('suivi_dotations')
        
        elif dotation_type == 'ttc':
            try:
                dotation = Achat_Carburant_TTC.objects.get(pk=dotation_id)
                rechargements = Rechargement_Carte_Carburant_TTC.objects.filter(achat_carburant_ttc=dotation)
                
                # Récupérer toutes les cartes associées
                cartes_query = Carte_Carburant.objects.filter(rechargements_ttc__achat_carburant_ttc=dotation)
                
                # Filtrer par service si spécifié
                if service_obj:
                    cartes_query = cartes_query.filter(vehicule__service=service_obj)
                
                cartes = cartes_query.distinct()
                
                for carte in cartes:
                    # Trouver le rechargement associé à cette carte
                    rechargement = rechargements.filter(carte_carburant=carte).first()
                    if not rechargement:
                        continue
                    
                    # Calculer le solde d'ouverture (avant le premier ravitaillement du mois)
                    demandes_avant_mois = Demande_Carte_Carburant.objects.filter(rechargement_ttc=rechargement, date_ravitaillement__lt=debut_mois).order_by('-date_ravitaillement')
                    
                    # Si aucune demande avant le mois, le solde d'ouverture est le montant total du rechargement
                    if not demandes_avant_mois.exists():
                        solde_ouverture_montant = rechargement.montant_ttc
                        solde_ouverture_volume = rechargement.volume
                    else:
                        # Sinon, c'est le solde après la dernière demande avant le mois
                        derniere_demande = demandes_avant_mois.first()
                        solde_ouverture_montant = derniere_demande.nouveau_solde_carte or 0
                        # Calculer le volume restant proportionnellement au montant
                        ratio = solde_ouverture_montant / rechargement.montant_ttc if rechargement.montant_ttc > 0 else 0
                        # Conversion sécuritaire via string
                        from decimal import Decimal
                        ratio_decimal = Decimal(str(ratio))
                        solde_ouverture_volume = rechargement.volume * ratio_decimal
                    
                    # Calculer la consommation pendant le mois
                    demandes_du_mois = Demande_Carte_Carburant.objects.filter(rechargement_ttc=rechargement, date_ravitaillement__gte=debut_mois, date_ravitaillement__lte=fin_mois).order_by('date_ravitaillement')
                    
                    volume_consommation = sum(demande.volume or 0 for demande in demandes_du_mois)
                    montant_consommation = sum(demande.montant_ttc or 0 for demande in demandes_du_mois)
                    
                    # Calculer le solde de clôture
                    solde_cloture_montant = solde_ouverture_montant - montant_consommation
                    solde_cloture_volume = solde_ouverture_volume - volume_consommation
                    
                    # Stocker les résultats
                    soldes_ouverture[carte.numero_carte] = {
                        'volume': solde_ouverture_volume,
                        'montant': solde_ouverture_montant
                    }
                    consommations[carte.numero_carte] = {
                        'volume': volume_consommation,
                        'montant': montant_consommation
                    }
                    soldes_cloture[carte.numero_carte] = {
                        'volume': solde_cloture_volume,
                        'montant': solde_cloture_montant
                    }
                    
                    # Ajouter aux totaux
                    total_volume_ouverture += solde_ouverture_volume
                    total_montant_ouverture += solde_ouverture_montant
                    total_volume_consommation += volume_consommation
                    total_montant_consommation += montant_consommation
                    total_volume_cloture += solde_cloture_volume
                    total_montant_cloture += solde_cloture_montant
                
            except Achat_Carburant_TTC.DoesNotExist:
                messages.error(request, "La dotation spécifiée n'existe pas.")
                return redirect('suivi_dotations')
        
        else:
            messages.error(request, "Type de dotation invalide.")
            return redirect('suivi_dotations')
        
        # Formater les noms de mois
        nom_mois = f"{get_french_month_name(mois)} {annee}"
        
        # Rendre le template avec les données calculées
        return render(request, 'core/dotations/releve_consommation.html', {
            'dotation': dotation,
            'dotation_type': dotation_type,
            'mois': nom_mois,
            'cartes': cartes,
            'service': service_obj,
            'soldes_ouverture': soldes_ouverture,
            'consommations': consommations,
            'soldes_cloture': soldes_cloture,
            'total_volume_ouverture': total_volume_ouverture,
            'total_montant_ouverture': total_montant_ouverture,
            'total_volume_consommation': total_volume_consommation,
            'total_montant_consommation': total_montant_consommation,
            'total_volume_cloture': total_volume_cloture,
            'total_montant_cloture': total_montant_cloture,
            'title': f'Relevé de consommation de carburant - {nom_mois}',
            'safe': True
        })
    
    # Si la méthode est GET, afficher le formulaire
    # Récupérer tous les services pour le formulaire
    services = Service.objects.all().order_by('nom_service')
    
    return render(request, 'core/dotations/releve_consommation_form.html', {
        'dotations_ht_json': dotations_ht_json,
        'dotations_ttc_json': dotations_ttc_json,
        'services': services,
        'title': 'Générer un relevé de consommation de carburant'
    })

@login_required
@user_passes_test(lambda u: u.groupe.filter(nom_groupe__in=['Administrateur', 'Gestionnaire Carburant']).exists())
def dashboard_carburant(request):
    """
    Vue pour le tableau de bord carburant
    Affiche les statistiques suivantes:
    - Estimation de la consommation par 100 km pour les véhicules
    - Tendances d'utilisation des rechargements de carte
    - Statut de consommation des véhicules (Plus, Moins, Moyenne)
    - Âge des véhicules
    - Véhicules les plus utilisés en fonction des distances parcourues
    """
    # Récupérer tous les véhicules
    vehicules = Vehicule.objects.all()
    
    # Statistiques de consommation par véhicule
    vehicules_stats = []
    for vehicule in vehicules:
        # Récupérer les demandes de carburant pour ce véhicule
        demandes = Demande_Carte_Carburant.objects.filter(vehicule=vehicule, statut_demande='Close', date_ravitaillement__isnull=False, volume__isnull=False).order_by('-date_ravitaillement')
        
        if demandes.exists():
            # Calculer la consommation moyenne
            total_volume = demandes.aggregate(Sum('volume'))['volume__sum'] or 0
            
            # Calculer la distance parcourue entre le premier et dernier ravitaillement
            if demandes.count() > 1:
                premiere_demande = demandes.last()
                derniere_demande = demandes.first()
                if premiere_demande.km_vehicule and derniere_demande.km_vehicule:
                    distance_parcourue = derniere_demande.km_vehicule - premiere_demande.km_vehicule
                    if distance_parcourue > 0:
                        # Consommation aux 100 km
                        consommation_100km = (total_volume / distance_parcourue) * 100
                    else:
                        consommation_100km = None
                else:
                    distance_parcourue = None
                    consommation_100km = None
            else:
                distance_parcourue = None
                consommation_100km = None
            
            # Calculer l'âge du véhicule en années
            age_vehicule = None
            if vehicule.date_mise_en_service:
                today = timezone.now().date()
                delta = today - vehicule.date_mise_en_service
                age_vehicule = delta.days / 365.25  # Approximation en années
            
            vehicules_stats.append({
                'vehicule': vehicule,
                'consommation_100km': consommation_100km,
                'distance_parcourue': distance_parcourue,
                'age_vehicule': age_vehicule,
                'nb_ravitaillements': demandes.count(),
                'dernier_ravitaillement': demandes.first().date_ravitaillement if demandes.exists() else None
            })
    
    # Trier les véhicules par distance parcourue (du plus au moins utilisé)
    vehicules_stats.sort(key=lambda x: x['distance_parcourue'] if x['distance_parcourue'] else 0, reverse=True)
    
    # Calculer la consommation moyenne globale pour déterminer les statuts (Plus, Moins, Moyenne)
    consommations = [v['consommation_100km'] for v in vehicules_stats if v['consommation_100km'] is not None]
    tendances_list = []
    if consommations:
        from decimal import Decimal
        consommation_moyenne = sum(consommations) / len(consommations)
        
        # Déterminer le statut de consommation de chaque véhicule
        for v in vehicules_stats:
            if v['consommation_100km'] is not None:
                # Conversion en Decimal pour éviter les erreurs de type
                if v['consommation_100km'] > consommation_moyenne * Decimal('1.1'):  # 10% au-dessus de la moyenne
                    v['statut_consommation'] = 'Plus'
                elif v['consommation_100km'] < consommation_moyenne * Decimal('0.9'):  # 10% en-dessous de la moyenne
                    v['statut_consommation'] = 'Moins'
                else:
                    v['statut_consommation'] = 'Moyenne'
            else:
                v['statut_consommation'] = None
        
        # Tendances d'utilisation des rechargements de carte par mois
        import calendar
        from datetime import datetime, timedelta
        
        # Récupérer les 12 derniers mois
        today = timezone.now().date()
        start_date = today - timedelta(days=365)  # Un an en arrière
        
        # Rechargements HT
        rechargements_ht = Rechargement_Carte_Carburant_HT.objects.filter(date_rechargement__gte=start_date).order_by('date_rechargement')
        
        # Rechargements TTC
        rechargements_ttc = Rechargement_Carte_Carburant_TTC.objects.filter(date_rechargement__gte=start_date).order_by('date_rechargement')
        
        # Agréger les données par mois
        tendances_mensuelles = {}
        
        for rech in rechargements_ht:
            month_key = f"{calendar.month_name[rech.date_rechargement.month]} {rech.date_rechargement.year}"
            if month_key not in tendances_mensuelles:
                tendances_mensuelles[month_key] = {'volume_ht': 0, 'volume_ttc': 0, 'count_ht': 0, 'count_ttc': 0}
            tendances_mensuelles[month_key]['volume_ht'] += float(rech.volume)
            tendances_mensuelles[month_key]['count_ht'] += 1
        
        for rech in rechargements_ttc:
            month_key = f"{calendar.month_name[rech.date_rechargement.month]} {rech.date_rechargement.year}"
            if month_key not in tendances_mensuelles:
                tendances_mensuelles[month_key] = {'volume_ht': 0, 'volume_ttc': 0, 'count_ht': 0, 'count_ttc': 0}
            tendances_mensuelles[month_key]['volume_ttc'] += float(rech.volume)
            tendances_mensuelles[month_key]['count_ttc'] += 1
        
        # Convertir en liste triée par date
        tendances_list = []
        for month, data in tendances_mensuelles.items():
            month_date = datetime.strptime(month, "%B %Y")
            tendances_list.append({
                'month': month,
                'month_date': month_date,
                'volume_ht': data['volume_ht'],
                'volume_ttc': data['volume_ttc'],
                'count_ht': data['count_ht'],
                'count_ttc': data['count_ttc'],
                'total_volume': data['volume_ht'] + data['volume_ttc'],
                'total_count': data['count_ht'] + data['count_ttc']
            })
        
        tendances_list.sort(key=lambda x: x['month_date'])

    return render(request, 'core/carburant/dashboard.html', {
        'vehicules_stats': vehicules_stats,
        'tendances': tendances_list,
        'title': 'Tableau de bord Carburant'
    })

@login_required
@user_passes_test(lambda u: u.groupe.filter(nom_groupe__in=['Administrateur', 'Gestionnaire Carburant']).exists())
def etat_ravitaillements(request):
    """
    Vue pour afficher l'état multicritère des ravitaillements de carburant
    """
    # Initialiser les variables
    ravitaillements = Demande_Carte_Carburant.objects.filter(
        statut_demande__in=['Acceptée', 'Close'],
        date_ravitaillement__isnull=False
    ).order_by('-date_ravitaillement')
    
    # Filtrage par service de l'utilisateur si non admin
    if not request.user.is_superuser and not request.user.groupe.filter(nom_groupe='Administrateur').exists():
        # Récupérer les services de l'utilisateur (relation many-to-many)
        user_services = request.user.service.all().values_list('id_service', flat=True)
        ravitaillements = ravitaillements.filter(service__id_service__in=user_services)
        # Récupérer uniquement les services de l'utilisateur
        services = Service.objects.filter(id_service__in=user_services).order_by('nom_service')
    else:
        # Pour les administrateurs, tous les services
        services = Service.objects.all().order_by('nom_service')
    
    # Récupérer les listes pour les filtres
    vehicules = Vehicule.objects.all().order_by('immatriculation')
    chauffeurs = Utilisateur.objects.filter(groupe__nom_groupe='Driver').order_by('nom_complet')
    cartes = Carte_Carburant.objects.all().order_by('numero_carte')
    
    # Récupérer les achats de carburant pour le filtre de dotation
    achats_ht = Achat_Stock_Carburant_HT.objects.filter(statut='Ouverte').order_by('-date_achat')
    achats_ttc = Achat_Carburant_TTC.objects.filter(statut='Ouverte').order_by('-date_achat')
    
    # Récupérer les filtres du formulaire
    if request.method == 'POST':
        # 1. Filtrage par date (premier niveau)
        date_debut = request.POST.get('date_debut')
        if date_debut:
            try:
                date_debut = datetime.strptime(date_debut, '%Y-%m-%d').date()
                ravitaillements = ravitaillements.filter(date_ravitaillement__gte=date_debut)
            except ValueError:
                messages.error(request, "Format de date de début invalide")
        
        date_fin = request.POST.get('date_fin')
        if date_fin:
            try:
                date_fin = datetime.strptime(date_fin, '%Y-%m-%d').date()
                ravitaillements = ravitaillements.filter(date_ravitaillement__lte=date_fin)
            except ValueError:
                messages.error(request, "Format de date de fin invalide")
        
        # 2. Filtrage par service (deuxième niveau)
        service_id = request.POST.get('service')
        if service_id and service_id != 'tous':
            ravitaillements = ravitaillements.filter(service__id_service=service_id)
        
        # 3. Filtrage par dotation (troisième niveau)
        dotation = request.POST.get('dotation')
        if dotation and dotation != 'tous':
            if dotation.startswith('ht_'):
                achat_ht_id = dotation.replace('ht_', '')
                try:
                    achat_ht_id = int(achat_ht_id)
                    ravitaillements = ravitaillements.filter(
                        rechargement_ht__isnull=False,
                        rechargement_ht__achat_stock_carburant_ht__id_achat_stock_carburant_ht=achat_ht_id
                    )
                except ValueError:
                    messages.error(request, "ID d'achat HT invalide")
            elif dotation.startswith('ttc_'):
                achat_ttc_id = dotation.replace('ttc_', '')
                try:
                    achat_ttc_id = int(achat_ttc_id)
                    ravitaillements = ravitaillements.filter(
                        rechargement_ttc__isnull=False,
                        rechargement_ttc__achat_carburant_ttc__id_achat_carburant_ttc=achat_ttc_id
                    )
                except ValueError:
                    messages.error(request, "ID d'achat TTC invalide")
        
        # 4. Filtrage par carte carburant (quatrième niveau)
        carte_id = request.POST.get('carte')
        if carte_id and carte_id != 'tous':
            try:
                carte_id = int(carte_id)
                ravitaillements = ravitaillements.filter(
                    Q(rechargement_ht__carte_carburant__id_carte_carburant=carte_id) | 
                    Q(rechargement_ttc__carte_carburant__id_carte_carburant=carte_id)
                )
            except ValueError:
                messages.error(request, "ID de carte invalide")
        
        # 5. Filtrage par véhicule (cinquième niveau)
        vehicule_id = request.POST.get('vehicule')
        if vehicule_id and vehicule_id != 'tous':
            ravitaillements = ravitaillements.filter(vehicule__id_vehicule=vehicule_id)
        
        # 6. Filtrage par chauffeur (sixième niveau)
        chauffeur_id = request.POST.get('chauffeur')
        if chauffeur_id and chauffeur_id != 'tous':
            ravitaillements = ravitaillements.filter(utilisateur_demandeur__id_utilisateur=chauffeur_id)
        
        # Export en PDF ou Excel
        export_format = request.POST.get('export_format')
        if export_format:
            if export_format == 'pdf':
                return export_pdf(request, ravitaillements)
            elif export_format == 'excel':
                return export_excel(request, ravitaillements)
    
    # Calculer les totaux
    total_montant = ravitaillements.aggregate(total=Sum('montant_ttc'))['total'] or 0
    total_volume = ravitaillements.aggregate(total=Sum('volume'))['total'] or 0
    total_ravitaillements = ravitaillements.count()
    
    # Rendre le template avec les données
    return render(request, 'core/carburant/etat_ravitaillements.html', {
        'ravitaillements': ravitaillements,
        'services': services,
        'vehicules': vehicules,
        'chauffeurs': chauffeurs,
        'cartes': cartes,
        'achats_ht': achats_ht,
        'achats_ttc': achats_ttc,
        'total_montant': total_montant,
        'total_volume': total_volume,
        'total_ravitaillements': total_ravitaillements,
        'title': 'État des ravitaillements de carburant'
    })

def export_pdf(request, ravitaillements):
    """
    Exporte les ravitaillements au format PDF
    """
    # Calculer les totaux
    total_montant = ravitaillements.aggregate(total=Sum('montant_ttc'))['total'] or 0
    total_volume = ravitaillements.aggregate(total=Sum('volume'))['total'] or 0
    total_ravitaillements = ravitaillements.count()
    
    # Préparer le contexte pour le template PDF
    context = {
        'ravitaillements': ravitaillements,
        'total_montant': total_montant,
        'total_volume': total_volume,
        'total_ravitaillements': total_ravitaillements,
        'date_generation': timezone.now(),
        'utilisateur': request.user.nom_complet,
    }
    
    # Générer le PDF
    output_filename = f"etat_ravitaillements_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf_path = generate_pdf_from_template('core/carburant/etat_ravitaillements_pdf.html', context, output_filename)
    
    if pdf_path:
        with open(pdf_path, 'rb') as pdf_file:
            response = HttpResponse(pdf_file.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{output_filename}"'
            return response
    else:
        messages.error(request, "Erreur lors de la génération du PDF")
        return redirect('etat_ravitaillements')

def export_excel(request, ravitaillements):
    """
    Exporte les ravitaillements au format Excel
    """
    # Créer un buffer pour stocker le fichier Excel
    output = io.BytesIO()
    
    # Créer un classeur Excel et une feuille
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet('Ravitaillements')
    
    # Ajouter des styles
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#4472C4',
        'font_color': 'white',
        'align': 'center',
        'valign': 'vcenter',
        'border': 1
    })
    
    date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})
    number_format = workbook.add_format({'num_format': '# ##0'})
    
    # Définir les en-têtes
    headers = [
        'ID', 'Date ravitaillement', 'Service', 'Véhicule', 'Chauffeur', 
        'Carte', 'Station', 'Volume (L)', 'Montant (FCFA)', 'Kilométrage'
    ]
    
    # Écrire les en-têtes
    for col, header in enumerate(headers):
        worksheet.write(0, col, header, header_format)
    
    # Style pour les données
    font_style = workbook.add_format({
        'align': 'left',
        'valign': 'vcenter',
        'border': 1
    })
    
    # Écrire les données
    for row, ravitaillement in enumerate(ravitaillements, start=1):
        worksheet.write(row, 0, ravitaillement.id_demande, font_style)
        worksheet.write_datetime(row, 1, ravitaillement.date_ravitaillement, date_format)
        worksheet.write(row, 2, ravitaillement.service.nom_service, font_style)
        worksheet.write(row, 3, str(ravitaillement.vehicule), font_style)
        worksheet.write(row, 4, ravitaillement.utilisateur_demandeur.nom_complet, font_style)
        
        # Obtenir le numéro de carte
        carte = ravitaillement.get_carte_carburant
        worksheet.write(row, 5, carte.numero_carte if carte else '', font_style)
        
        worksheet.write(row, 6, ravitaillement.station_service or '', font_style)
        worksheet.write_number(row, 7, float(ravitaillement.volume or 0), number_format)
        worksheet.write_number(row, 8, ravitaillement.montant_ttc or 0, number_format)
        worksheet.write_number(row, 9, ravitaillement.km_vehicule or 0, number_format)
    
    # Calculer les totaux
    total_row = len(ravitaillements) + 2
    worksheet.write(total_row, 6, 'TOTAL', header_format)
    worksheet.write_formula(total_row, 7, f'=SUM(H2:H{total_row-1})', number_format)
    worksheet.write_formula(total_row, 8, f'=SUM(I2:I{total_row-1})', number_format)
    
    # Ajuster la largeur des colonnes
    for i, width in enumerate([10, 18, 20, 20, 25, 15, 20, 15, 20, 15]):
        worksheet.set_column(i, i, width)
    
    # Fermer le classeur
    workbook.close()
    
    # Préparer la réponse
    output.seek(0)
    filename = f"etat_ravitaillements_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    response = HttpResponse(
        output,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response

@login_required
@user_passes_test(lambda u: u.groupe.filter(nom_groupe__in=['Administrateur', 'Gestionnaire Carburant']).exists())
def get_cartes_by_dotation(request):
    """API pour obtenir les cartes disponibles en fonction d'une dotation."""
    dotation_source = request.GET.get('dotation_source') or request.GET.get('dotation', '')
    service_id = request.GET.get('service_id')

    # Compatibilité legacy: paramètres ht_/ttc_
    if isinstance(dotation_source, str) and dotation_source.startswith('ht_'):
        dotation_source = f"HT_{dotation_source.replace('ht_', '')}"
    elif isinstance(dotation_source, str) and dotation_source.startswith('ttc_'):
        dotation_source = f"TTC_{dotation_source.replace('ttc_', '')}"

    if dotation_source in ('tous', None):
        dotation_source = ''

    # Compatibilité: si service_id absent, utiliser le premier service de l'utilisateur
    if not service_id:
        user_service = request.user.service.first()
        service_id = user_service.id_service if user_service else None

    if not service_id:
        return JsonResponse({'error': 'Paramètre service_id manquant'}, status=400)

    try:
        service = Service.objects.get(pk=service_id)
    except Service.DoesNotExist:
        return JsonResponse({'error': 'Service non trouvé'}, status=404)

    cartes = []

    if isinstance(dotation_source, str) and dotation_source.startswith('HT_'):
        dotation_id = int(dotation_source.split('_')[1])
        try:
            dotation = Achat_Stock_Carburant_HT.objects.get(pk=dotation_id)
            rechargements = Rechargement_Carte_Carburant_HT.objects.filter(
                achat_stock_carburant_ht=dotation,
                carte_carburant__service=service,
                carte_carburant__statut='Disponible',
            ).select_related('carte_carburant')

            for rechargement in rechargements:
                solde = rechargement.solde_restant if rechargement.solde_restant is not None else rechargement.montant_ttc
                cartes.append({
                    'id': rechargement.carte_carburant.id_carte_carburant,
                    'text': f"{rechargement.carte_carburant.numero_carte} - Solde: {solde:,} FCFA".replace(',', ' '),
                    'numero': rechargement.carte_carburant.numero_carte,
                })
        except Achat_Stock_Carburant_HT.DoesNotExist:
            return JsonResponse({'error': 'Dotation non trouvée'}, status=404)

    elif isinstance(dotation_source, str) and dotation_source.startswith('TTC_'):
        dotation_id = int(dotation_source.split('_')[1])
        try:
            dotation = Achat_Carburant_TTC.objects.get(pk=dotation_id)
            rechargements = Rechargement_Carte_Carburant_TTC.objects.filter(
                achat_carburant_ttc=dotation,
                carte_carburant__service=service,
                carte_carburant__statut='Disponible',
            ).select_related('carte_carburant')

            for rechargement in rechargements:
                solde = rechargement.solde_restant if rechargement.solde_restant is not None else rechargement.montant_ttc
                cartes.append({
                    'id': rechargement.carte_carburant.id_carte_carburant,
                    'text': f"{rechargement.carte_carburant.numero_carte} - Solde: {solde:,} FCFA".replace(',', ' '),
                    'numero': rechargement.carte_carburant.numero_carte,
                })
        except Achat_Carburant_TTC.DoesNotExist:
            return JsonResponse({'error': 'Dotation non trouvée'}, status=404)
    else:
        cartes_query = Carte_Carburant.objects.filter(
            service=service,
            statut='Disponible',
        ).order_by('numero_carte')

        for carte in cartes_query:
            cartes.append({
                'id': carte.id_carte_carburant,
                'text': f"{carte.numero_carte} - Solde: {carte.format_solde()}",
                'numero': carte.numero_carte,
            })

    cartes_ids = [item['id'] for item in cartes]
    cartes_data = [{'id': item['id'], 'numero': item['numero']} for item in cartes]
    return JsonResponse({'cartes': cartes, 'cartes_ids': cartes_ids, 'cartes_data': cartes_data})

# Views pour les Types de Maintenance
class TypeMaintenanceListView(LoginRequiredMixin, ListView):
    model = TypeMaintenance
    template_name = 'core/type_maintenance/list.html'
    context_object_name = 'types_maintenance'
    ordering = ['libelle']
    
    def dispatch(self, request, *args, **kwargs):
        # Vérifier si l'utilisateur est staff ou appartient aux groupes autorisés
        user_groups = [group.nom_groupe for group in request.user.groupe.all()]
        if not (request.user.is_staff or 'Driver Principal' in user_groups or 'Gestionnaire Carburant' in user_groups):
            messages.error(request, "Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset

class TypeMaintenanceCreateView(LoginRequiredMixin, CreateView):
    model = TypeMaintenance
    template_name = 'core/type_maintenance/form.html'
    form_class = TypeMaintenanceForm
    success_url = reverse_lazy('type_maintenance_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ajouter un type de maintenance'
        context['submit_text'] = 'Ajouter'
        return context
        
    def dispatch(self, request, *args, **kwargs):
        # Vérifier si l'utilisateur est staff ou appartient aux groupes autorisés
        user_groups = [group.nom_groupe for group in request.user.groupe.all()]
        if not (request.user.is_staff or 'Driver Principal' in user_groups or 'Gestionnaire Carburant' in user_groups):
            messages.error(request, "Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

class TypeMaintenanceUpdateView(LoginRequiredMixin, UpdateView):
    model = TypeMaintenance
    template_name = 'core/type_maintenance/form.html'
    form_class = TypeMaintenanceForm
    success_url = reverse_lazy('type_maintenance_list')
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Modifier un type de maintenance'
        context['submit_text'] = 'Modifier'
        return context
        
    def dispatch(self, request, *args, **kwargs):
        # Vérifier si l'utilisateur est staff ou appartient aux groupes autorisés
        user_groups = [group.nom_groupe for group in request.user.groupe.all()]
        if not (request.user.is_staff or 'Driver Principal' in user_groups or 'Gestionnaire Carburant' in user_groups):
            messages.error(request, "Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

class TypeMaintenanceDeleteView(LoginRequiredMixin, DeleteView):
    model = TypeMaintenance
    template_name = 'core/type_maintenance/delete.html'
    success_url = reverse_lazy('type_maintenance_list')
    pk_url_kwarg = 'id'
    
    def dispatch(self, request, *args, **kwargs):
        # Vérifier si l'utilisateur est staff ou appartient aux groupes autorisés
        user_groups = [group.nom_groupe for group in request.user.groupe.all()]
        if not (request.user.is_staff or 'Driver Principal' in user_groups or 'Gestionnaire Carburant' in user_groups):
            messages.error(request, "Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

# Views pour les Maintenances
class MaintenanceListView(LoginRequiredMixin, ListView):
    model = Maintenance
    template_name = 'core/maintenance/list.html'
    context_object_name = 'maintenances'
    ordering = ['-date']
    
    def dispatch(self, request, *args, **kwargs):
        # Vérifier si l'utilisateur est staff ou appartient aux groupes autorisés
        user_groups = [group.nom_groupe for group in request.user.groupe.all()]
        if not (request.user.is_staff or 'Driver Principal' in user_groups or 'Gestionnaire Carburant' in user_groups):
            messages.error(request, "Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(service__in=self.request.user.service.all())

class MaintenanceCreateView(LoginRequiredMixin, CreateView):
    model = Maintenance
    template_name = 'core/maintenance/form.html'
    form_class = MaintenanceForm
    success_url = reverse_lazy('maintenance_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ajouter une maintenance'
        context['submit_text'] = 'Ajouter'
        return context
        
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
        
    def dispatch(self, request, *args, **kwargs):
        # Vérifier si l'utilisateur est staff ou appartient aux groupes autorisés
        user_groups = [group.nom_groupe for group in request.user.groupe.all()]
        if not (request.user.is_staff or 'Driver Principal' in user_groups or 'Gestionnaire Carburant' in user_groups):
            messages.error(request, "Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

class MaintenanceUpdateView(LoginRequiredMixin, UpdateView):
    model = Maintenance
    template_name = 'core/maintenance/form.html'
    form_class = MaintenanceForm
    success_url = reverse_lazy('maintenance_list')
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Modifier une maintenance'
        context['submit_text'] = 'Modifier'
        return context
        
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
        
    def dispatch(self, request, *args, **kwargs):
        # Vérifier si l'utilisateur est staff ou appartient aux groupes autorisés
        user_groups = [group.nom_groupe for group in request.user.groupe.all()]
        if not (request.user.is_staff or 'Driver Principal' in user_groups or 'Gestionnaire Carburant' in user_groups):
            messages.error(request, "Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        maintenance = self.object
        
        # Mettre à jour ou créer une planification si des périodicités sont définies
        if maintenance.periodicite_km or maintenance.periodicite_mois:
            # Calculer les prochaines échéances
            prochaine_echeance_km = None
            if maintenance.periodicite_km:
                prochaine_echeance_km = maintenance.km_vehicule + maintenance.periodicite_km
            
            prochaine_echeance_date = None
            if maintenance.periodicite_mois:
                from datetime import datetime
                from dateutil.relativedelta import relativedelta
                prochaine_echeance_date = maintenance.date + relativedelta(months=maintenance.periodicite_mois)
            
            # Chercher un utilisateur du groupe "Driver Principal" lié au service
            driver_principal = Utilisateur.objects.filter(
                groupe__nom_groupe='Driver Principal',
                service=maintenance.service
            ).first()
            
            # Si aucun utilisateur "Driver Principal" n'est trouvé, utiliser l'utilisateur actuel
            if not driver_principal:
                driver_principal = self.request.user
            
            # Chercher une planification existante pour ce véhicule et ce type de maintenance
            planification = Planification.objects.filter(
                vehicule=maintenance.vehicule,
                type_maintenance=maintenance.type_maintenance
            ).first()
            
            if planification:
                # Mettre à jour la planification existante
                planification.service = maintenance.service
                planification.utilisateur = driver_principal
                planification.prochaine_echeance_km = prochaine_echeance_km if prochaine_echeance_km else 0
                planification.prochaine_echeance_date = prochaine_echeance_date
                planification.alerte_km = maintenance.alerte_km
                planification.alerte_mois = maintenance.alerte_mois
                planification.save()
                
                messages.success(self.request, 
                               f"La maintenance a été modifiée et la planification a été mise à jour.")
            else:
                # Créer une nouvelle planification
                Planification.objects.create(
                    service=maintenance.service,
                    utilisateur=driver_principal,
                    vehicule=maintenance.vehicule,
                    type_maintenance=maintenance.type_maintenance,
                    prochaine_echeance_km=prochaine_echeance_km if prochaine_echeance_km else 0,
                    prochaine_echeance_date=prochaine_echeance_date,
                    alerte_km=maintenance.alerte_km,
                    alerte_mois=maintenance.alerte_mois
                )
                
                messages.success(self.request, 
                               f"La maintenance a été modifiée et une planification a été générée pour la prochaine échéance.")
        
        return response

# Views pour les Planifications
class PlanificationListView(LoginRequiredMixin, ListView):
    model = Planification
    template_name = 'core/planification/list.html'
    context_object_name = 'planifications'
    ordering = ['prochaine_echeance_km']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrer les planifications en fonction des services de l'utilisateur
        services_ids = self.request.user.service.values_list('id_service', flat=True)
        queryset = queryset.filter(service__id_service__in=services_ids)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from datetime import date
        context['today'] = date.today()
        return context
    
    def dispatch(self, request, *args, **kwargs):
        # Vérifier si l'utilisateur est staff ou appartient aux groupes autorisés
        user_groups = [group.nom_groupe for group in request.user.groupe.all()]
        if not (request.user.is_staff or 'Driver Principal' in user_groups or 'Gestionnaire Carburant' in user_groups):
            messages.error(request, "Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

class PlanificationCreateView(LoginRequiredMixin, CreateView):
    model = Planification
    template_name = 'core/planification/form.html'
    form_class = PlanificationForm
    success_url = reverse_lazy('planification_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ajouter une planification'
        context['submit_text'] = 'Ajouter'
        return context
        
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
        
    def dispatch(self, request, *args, **kwargs):
        # Vérifier si l'utilisateur est staff ou appartient aux groupes autorisés
        user_groups = [group.nom_groupe for group in request.user.groupe.all()]
        if not (request.user.is_staff or 'Driver Principal' in user_groups or 'Gestionnaire Carburant' in user_groups):
            messages.error(request, "Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

class PlanificationUpdateView(LoginRequiredMixin, UpdateView):
    model = Planification
    template_name = 'core/planification/form.html'
    form_class = PlanificationForm
    success_url = reverse_lazy('planification_list')
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Modifier une planification'
        context['submit_text'] = 'Modifier'
        return context
        
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
        
    def dispatch(self, request, *args, **kwargs):
        # Vérifier si l'utilisateur est staff ou appartient aux groupes autorisés
        user_groups = [group.nom_groupe for group in request.user.groupe.all()]
        if not (request.user.is_staff or 'Driver Principal' in user_groups or 'Gestionnaire Carburant' in user_groups):
            messages.error(request, "Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

class PlanificationDeleteView(LoginRequiredMixin, DeleteView):
    model = Planification
    template_name = 'core/planification/delete.html'
    success_url = reverse_lazy('planification_list')
    pk_url_kwarg = 'id'
    
    def dispatch(self, request, *args, **kwargs):
        # Vérifier si l'utilisateur est staff ou appartient aux groupes autorisés
        user_groups = [group.nom_groupe for group in request.user.groupe.all()]
        if not (request.user.is_staff or 'Driver Principal' in user_groups or 'Gestionnaire Carburant' in user_groups):
            messages.error(request, "Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

class PlanificationDetailView(LoginRequiredMixin, DetailView):
    model = Planification
    template_name = 'core/planification/detail.html'
    context_object_name = 'planification'
    pk_url_kwarg = 'id'
    
    def dispatch(self, request, *args, **kwargs):
        # Vérifier si l'utilisateur est staff ou appartient aux groupes autorisés
        user_groups = [group.nom_groupe for group in request.user.groupe.all()]
        if not (request.user.is_staff or 'Driver Principal' in user_groups or 'Gestionnaire Carburant' in user_groups):
            messages.error(request, "Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

# API pour récupérer le kilométrage d'un véhicule
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required

@login_required
@require_GET
def get_vehicule_kilometrage(request, id_vehicule):
    """
    API pour récupérer le kilométrage actuel d'un véhicule.
    """
    try:
        # Récupérer le véhicule
        vehicule = Vehicule.objects.get(id_vehicule=id_vehicule)
        
        # Vérifier si l'utilisateur a accès à ce véhicule
        services_ids = request.user.service.values_list('id_service', flat=True)
        if vehicule.service.id_service not in services_ids and not request.user.is_staff:
            return JsonResponse({'error': 'Vous n\'avez pas accès à ce véhicule'}, status=403)
        
        # Retourner le kilométrage
        return JsonResponse({'kilometrage': vehicule.kilometrage})
    except Vehicule.DoesNotExist:
        return JsonResponse({'error': 'Véhicule non trouvé'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

class MaintenanceCreateView(LoginRequiredMixin, CreateView):
    model = Maintenance
    template_name = 'core/maintenance/form.html'
    form_class = MaintenanceForm
    success_url = reverse_lazy('maintenance_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ajouter une maintenance'
        context['submit_text'] = 'Ajouter'
        return context
        
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
        
    def dispatch(self, request, *args, **kwargs):
        # Vérifier si l'utilisateur est staff ou appartient aux groupes autorisés
        user_groups = [group.nom_groupe for group in request.user.groupe.all()]
        if not (request.user.is_staff or 'Driver Principal' in user_groups or 'Gestionnaire Carburant' in user_groups):
            messages.error(request, "Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        maintenance = self.object
        
        # Créer une planification si des périodicités sont définies
        if maintenance.periodicite_km or maintenance.periodicite_mois:
            # Calculer les prochaines échéances
            prochaine_echeance_km = None
            if maintenance.periodicite_km:
                prochaine_echeance_km = maintenance.km_vehicule + maintenance.periodicite_km
            
            prochaine_echeance_date = None
            if maintenance.periodicite_mois:
                from datetime import datetime
                from dateutil.relativedelta import relativedelta
                prochaine_echeance_date = maintenance.date + relativedelta(months=maintenance.periodicite_mois)
            
            # Chercher un utilisateur du groupe "Driver Principal" lié au service
            driver_principal = Utilisateur.objects.filter(
                groupe__nom_groupe='Driver Principal',
                service=maintenance.service
            ).first()
            
            # Si aucun utilisateur "Driver Principal" n'est trouvé, utiliser l'utilisateur actuel
            if not driver_principal:
                driver_principal = self.request.user
            
            # Créer la planification
            Planification.objects.create(
                service=maintenance.service,
                utilisateur=driver_principal,
                vehicule=maintenance.vehicule,
                type_maintenance=maintenance.type_maintenance,
                prochaine_echeance_km=prochaine_echeance_km if prochaine_echeance_km else 0,
                prochaine_echeance_date=prochaine_echeance_date,
                alerte_km=maintenance.alerte_km,
                alerte_mois=maintenance.alerte_mois
            )
            
            messages.success(self.request, 
                           f"La maintenance a été créée et une planification a été générée pour la prochaine échéance.")
        
        return response

class MaintenanceDeleteView(LoginRequiredMixin, DeleteView):
    model = Maintenance
    template_name = 'core/maintenance/delete.html'
    success_url = reverse_lazy('maintenance_list')
    pk_url_kwarg = 'id'
    
    def dispatch(self, request, *args, **kwargs):
        # Vérifier si l'utilisateur est staff ou appartient aux groupes autorisés
        user_groups = [group.nom_groupe for group in request.user.groupe.all()]
        if not (request.user.is_staff or 'Driver Principal' in user_groups or 'Gestionnaire Carburant' in user_groups):
            messages.error(request, "Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

class MaintenanceDetailView(LoginRequiredMixin, DetailView):
    model = Maintenance
    template_name = 'core/maintenance/detail.html'
    context_object_name = 'maintenance'
    pk_url_kwarg = 'id'
    
    def dispatch(self, request, *args, **kwargs):
        # Vérifier si l'utilisateur est staff ou appartient aux groupes autorisés
        user_groups = [group.nom_groupe for group in request.user.groupe.all()]
        if not (request.user.is_staff or 'Driver Principal' in user_groups or 'Gestionnaire Carburant' in user_groups):
            messages.error(request, "Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

class PlanificationListView(LoginRequiredMixin, ListView):
    model = Planification
    template_name = 'core/planification/list.html'
    context_object_name = 'planifications'
    ordering = ['prochaine_echeance_km']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrer les planifications en fonction des services de l'utilisateur
        services_ids = self.request.user.service.values_list('id_service', flat=True)
        queryset = queryset.filter(service__id_service__in=services_ids)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from datetime import date
        context['today'] = date.today()
        return context
    
    def dispatch(self, request, *args, **kwargs):
        # Vérifier si l'utilisateur est staff ou appartient aux groupes autorisés
        user_groups = [group.nom_groupe for group in request.user.groupe.all()]
        if not (request.user.is_staff or 'Driver Principal' in user_groups or 'Gestionnaire Carburant' in user_groups):
            messages.error(request, "Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

# Vue pour le rapport de maintenance
class MaintenanceReportView(LoginRequiredMixin, TemplateView):
    template_name = 'core/maintenance/report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Récupérer les paramètres de filtrage
        date_debut = self.request.GET.get('date_debut')
        date_fin = self.request.GET.get('date_fin')
        service_id = self.request.GET.get('service')
        vehicule_id = self.request.GET.get('vehicule')
        
        # Filtrer les services selon l'utilisateur connecté
        services_ids = self.request.user.service.values_list('id_service', flat=True)
        context['services'] = Service.objects.filter(id_service__in=services_ids)
        
        # Initialiser les véhicules (sera mis à jour si un service est sélectionné)
        context['vehicules'] = Vehicule.objects.filter(service__id_service__in=services_ids)
        
        # Si un service spécifique est sélectionné, filtrer les véhicules
        if service_id:
            context['vehicules'] = context['vehicules'].filter(service__id_service=service_id)
            context['selected_service'] = Service.objects.get(id_service=service_id)
        
        # Si un véhicule spécifique est sélectionné
        if vehicule_id:
            context['selected_vehicule'] = Vehicule.objects.get(id_vehicule=vehicule_id)
        
        # Initialiser la requête de base pour les maintenances
        maintenances = Maintenance.objects.filter(service__id_service__in=services_ids)
        
        # Appliquer les filtres de date
        if date_debut:
            from datetime import datetime
            date_debut_obj = datetime.strptime(date_debut, '%Y-%m-%d').date()
            maintenances = maintenances.filter(date__gte=date_debut_obj)
            context['date_debut'] = date_debut
        
        if date_fin:
            from datetime import datetime
            date_fin_obj = datetime.strptime(date_fin, '%Y-%m-%d').date()
            maintenances = maintenances.filter(date__lte=date_fin_obj)
            context['date_fin'] = date_fin
        
        # Appliquer les filtres de service et de véhicule
        if service_id:
            maintenances = maintenances.filter(service__id_service=service_id)
        
        if vehicule_id:
            maintenances = maintenances.filter(vehicule__id_vehicule=vehicule_id)
        
        # Ordonner les maintenances par date décroissante
        maintenances = maintenances.order_by('-date')
        
        # Ajouter les maintenances au contexte
        context['maintenances'] = maintenances
        
        # Calculer les statistiques
        if maintenances.exists():
            # Coût total des maintenances
            context['cout_total'] = maintenances.aggregate(Sum('montant'))['montant__sum']
            
            # Nombre total de maintenances
            context['nombre_maintenances'] = maintenances.count()
            # Coût moyen par maintenance (calculé directement)
            if context['nombre_maintenances'] > 0:
                context['cout_moyen'] = context['cout_total'] / context['nombre_maintenances']
            else:
                context['cout_moyen'] = 0
            
            # Types de maintenance les plus fréquents
            types_maintenance = maintenances.values('type_maintenance__libelle').annotate(
                count=Count('type_maintenance')
            ).order_by('-count')[:5]
            context['types_maintenance_frequents'] = types_maintenance
            
            # Coût moyen par type de maintenance
            cout_moyen_par_type = maintenances.values('type_maintenance__libelle').annotate(
                cout_moyen=Avg('montant')
            ).order_by('-cout_moyen')[:5]
            context['cout_moyen_par_type'] = cout_moyen_par_type
            
            # Coût total par véhicule
            cout_par_vehicule = maintenances.values('vehicule__immatriculation', 'vehicule__marque', 'vehicule__modele').annotate(
                cout_total=Sum('montant')
            ).order_by('-cout_total')[:5]
            context['cout_par_vehicule'] = cout_par_vehicule
        
        return context
    
    def dispatch(self, request, *args, **kwargs):
        # Vérifier si l'utilisateur est staff ou appartient aux groupes autorisés
        user_groups = [group.nom_groupe for group in request.user.groupe.all()]
        if not (request.user.is_staff or 'Driver Principal' in user_groups or 'Gestionnaire Carburant' in user_groups):
            messages.error(request, "Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

# Vues pour l'exportation des rapports de maintenance
class MaintenanceReportExportPDF(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # Récupérer les paramètres de filtrage
        date_debut = request.GET.get('date_debut')
        date_fin = request.GET.get('date_fin')
        service_id = request.GET.get('service')
        vehicule_id = request.GET.get('vehicule')
        
        # Filtrer les services selon l'utilisateur connecté
        services_ids = request.user.service.values_list('id_service', flat=True)
        
        # Initialiser la requête de base pour les maintenances
        maintenances = Maintenance.objects.filter(service__id_service__in=services_ids)
        
        # Appliquer les filtres de date
        if date_debut:
            from datetime import datetime
            date_debut_obj = datetime.strptime(date_debut, '%Y-%m-%d').date()
            maintenances = maintenances.filter(date__gte=date_debut_obj)
        
        if date_fin:
            from datetime import datetime
            date_fin_obj = datetime.strptime(date_fin, '%Y-%m-%d').date()
            maintenances = maintenances.filter(date__lte=date_fin_obj)
        
        # Appliquer les filtres de service et de véhicule
        if service_id:
            maintenances = maintenances.filter(service__id_service=service_id)
        
        if vehicule_id:
            maintenances = maintenances.filter(vehicule__id_vehicule=vehicule_id)
        
        # Ordonner les maintenances par date décroissante
        maintenances = maintenances.order_by('-date')
        
        # Générer le PDF
        from django.http import HttpResponse
        from reportlab.lib.pagesizes import letter, landscape
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet
        from io import BytesIO
        
        # Créer un buffer pour le PDF
        buffer = BytesIO()
        
        # Créer le document PDF
        doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = styles['Heading1']
        subtitle_style = styles['Heading2']
        normal_style = styles['Normal']
        
        # Titre
        elements.append(Paragraph("Rapport de Maintenance des Véhicules", title_style))
        elements.append(Spacer(1, 12))
        
        # Sous-titre avec les filtres
        filter_text = f"Service: {Service.objects.get(id_service=service_id).nom_service if service_id else 'Tous'} | Véhicule: {Vehicule.objects.get(id_vehicule=vehicule_id).immatriculation if vehicule_id else 'Tous'}"
        if date_debut and date_fin:
            filter_text += f" | Période: du {date_debut} au {date_fin}"
        elif date_debut:
            filter_text += f" | Période: à partir du {date_debut}"
        elif date_fin:
            filter_text += f" | Période: jusqu'au {date_fin}"
        
        elements.append(Paragraph(filter_text, subtitle_style))
        elements.append(Spacer(1, 12))
        
        # Tableau des maintenances
        if maintenances.exists():
            # En-têtes du tableau
            data = [['Date', 'Service', 'Véhicule', 'Type de maintenance', 'Détail', 'Fournisseur', 'Kilométrage', 'Montant (FCFA)']]
            
            # Données du tableau
            for maintenance in maintenances:
                data.append([
                    maintenance.date.strftime('%d/%m/%Y'),
                    maintenance.service.nom_service,
                    str(maintenance.vehicule),
                    maintenance.type_maintenance.libelle,
                    maintenance.detail,
                    maintenance.fournisseur.nom_fournisseur,
                    f"{maintenance.km_vehicule} km",
                    f"{maintenance.montant:,}".replace(',', ' ')
                ])
            
            # Créer le tableau
            table = Table(data, repeatRows=1)
            
            # Style du tableau
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('ALIGN', (4, 1), (5, -1), 'RIGHT'),
            ]))
            
            elements.append(table)
            
            # Statistiques
            elements.append(Spacer(1, 20))
            elements.append(Paragraph("Statistiques", subtitle_style))
            elements.append(Spacer(1, 12))
            
            from django.db.models import Sum
            cout_total = maintenances.aggregate(Sum('montant'))['montant__sum']
            nombre_maintenances = maintenances.count()
            
            stats_data = [
                ['Nombre total de maintenances', str(nombre_maintenances)],
                ['Coût total des maintenances', f"{cout_total:,}".replace(',', ' ') + " FCFA"],
                ['Coût moyen par maintenance', f"{cout_total/nombre_maintenances:,.2f}".replace(',', ' ') + " FCFA"]
            ]
            
            stats_table = Table(stats_data)
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            elements.append(stats_table)
        else:
            elements.append(Paragraph("Aucune maintenance trouvée pour les critères sélectionnés.", normal_style))
        
        # Construire le PDF
        doc.build(elements)
        
        # Récupérer le contenu du PDF
        pdf = buffer.getvalue()
        buffer.close()
        
        # Créer la réponse HTTP
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="rapport_maintenance.pdf"'
        response.write(pdf)
        
        return response

class MaintenanceReportExportExcel(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # Récupérer les paramètres de filtrage
        date_debut = request.GET.get('date_debut')
        date_fin = request.GET.get('date_fin')
        service_id = request.GET.get('service')
        vehicule_id = request.GET.get('vehicule')
        
        # Filtrer les services selon l'utilisateur connecté
        services_ids = request.user.service.values_list('id_service', flat=True)
        
        # Initialiser la requête de base pour les maintenances
        maintenances = Maintenance.objects.filter(service__id_service__in=services_ids)
        
        # Appliquer les filtres de date
        if date_debut:
            from datetime import datetime
            date_debut_obj = datetime.strptime(date_debut, '%Y-%m-%d').date()
            maintenances = maintenances.filter(date__gte=date_debut_obj)
        
        if date_fin:
            from datetime import datetime
            date_fin_obj = datetime.strptime(date_fin, '%Y-%m-%d').date()
            maintenances = maintenances.filter(date__lte=date_fin_obj)
        
        # Appliquer les filtres de service et de véhicule
        if service_id:
            maintenances = maintenances.filter(service__id_service=service_id)
        
        if vehicule_id:
            maintenances = maintenances.filter(vehicule__id_vehicule=vehicule_id)
        
        # Ordonner les maintenances par date décroissante
        maintenances = maintenances.order_by('-date')
        
        # Générer le fichier Excel
        import xlwt
        from django.http import HttpResponse
        
        # Créer un workbook et ajouter une feuille
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Rapport de Maintenance')
        
        # Styles
        font_style = xlwt.XFStyle()
        font_style.font.bold = True
        
        # En-têtes
        columns = ['Date', 'Service', 'Véhicule', 'Type de maintenance', 'Détail', 'Fournisseur', 'Kilométrage', 'Montant (FCFA)']
        
        # Écrire les en-têtes
        for col_num, column_title in enumerate(columns):
            ws.write(0, col_num, column_title, font_style)
        
        # Style pour les données
        font_style = xlwt.XFStyle()
        
        # Écrire les données
        row_num = 1
        for maintenance in maintenances:
            ws.write(row_num, 0, maintenance.date.strftime('%d/%m/%Y'), font_style)
            ws.write(row_num, 1, maintenance.service.nom_service, font_style)
            ws.write(row_num, 2, str(maintenance.vehicule), font_style)
            ws.write(row_num, 3, maintenance.type_maintenance.libelle, font_style)
            ws.write(row_num, 4, maintenance.detail, font_style)
            ws.write(row_num, 5, maintenance.fournisseur.nom_fournisseur, font_style)
            ws.write(row_num, 6, maintenance.km_vehicule, font_style)
            ws.write(row_num, 7, maintenance.montant, font_style)
            row_num += 1
        
        # Ajouter une feuille pour les statistiques
        if maintenances.exists():
            ws_stats = wb.add_sheet('Statistiques')
            
            # En-têtes
            ws_stats.write(0, 0, 'Statistiques', font_style)
            ws_stats.write(0, 1, 'Valeur', font_style)
            
            # Données
            from django.db.models import Sum, Count, Avg
            cout_total = maintenances.aggregate(Sum('montant'))['montant__sum']
            nombre_maintenances = maintenances.count()
            
            row_num = 1
            ws_stats.write(row_num, 0, 'Nombre total de maintenances', font_style)
            ws_stats.write(row_num, 1, nombre_maintenances, font_style)
            row_num += 1
            
            ws_stats.write(row_num, 0, 'Coût total des maintenances (FCFA)', font_style)
            ws_stats.write(row_num, 1, cout_total, font_style)
            row_num += 1
            
            ws_stats.write(row_num, 0, 'Coût moyen par maintenance (FCFA)', font_style)
            ws_stats.write(row_num, 1, cout_total/nombre_maintenances, font_style)
            row_num += 2
            
            # Types de maintenance les plus fréquents
            ws_stats.write(row_num, 0, 'Types de maintenance les plus fréquents', font_style)
            ws_stats.write(row_num, 1, 'Nombre', font_style)
            row_num += 1
            
            types_maintenance = maintenances.values('type_maintenance__libelle').annotate(
                count=Count('type_maintenance')
            ).order_by('-count')[:5]
            
            for type_maintenance in types_maintenance:
                ws_stats.write(row_num, 0, type_maintenance['type_maintenance__libelle'], font_style)
                ws_stats.write(row_num, 1, type_maintenance['count'], font_style)
                row_num += 1
            
            row_num += 1
            
            # Coût par véhicule
            ws_stats.write(row_num, 0, 'Coût par véhicule', font_style)
            ws_stats.write(row_num, 1, 'Montant (FCFA)', font_style)
            row_num += 1
            
            cout_par_vehicule = maintenances.values('vehicule__immatriculation').annotate(
                cout_total=Sum('montant')
            ).order_by('-cout_total')[:5]
            
            for vehicule in cout_par_vehicule:
                ws_stats.write(row_num, 0, vehicule['vehicule__immatriculation'], font_style)
                ws_stats.write(row_num, 1, vehicule['cout_total'], font_style)
                row_num += 1
        
        # Créer la réponse HTTP
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="rapport_maintenance.xls"'
        response.write(wb.save('rapport_maintenance.xls'))
        
        return response

def _is_driver_principal(user):
    return user.groupe.filter(nom_groupe="Driver Principal").exists()


def _is_admin_like(user):
    return user.is_staff or user.is_superuser or user.groupe.filter(nom_groupe='Administrateur').exists()


def _user_service_ids(user):
    return list(user.service.values_list('id_service', flat=True))


@login_required
def demandes_course_list(request):
    user = request.user
    services_ids = _user_service_ids(user)

    if _is_admin_like(user):
        demandes = DemandeCourse.objects.all()
    else:
        demandes = DemandeCourse.objects.filter(
            Q(id_service__id_service__in=services_ids) |
            Q(id_utilisateur=user) |
            Q(id_auteur=user)
        )

    demandes = demandes.select_related('id_service', 'id_utilisateur', 'id_vehicule').order_by('-date_demande')
    is_driver_principal = _is_driver_principal(user)
    return render(request, 'core/demandes_course/list.html', {'demandes': demandes, 'is_driver_principal': is_driver_principal})


@login_required
def demande_course_create(request):
    if request.method == 'POST':
        form = DemandeCourseFormAmeliore(request.POST, user=request.user)
        if form.is_valid():
            demande = form.save(commit=False)
            demande.id_utilisateur = request.user
            demande.id_auteur = request.user
            demande.statut = 'soumise'
            demande.save()

            try:
                notify_driver_principal_course(demande)
            except Exception:
                messages.warning(request, "Demande créée, mais la notification email n'a pas pu être envoyée.")

            messages.success(request, "Demande de course créée avec succès.")
            return redirect('demandes_course_list')
    else:
        form = DemandeCourseFormAmeliore(user=request.user)

    return render(request, 'core/demandes_course/form_ameliore.html', {'form': form, 'demandeur': True})


@login_required
def demande_course_update(request, pk):
    demande = get_object_or_404(DemandeCourse, pk=pk)
    owner = demande.id_auteur or demande.id_utilisateur

    if owner != request.user and not _is_admin_like(request.user):
        messages.error(request, "Vous n'êtes pas autorisé à modifier cette demande.")
        return redirect('demandes_course_list')

    if demande.statut != 'soumise':
        messages.warning(request, "Seules les demandes au statut 'soumise' peuvent être modifiées.")
        return redirect('demande_course_detail', pk=demande.pk)

    if request.method == 'POST':
        form = DemandeCourseFormAmeliore(request.POST, instance=demande, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Demande de course modifiée avec succès.")
            return redirect('demandes_course_list')
    else:
        form = DemandeCourseFormAmeliore(instance=demande, user=request.user)

    return render(request, 'core/demandes_course/form_ameliore.html', {'form': form, 'edit': True})


@login_required
def demande_course_detail(request, pk):
    demande = get_object_or_404(DemandeCourse, pk=pk)
    services_ids = _user_service_ids(request.user)
    can_access = (
        _is_admin_like(request.user) or
        demande.id_service_id in services_ids or
        demande.id_utilisateur == request.user or
        demande.id_auteur == request.user
    )

    if not can_access:
        messages.error(request, "Vous n'êtes pas autorisé à consulter cette demande.")
        return redirect('demandes_course_list')

    return render(request, 'core/demandes_course/detail.html', {'demande': demande})


@login_required
def demande_course_traitement(request, pk):
    """
    Traite une demande de course (acceptation/rejet), et crée/met à jour la planification
    lorsque la demande est acceptée.
    """
    demande = get_object_or_404(DemandeCourse, pk=pk)
    services_ids = _user_service_ids(request.user)

    if not (_is_admin_like(request.user) or (_is_driver_principal(request.user) and demande.id_service_id in services_ids)):
        messages.error(request, "Vous n'êtes pas autorisé à traiter cette demande.")
        return redirect('demandes_course_list')

    if request.method == 'POST':
        form = DemandeCourseTraitementForm(request.POST, instance=demande, user=request.user)
        if form.is_valid():
            selected_status = form.cleaned_data['statut']
            selected_driver = form.cleaned_data.get('id_utilisateur')
            selected_vehicule = form.cleaned_data.get('id_vehicule')

            with transaction.atomic():
                demande = form.save(commit=False)

                if selected_status == 'rejetée':
                    demande.statut = 'rejetée'
                    demande.id_vehicule = None
                    demande.save()

                elif selected_status == 'acceptée':
                    # Contrôles de conflit simples sur même créneau de départ
                    vehicule_conflict = PlanificationCourse.objects.filter(
                        vehicule=selected_vehicule,
                        date_heure=demande.date_heure_prevue,
                        statut='planifiée'
                    ).exclude(demande=demande).exists()

                    chauffeur_conflict = PlanificationCourse.objects.filter(
                        utilisateur=selected_driver,
                        date_heure=demande.date_heure_prevue,
                        statut='planifiée'
                    ).exclude(demande=demande).exists()

                    if vehicule_conflict:
                        form.add_error('id_vehicule', "Ce véhicule est déjà planifié sur ce créneau.")
                        return render(request, 'core/demandes_course/traitement_form.html', {'form': form, 'demande': demande, 'traitement': True})

                    if chauffeur_conflict:
                        form.add_error('id_utilisateur', "Ce chauffeur est déjà planifié sur ce créneau.")
                        return render(request, 'core/demandes_course/traitement_form.html', {'form': form, 'demande': demande, 'traitement': True})

                    demande.statut = 'planifiée'
                    demande.save()

                    PlanificationCourse.objects.update_or_create(
                        demande=demande,
                        defaults={
                            'date_heure': demande.date_heure_prevue,
                            'utilisateur': demande.id_utilisateur,
                            'vehicule': demande.id_vehicule,
                            'statut': 'planifiée',
                            'lieu_arrivee': demande.lieu_arrivee,
                        }
                    )

            try:
                if demande.statut == 'rejetée':
                    notify_course_rejected(demande)
                elif demande.statut == 'planifiée':
                    notify_course_affectation(demande, demande.id_utilisateur, demande.id_vehicule)
            except Exception:
                messages.warning(request, "Traitement enregistré, mais la notification email n'a pas pu être envoyée.")

            messages.success(request, "Demande de course traitée avec succès.")
            return redirect('demandes_course_list')
    else:
        form = DemandeCourseTraitementForm(instance=demande, user=request.user)

    return render(request, 'core/demandes_course/traitement_form.html', {'form': form, 'demande': demande, 'traitement': True})


@login_required
def planification_courses_view(request):
    date_str = request.GET.get('date')
    date_selected = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else datetime.now().date()
    heures = list(range(5, 23))

    user = request.user
    services_ids = _user_service_ids(user)
    is_driver_principal = _is_driver_principal(user)

    queryset = PlanificationCourse.objects.select_related('utilisateur', 'vehicule', 'demande')
    if _is_admin_like(user):
        pass
    elif is_driver_principal:
        queryset = queryset.filter(utilisateur__service__id_service__in=services_ids)
    elif user.groupe.filter(nom_groupe='Driver').exists():
        queryset = queryset.filter(utilisateur=user)
    else:
        queryset = queryset.filter(utilisateur__service__id_service__in=services_ids)

    # Véhicules affichés dans la grille
    if _is_admin_like(user):
        vehicules = Vehicule.objects.all().order_by('immatriculation')
    else:
        vehicules = Vehicule.objects.filter(service__id_service__in=services_ids).order_by('immatriculation')

    planifications_sidebar = queryset.filter(date_heure__gte=timezone.now()).order_by('date_heure')
    planifications_jour = queryset.filter(date_heure__date=date_selected)

    planning_dict = {(plan.date_heure.hour, plan.vehicule.pk): plan for plan in planifications_jour}

    context = {
        'date_selected': date_selected,
        'heures': heures,
        'vehicules': vehicules,
        'planning_dict': planning_dict,
        'planifications_sidebar': planifications_sidebar,
        'is_driver_principal': is_driver_principal,
    }
    return render(request, 'core/planification/courses.html', context)


@login_required
def planification_course_detail(request, pk):
    planification = get_object_or_404(PlanificationCourse.objects.select_related('utilisateur', 'vehicule', 'demande'), pk=pk)
    services_ids = _user_service_ids(request.user)

    can_access = (
        _is_admin_like(request.user) or
        planification.utilisateur == request.user or
        planification.utilisateur.service.filter(id_service__in=services_ids).exists()
    )
    if not can_access:
        messages.error(request, "Vous n'êtes pas autorisé à consulter cette planification.")
        return redirect('planification_courses')

    execution = planification.executions.order_by('-date_heure_debut').first()
    return render(
        request,
        'core/planification/planification_detail.html',
        {'planification': planification, 'execution': execution}
    )


@login_required
def planification_course_manuelle(request):
    if not (_is_driver_principal(request.user) or _is_admin_like(request.user)):
        messages.error(request, "Vous n'êtes pas autorisé à créer une planification manuelle.")
        return redirect('planification_courses')

    if request.method == 'POST':
        form = PlanificationCourseForm(request.POST, user=request.user)
        if form.is_valid():
            with transaction.atomic():
                planification = form.save(commit=False)
                planification.demande = None
                planification.statut = 'planifiée'

                conflict = PlanificationCourse.objects.filter(
                    vehicule=planification.vehicule,
                    date_heure=planification.date_heure,
                    statut='planifiée'
                ).exists()
                if conflict:
                    form.add_error('vehicule', "Ce véhicule est déjà planifié à ce créneau.")
                    return render(request, 'core/planification/planification_manuelle_form.html', {'form': form})

                planification.save()

            messages.success(request, "Planification manuelle créée avec succès.")
            return redirect('planification_courses')
    else:
        form = PlanificationCourseForm(user=request.user)

    return render(request, 'core/planification/planification_manuelle_form.html', {'form': form})

# --- END OF FILE ---
