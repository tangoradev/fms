"""
URL configuration for fms project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views
from core import views_admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('services/', views.services_view, name='services_view'),
    path('services/ajouter/', views.service_create, name='service_create'),
    path('services/<int:pk>/modifier/', views.service_edit, name='service_edit'),
    path('services/<int:pk>/supprimer/', views.service_delete, name='service_delete'),
    path('groupes/', views.groupes_view, name='groupes_view'),
    path('groupes/ajouter/', views.groupe_create, name='groupe_create'),
    path('groupes/<int:pk>/modifier/', views.groupe_edit, name='groupe_edit'),
    path('groupes/<int:pk>/supprimer/', views.groupe_delete, name='groupe_delete'),
    path('utilisateurs/', views.utilisateurs_view, name='utilisateurs_view'),
    path('utilisateurs/ajouter/', views.utilisateur_create, name='utilisateur_create'),
    path('utilisateurs/<int:pk>/modifier/', views.utilisateur_update, name='utilisateur_update'),
    path('utilisateurs/<int:pk>/supprimer/', views.utilisateur_delete, name='utilisateur_delete'),
    
    # Routes pour les véhicules
    path('vehicules/', views.vehicules_list, name='vehicules_list'),
    path('vehicules/dashboard/', views.fleet_dashboard, name='fleet_dashboard'),
    path('vehicules/ajouter/', views.vehicule_create, name='vehicule_create'),
    path('vehicules/<int:pk>/', views.vehicule_detail, name='vehicule_detail'),
    path('vehicules/<int:pk>/modifier/', views.vehicule_update, name='vehicule_update'),
    path('vehicules/<int:pk>/statut/', views.vehicule_change_status, name='vehicule_change_status'),
    path('vehicules/<int:pk>/affectations/ajouter/', views.vehicule_affectation_create, name='vehicule_affectation_create'),
    path('vehicules/affectations/<int:affectation_id>/cloturer/', views.vehicule_affectation_close, name='vehicule_affectation_close'),
    path('vehicules/<int:pk>/documents/ajouter/', views.vehicule_document_create, name='vehicule_document_create'),
    path('vehicules/<int:pk>/supprimer/', views.vehicule_delete, name='vehicule_delete'),
    
    # Routes pour les cartes carburant
    path('cartes-carburant/', views.cartes_carburant_list, name='cartes_carburant_list'),
    path('cartes-carburant/ajouter/', views.carte_carburant_create, name='carte_carburant_create'),
    path('cartes-carburant/<int:pk>/', views.carte_carburant_detail, name='carte_carburant_detail'),
    path('cartes-carburant/<int:pk>/modifier/', views.carte_carburant_update, name='carte_carburant_update'),
    path('cartes-carburant/<int:pk>/supprimer/', views.carte_carburant_delete, name='carte_carburant_delete'),
    
    # Routes pour les fournisseurs
    path('fournisseurs/', views.fournisseurs_list, name='fournisseurs_list'),
    path('fournisseurs/ajouter/', views.fournisseur_create, name='fournisseur_create'),
    path('fournisseurs/<int:pk>/', views.fournisseur_detail, name='fournisseur_detail'),
    path('fournisseurs/<int:pk>/modifier/', views.fournisseur_update, name='fournisseur_update'),
    path('fournisseurs/<int:pk>/supprimer/', views.fournisseur_delete, name='fournisseur_delete'),
    
    # Routes pour les achats de carburant HT
    path('achats-carburant-ht/', views.achats_carburant_ht_list, name='achats_carburant_ht_list'),
    path('achats-carburant-ht/ajouter/', views.achat_carburant_ht_create, name='achat_carburant_ht_create'),
    path('achats-carburant-ht/<int:pk>/', views.achat_carburant_ht_detail, name='achat_carburant_ht_detail'),
    path('achats-carburant-ht/<int:pk>/modifier/', views.achat_carburant_ht_update, name='achat_carburant_ht_update'),
    path('achats-carburant-ht/<int:pk>/supprimer/', views.achat_carburant_ht_delete, name='achat_carburant_ht_delete'),
    
    # Routes pour les achats de carburant TTC
    path('achats-carburant-ttc/', views.achats_carburant_ttc_list, name='achats_carburant_ttc_list'),
    path('achats-carburant-ttc/ajouter/', views.achat_carburant_ttc_create, name='achat_carburant_ttc_create'),
    path('achats-carburant-ttc/<int:pk>/', views.achat_carburant_ttc_detail, name='achat_carburant_ttc_detail'),
    path('achats-carburant-ttc/<int:pk>/modifier/', views.achat_carburant_ttc_update, name='achat_carburant_ttc_update'),
    path('achats-carburant-ttc/<int:pk>/supprimer/', views.achat_carburant_ttc_delete, name='achat_carburant_ttc_delete'),
    path('achats-carburant-ttc/<int:pk>/rechargements/', views.achat_carburant_ttc_rechargement, name='achat_carburant_ttc_rechargement'),
    
    # Routes pour les rechargements de cartes carburant
    path('rechargements-carte-carburant/', views.rechargements_carte_carburant_list, name='rechargements_carte_carburant_list'),
    path('rechargements-carte-carburant/ajouter/', views.rechargement_carte_carburant_create, name='rechargement_carte_carburant_create'),
    path('rechargements-carte-carburant/<int:pk>/', views.rechargement_carte_carburant_detail, name='rechargement_carte_carburant_detail'),
    path('rechargements-carte-carburant/<int:pk>/modifier/', views.rechargement_carte_carburant_update, name='rechargement_carte_carburant_update'),
    path('rechargements-carte-carburant/<int:pk>/supprimer/', views.rechargement_carte_carburant_delete, name='rechargement_carte_carburant_delete'),
    path('achats-carburant-ht/<int:pk>/rechargements/', views.achat_stock_carburant_rechargement, name='achat_stock_carburant_rechargement'),
    
    # Routes pour les demandes de carte carburant
    path('demandes-carte-carburant/', views.demandes_carte_carburant_list, name='demandes_carte_carburant_list'),
    path('demandes-carte-carburant/creer/', views.demande_carte_carburant_create, name='demande_carte_carburant_create'),
    path('demandes-carte-carburant/<int:pk>/', views.demande_carte_carburant_detail, name='demande_carte_carburant_detail'),
    path('demandes-carte-carburant/<int:pk>/traiter/', views.demande_carte_carburant_traitement, name='demande_carte_carburant_traitement'),
    path('demandes-carte-carburant/<int:pk>/cloturer/', views.demande_carte_carburant_cloture, name='demande_carte_carburant_cloture'),
    path('demandes-carte-carburant/<int:pk>/supprimer/', views.demande_carte_carburant_delete, name='demande_carte_carburant_delete'),
    
    # Route pour le tableau de bord carburant
    path('carburant/dashboard/', views.dashboard_carburant, name='dashboard_carburant'),
    
    # API pour les cartes carburant
    path('api/cartes-by-dotation/', views.get_cartes_by_dotation, name='get_cartes_by_dotation'),
    
    # Dotations de carburant
    path('dotations/suivi/', views.suivi_dotations, name='suivi_dotations'),
    path('dotations/detail/<str:dotation_type>/<int:dotation_id>/', views.dotation_detail, name='dotation_detail'),
    
    # Route pour les rapports
    path('rapports/mensuel-consommation/', views.rapport_mensuel_consommation, name='rapport_mensuel_consommation'),
    path('rapports/releve-consommation/', views.releve_consommation_carburant, name='releve_consommation_carburant'),
    path('rapports/etat-ravitaillements/', views.etat_ravitaillements, name='etat_ravitaillements'),
    
    # Route pour l'interface mobile
    path('mobile/', views.home_view, {'template_name': 'core/mobile.html'}, name='mobile'),
    
    # Route pour les logs d'emails
    path('admin/email-logs/', views_admin.view_email_logs, name='view_email_logs'),
    
    # Route pour le téléchargement de la fiche de ravitaillement
    path('telecharger-fiche-ravitaillement/<int:pk>/', views.telecharger_fiche_ravitaillement, name='telecharger_fiche_ravitaillement'),
    path('regenerer-fiche-ravitaillement/<int:pk>/', views.regenerer_fiche_ravitaillement, name='regenerer_fiche_ravitaillement'),
    
    # Routes pour les types de maintenance
    path('types-maintenance/', views.TypeMaintenanceListView.as_view(), name='type_maintenance_list'),
    path('types-maintenance/ajouter/', views.TypeMaintenanceCreateView.as_view(), name='type_maintenance_create'),
    path('types-maintenance/<int:id>/modifier/', views.TypeMaintenanceUpdateView.as_view(), name='type_maintenance_update'),
    path('types-maintenance/<int:id>/supprimer/', views.TypeMaintenanceDeleteView.as_view(), name='type_maintenance_delete'),
    
    # Routes pour les maintenances
    path('maintenances/', views.MaintenanceListView.as_view(), name='maintenance_list'),
    path('maintenances/ajouter/', views.MaintenanceCreateView.as_view(), name='maintenance_create'),
    path('maintenances/<int:id>/', views.MaintenanceDetailView.as_view(), name='maintenance_detail'),
    path('maintenances/<int:id>/modifier/', views.MaintenanceUpdateView.as_view(), name='maintenance_update'),
    path('maintenances/<int:id>/supprimer/', views.MaintenanceDeleteView.as_view(), name='maintenance_delete'),
    
    # Routes pour les planifications de maintenance
    path('planifications/', views.PlanificationListView.as_view(), name='planification_list'),
    path('planifications/create/', views.PlanificationCreateView.as_view(), name='planification_create'),
    path('planifications/<int:pk>/update/', views.PlanificationUpdateView.as_view(), name='planification_update'),
    path('planifications/<int:pk>/delete/', views.PlanificationDeleteView.as_view(), name='planification_delete'),
    path('planifications/<int:pk>/', views.PlanificationDetailView.as_view(), name='planification_detail'),
    
    # URLs pour les rapports de maintenance
    path('maintenance/rapport/', views.MaintenanceReportView.as_view(), name='maintenance_report'),
    path('maintenance/rapport/pdf/', views.MaintenanceReportExportPDF.as_view(), name='maintenance_report_pdf'),
    path('maintenance/rapport/excel/', views.MaintenanceReportExportExcel.as_view(), name='maintenance_report_excel'),
    
    # API pour le kilométrage des véhicules
    path('api/vehicule/<int:id_vehicule>/kilometrage/', views.get_vehicule_kilometrage, name='api_vehicule_kilometrage'),
    
    # Demandes de course
    path('demandes-courses/', views.demandes_course_list, name='demandes_course_list'),
    path('demandes-courses/ajouter/', views.demande_course_create, name='demande_course_create'),
    path('demandes-courses/<int:pk>/', views.demande_course_detail, name='demande_course_detail'),
    path('demandes-courses/<int:pk>/modifier/', views.demande_course_update, name='demande_course_update'),
    path('demandes-courses/<int:pk>/traiter/', views.demande_course_traitement, name='demande_course_traitement'),
    # Route pour les demandes de course par utilisateur
    # path('demandes-courses/utilisateur/', views.demandes_course_utilisateur, name='demandes_course_utilisateur'),
    path('planification-courses/', views.planification_courses_view, name='planification_courses'),
    path('planification-courses/<int:pk>/', views.planification_course_detail, name='planification_course_detail'),    
]

# Ajout des URLs pour les fichiers statiques en mode développement
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
