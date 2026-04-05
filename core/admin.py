from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.http import HttpResponse
from django.urls import path
from django.utils.html import format_html
from django.conf import settings
import os
from .models import (
    Service, Groupe, Utilisateur, Vehicule, Carte_Carburant, 
    Fournisseur, Achat_Stock_Carburant_HT, Achat_Carburant_TTC,
    Demande_Carte_Carburant, Rechargement_Carte_Carburant_HT, Rechargement_Carte_Carburant_TTC,
    TypeMaintenance, Maintenance, Planification, DemandeCourse, PlanificationCourse
)
from django import forms

# Register your models here.

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('id_service', 'nom_service', 'description')
    search_fields = ('nom_service', 'description')
    ordering = ('nom_service',)


@admin.register(Groupe)
class GroupeAdmin(admin.ModelAdmin):
    list_display = ('id_groupe', 'nom_groupe')
    search_fields = ('nom_groupe',)
    ordering = ('nom_groupe',)


@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    list_display = ('email', 'nom_complet', 'fonction', 'statut', 'is_active', 'is_staff')
    list_filter = ('statut', 'is_active', 'is_staff', 'groupe', 'service')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informations personnelles', {'fields': ('nom_complet', 'fonction')}),
        ('Affiliations', {'fields': ('groupe', 'service')}),
        ('Statut', {'fields': ('statut', 'is_active', 'is_staff', 'is_superuser')}),
        ('Permissions', {'fields': ('groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nom_complet', 'password1', 'password2', 'fonction', 'statut', 'is_active', 'is_staff'),
        }),
    )
    search_fields = ('email', 'nom_complet', 'fonction')
    ordering = ('nom_complet',)
    filter_horizontal = ('groupe', 'service', 'groups', 'user_permissions')


@admin.register(Vehicule)
class VehiculeAdmin(admin.ModelAdmin):
    list_display = ('id_vehicule', 'immatriculation', 'marque', 'modele', 'service', 'type_carburant', 'kilometrage', 'statut')
    list_filter = ('service', 'marque', 'type_carburant', 'statut')
    search_fields = ('immatriculation', 'marque', 'modele', 'chassis')
    ordering = ('immatriculation',)
    fieldsets = (
        ('Informations générales', {'fields': ('service', 'marque', 'modele', 'immatriculation', 'chassis')}),
        ('Caractéristiques', {'fields': ('type_carburant', 'date_mise_en_service', 'kilometrage', 'statut')}),
        ('Documents', {'fields': ('document', 'photo')}),
    )


@admin.register(Carte_Carburant)
class CarteCarburantAdmin(admin.ModelAdmin):
    list_display = ('id_carte_carburant', 'numero_carte', 'service', 'vehicule', 'get_solde_actif_display', 'statut')
    list_filter = ('service', 'statut')
    search_fields = ('numero_carte',)
    ordering = ('numero_carte',)
    fieldsets = (
        ('Informations générales', {'fields': ('numero_carte', 'service', 'vehicule')}),
        ('État', {'fields': ('solde', 'statut')}),
    )
    
    def get_solde_actif_display(self, obj):
        """Affiche le solde actif de la carte carburant"""
        return obj.get_solde_actif_formate()
    
    get_solde_actif_display.short_description = "Solde (FCFA)"


@admin.register(Fournisseur)
class FournisseurAdmin(admin.ModelAdmin):
    list_display = ('id_fournisseur', 'nom_fournisseur', 'type_fournisseur', 'email', 'telephone')
    list_filter = ('type_fournisseur',)
    search_fields = ('nom_fournisseur', 'email', 'telephone')
    ordering = ('nom_fournisseur',)
    fieldsets = (
        ('Informations générales', {'fields': ('nom_fournisseur', 'type_fournisseur')}),
        ('Contact', {'fields': ('adresse', 'email', 'telephone')}),
    )


@admin.register(Achat_Stock_Carburant_HT)
class AchatStockCarburantHTAdmin(admin.ModelAdmin):
    list_display = ('id_achat_stock_carburant_ht', 'voucher', 'service', 'fournisseur', 'date_achat', 
                   'type_carburant', 'volume', 'montant_ht', 'montant_ttc', 'format_solde_theorique', 'statut')
    list_filter = ('service', 'fournisseur', 'type_carburant', 'statut')
    search_fields = ('voucher', 'libelle')
    ordering = ('-date_achat',)
    fieldsets = (
        ('Informations générales', {'fields': ('service', 'fournisseur', 'voucher', 'date_achat', 'libelle')}),
        ('Détails financiers', {'fields': ('business_unit', 'dept_id', 'project_id')}),
        ('Détails carburant', {'fields': ('type_carburant', 'volume', 'montant_ht', 'montant_ttc')}),
        ('État', {'fields': ('statut',)}),
        ('Documents', {'fields': ('document',)}),
    )
    readonly_fields = ('tx_taxe', 'statut')
    
    def format_solde_theorique(self, obj):
        return obj.format_solde_theorique()
    format_solde_theorique.short_description = "Solde théorique"


@admin.register(Achat_Carburant_TTC)
class AchatCarburantTTCAdmin(admin.ModelAdmin):
    list_display = ('id_achat_carburant_ttc', 'voucher', 'service', 'fournisseur', 'date_achat', 
                   'type_carburant', 'volume', 'montant_ttc', 'format_solde_theorique', 'statut')
    list_filter = ('service', 'fournisseur', 'type_carburant', 'statut')
    search_fields = ('voucher', 'libelle')
    ordering = ('-date_achat',)
    fieldsets = (
        ('Informations générales', {'fields': ('service', 'fournisseur', 'voucher', 'date_achat', 'libelle')}),
        ('Détails financiers', {'fields': ('business_unit', 'dept_id', 'project_id')}),
        ('Détails carburant', {'fields': ('type_carburant', 'volume', 'montant_ttc')}),
        ('État', {'fields': ('statut',)}),
        ('Documents', {'fields': ('document',)}),
    )
    readonly_fields = ('statut',)
    
    def format_solde_theorique(self, obj):
        return obj.format_solde_theorique()
    format_solde_theorique.short_description = "Solde théorique"


class DemandeCarteCarburantAdminForm(forms.ModelForm):
    """
    Formulaire personnalisé pour l'administration des demandes de cartes carburant
    """
    class Meta:
        model = Demande_Carte_Carburant
        fields = '__all__'
        widgets = {
            'rechargement_ht': forms.Select(attrs={'class': 'form-control'}),
            'rechargement_ttc': forms.Select(attrs={'class': 'form-control'}),
        }

@admin.register(Demande_Carte_Carburant)
class DemandeCarteCarburantAdmin(admin.ModelAdmin):
    form = DemandeCarteCarburantAdminForm
    list_display = ('id_demande', 'utilisateur_demandeur', 'service', 'vehicule', 'get_dotation_libelle', 'date_demande', 'statut_demande', 'utilisateur_traitant', 'date_traitement')
    list_filter = ('service', 'statut_demande', 'date_demande')
    search_fields = ('utilisateur_demandeur__nom_complet', 'vehicule__immatriculation', 'motif_demande')
    ordering = ('-date_demande',)
    fieldsets = (
        ('Informations de la demande', {'fields': ('utilisateur_demandeur', 'service', 'vehicule', 'motif_demande')}),
        ('Rechargement', {'fields': ('rechargement_ht', 'rechargement_ttc'), 'classes': ('wide',)}),
        ('Traitement', {'fields': ('statut_demande', 'utilisateur_traitant', 'commentaire')}),
        ('Ravitaillement', {'fields': ('date_ravitaillement', 'km_vehicule', 'prix_unitaire_ttc', 'volume', 'montant_ttc', 'station_service')}),
        ('Documents', {'fields': ('document',)}),
    )
    readonly_fields = ('date_demande', 'date_traitement', 'date_cloture')

    def get_dotation_libelle(self, obj):
        if obj.rechargement_ht:
            return obj.rechargement_ht.achat_stock_carburant_ht.libelle
        elif obj.rechargement_ttc:
            return obj.rechargement_ttc.achat_carburant_ttc.libelle
        else:
            return "-"

    get_dotation_libelle.short_description = "Dotation"


@admin.register(Rechargement_Carte_Carburant_HT)
class RechargementCarteCarburantHTAdmin(admin.ModelAdmin):
    list_display = ('id_rechargement_ht', 'get_achat_stock_libelle', 'carte_carburant', 'date_rechargement', 'volume', 'prix_unitaire_ttc', 'montant_ttc')
    list_filter = ('achat_stock_carburant_ht', 'carte_carburant', 'date_rechargement')
    search_fields = ('carte_carburant__numero_carte',)
    ordering = ('-date_rechargement',)
    fieldsets = (
        ('Informations générales', {'fields': ('achat_stock_carburant_ht', 'carte_carburant', 'date_rechargement')}),
        ('Détails du rechargement', {'fields': ('volume', 'prix_unitaire_ttc', 'montant_ttc')}),
    )
    
    def get_achat_stock_libelle(self, obj):
        return obj.achat_stock_carburant_ht.libelle if obj.achat_stock_carburant_ht else "-"
    
    get_achat_stock_libelle.short_description = "Achat stock carburant HT"
    get_achat_stock_libelle.admin_order_field = 'achat_stock_carburant_ht__libelle'


@admin.register(Rechargement_Carte_Carburant_TTC)
class RechargementCarteCarburantTTCAdmin(admin.ModelAdmin):
    list_display = ('id_rechargement_ttc', 'achat_carburant_ttc', 'carte_carburant', 'date_rechargement', 'volume', 'prix_unitaire_ttc', 'montant_ttc')
    list_filter = ('achat_carburant_ttc', 'carte_carburant', 'date_rechargement')
    search_fields = ('carte_carburant__numero_carte',)
    ordering = ('-date_rechargement',)
    fieldsets = (
        ('Informations générales', {'fields': ('achat_carburant_ttc', 'carte_carburant', 'date_rechargement')}),
        ('Détails du rechargement', {'fields': ('volume', 'prix_unitaire_ttc', 'montant_ttc')}),
    )


class EmailLogsAdmin(admin.ModelAdmin):
    """
    Vue d'administration pour consulter les logs d'emails
    """
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('email-logs/', self.admin_site.admin_view(self.view_email_logs), name='view_email_logs'),
        ]
        return custom_urls + urls
    
    def view_email_logs(self, request):
        """
        Vue pour afficher les logs d'emails
        """
        log_file = os.path.join(settings.BASE_DIR, 'logs', 'email_logs.txt')
        
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                content = f.read()
        else:
            content = "Aucun log d'email disponible."
        
        # Formater le contenu pour l'affichage HTML
        content = content.replace('\n', '<br>')
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Logs d'emails</title>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 20px; }}
                h1 {{ color: #0d6efd; }}
                .log-container {{ 
                    background-color: #f8f9fa; 
                    padding: 15px; 
                    border-radius: 5px; 
                    border: 1px solid #ddd;
                    max-height: 600px;
                    overflow-y: auto;
                }}
                .refresh-btn {{
                    background-color: #0d6efd;
                    color: white;
                    padding: 10px 15px;
                    text-decoration: none;
                    border-radius: 5px;
                    display: inline-block;
                    margin-top: 15px;
                }}
            </style>
        </head>
        <body>
            <h1>Logs d'emails</h1>
            <div class="log-container">
                {content}
            </div>
            <a href="." class="refresh-btn">Rafraîchir</a>
        </body>
        </html>
        """
        
        return HttpResponse(html)


@admin.register(TypeMaintenance)
class TypeMaintenanceAdmin(admin.ModelAdmin):
    """
    Vue d'administration pour les types de maintenance
    """
    list_display = ('id', 'libelle')
    search_fields = ('libelle',)
    ordering = ('libelle',)


@admin.register(Maintenance)
class MaintenanceAdmin(admin.ModelAdmin):
    """
    Vue d'administration pour les maintenances de véhicules
    """
    list_display = ('id', 'service', 'vehicule', 'type_maintenance', 'fournisseur', 'date', 'km_vehicule', 'format_montant')
    list_filter = ('service', 'type_maintenance', 'fournisseur', 'date')
    search_fields = ('vehicule__immatriculation', 'detail')
    ordering = ('-date',)
    fieldsets = (
        ('Informations générales', {'fields': ('service', 'vehicule', 'type_maintenance', 'detail')}),
        ('Fournisseur et coût', {'fields': ('fournisseur', 'date', 'km_vehicule', 'montant')}),
        ('Périodicité', {'fields': ('periodicite_km', 'alerte_km', 'periodicite_mois', 'alerte_mois')}),
        ('Documents', {'fields': ('facture',)}),
    )
    
    def format_montant(self, obj):
        return obj.format_montant()
    
    format_montant.short_description = "Montant (FCFA)"


@admin.register(Planification)
class PlanificationAdmin(admin.ModelAdmin):
    """
    Configuration de l'interface d'administration pour les planifications de maintenance.
    """
    list_display = ('id', 'service', 'vehicule', 'type_maintenance', 'utilisateur', 
                   'prochaine_echeance_km', 'prochaine_echeance_date', 'get_statut_display')
    list_filter = ('service', 'type_maintenance', 'utilisateur')
    search_fields = ('vehicule__immatriculation', 'vehicule__marque', 'vehicule__modele', 
                    'type_maintenance__libelle', 'utilisateur__username')
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('service', 'utilisateur', 'vehicule', 'type_maintenance')
        }),
        ('Échéances', {
            'fields': ('prochaine_echeance_km', 'prochaine_echeance_date')
        }),
        ('Alertes', {
            'fields': ('alerte_km', 'alerte_mois')
        }),
    )
    
    def get_statut_display(self, obj):
        """
        Affiche le statut de la planification avec un style visuel.
        """
        statut = obj.get_statut()
        if statut == "En retard":
            return format_html('<span style="color:red; font-weight:bold;">En retard</span>')
        elif statut == "En alerte":
            return format_html('<span style="color:orange; font-weight:bold;">En alerte</span>')
        else:
            return format_html('<span style="color:green;">Planifiée</span>')
    
    get_statut_display.short_description = "Statut"


class DemandeCourseAdminForm(forms.ModelForm):
    class Meta:
        model = DemandeCourse
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.fields['id_utilisateur'].queryset = User.objects.filter(groupe__nom_groupe__startswith="Driver").distinct()

class DemandeCourseAdmin(admin.ModelAdmin):
    form = DemandeCourseAdminForm
    list_display = ('id_demande_course', 'id_service', 'id_utilisateur', 'id_vehicule', 'id_auteur', 'date_demande', 'statut')
    list_filter = ('statut', 'id_service', 'id_vehicule')
    search_fields = ('id_demande_course', 'id_utilisateur__username', 'id_vehicule__immatriculation', 'objet')
    readonly_fields = ('id_auteur',)
    date_hierarchy = 'date_demande'

admin.site.register(DemandeCourse, DemandeCourseAdmin)


@admin.register(PlanificationCourse)
class PlanificationCourseAdmin(admin.ModelAdmin):
    list_display = ('id_planification', 'demande', 'date_heure', 'utilisateur', 'vehicule', 'statut', 'lieu_arrivee')
    search_fields = ('demande__id_demande_course', 'utilisateur__username', 'vehicule__immatriculation', 'lieu_arrivee')
    list_filter = ('statut', 'vehicule', 'lieu_arrivee')
    # list_editable = ('lieu_arrivee',)
