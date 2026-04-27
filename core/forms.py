from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import (
    Service, Groupe, Utilisateur, Vehicule, Carte_Carburant, 
    Fournisseur, Achat_Stock_Carburant_HT, Achat_Carburant_TTC, 
    Rechargement_Carte_Carburant_HT, Rechargement_Carte_Carburant_TTC,
    Demande_Carte_Carburant, TypeMaintenance, Maintenance, Planification, DemandeCourse, PlanificationCourse,
    ExecutionCourse
)
from django.utils import timezone
from django.db import models

class LoginForm(AuthenticationForm):
    """
    Formulaire de connexion personnalisé.
    """
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Adresse email'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mot de passe'})
    )


class ServiceForm(forms.ModelForm):
    """
    Formulaire pour la création et la modification des services.
    """
    class Meta:
        model = Service
        fields = ['nom_service', 'description']
        widgets = {
            'nom_service': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class GroupeForm(forms.ModelForm):
    """
    Formulaire pour la création et la modification des groupes.
    """
    class Meta:
        model = Groupe
        fields = ['nom_groupe', 'description']
        widgets = {
            'nom_groupe': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class UtilisateurCreationForm(UserCreationForm):
    """
    Formulaire pour la création d'utilisateurs.
    """
    class Meta:
        model = Utilisateur
        fields = ['nom_complet', 'email', 'fonction', 'groupe', 'service', 'statut', 'password1', 'password2']
        widgets = {
            'nom_complet': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'fonction': forms.TextInput(attrs={'class': 'form-control'}),
            'groupe': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'service': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'statut': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})


class UtilisateurUpdateForm(forms.ModelForm):
    """
    Formulaire pour la modification d'utilisateurs.
    """
    class Meta:
        model = Utilisateur
        fields = ['nom_complet', 'email', 'fonction', 'groupe', 'service', 'statut', 'is_active']
        widgets = {
            'nom_complet': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'fonction': forms.TextInput(attrs={'class': 'form-control'}),
            'groupe': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'service': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'statut': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class VehiculeForm(forms.ModelForm):
    """
    Formulaire pour la création et la modification des véhicules.
    """
    class Meta:
        model = Vehicule
        fields = [
            'service', 'marque', 'modele', 'chassis', 'immatriculation',
            'type_carburant', 'date_mise_en_service', 'kilometrage',
            'document', 'photo'
        ]
        widgets = {
            'service': forms.Select(attrs={'class': 'form-control'}),
            'marque': forms.TextInput(attrs={'class': 'form-control'}),
            'modele': forms.TextInput(attrs={'class': 'form-control'}),
            'chassis': forms.TextInput(attrs={'class': 'form-control'}),
            'immatriculation': forms.TextInput(attrs={'class': 'form-control'}),
            'type_carburant': forms.Select(attrs={'class': 'form-control'}),
            'date_mise_en_service': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'kilometrage': forms.NumberInput(attrs={'class': 'form-control'}),
            'document': forms.FileInput(attrs={'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        # Définir le statut par défaut à "Disponible" lors de la création
        if not instance.pk:  # Si c'est une nouvelle instance
            instance.statut = 'Disponible'
        if commit:
            instance.save()
        return instance


class CarteCarburantForm(forms.ModelForm):
    """
    Formulaire pour la modification des cartes carburant.
    Permet de modifier les informations d'une carte carburant existante.
    Le statut est automatiquement mis à jour dans la méthode save() du modèle.
    """
    class Meta:
        model = Carte_Carburant
        fields = ['numero_carte', 'service', 'vehicule', 'solde', 'statut']
        widgets = {
            'numero_carte': forms.TextInput(attrs={'class': 'form-control'}),
            'service': forms.Select(attrs={'class': 'form-control'}),
            'vehicule': forms.Select(attrs={'class': 'form-control'}),
            'solde': forms.NumberInput(attrs={'class': 'form-control'}),
            'statut': forms.Select(attrs={'class': 'form-control'}),
        }


class CarteCarburantCreateForm(forms.ModelForm):
    """
    Formulaire pour la création des cartes carburant.
    Le statut est automatiquement défini en fonction du solde:
    - Si le solde est 0, le statut est 'Non disponible'
    - Si le solde est supérieur à 0, le statut est 'Disponible'
    """
    class Meta:
        model = Carte_Carburant
        fields = ['numero_carte', 'service', 'vehicule', 'solde']
        widgets = {
            'numero_carte': forms.TextInput(attrs={'class': 'form-control'}),
            'service': forms.Select(attrs={'class': 'form-control'}),
            'vehicule': forms.Select(attrs={'class': 'form-control'}),
            'solde': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        # Définir le statut en fonction du solde
        if instance.solde == 0:
            instance.statut = 'Non disponible'
        else:
            instance.statut = 'Disponible'
        
        if commit:
            instance.save()
        return instance


class FournisseurForm(forms.ModelForm):
    """
    Formulaire pour la création et la modification des fournisseurs.
    """
    class Meta:
        model = Fournisseur
        fields = ['nom_fournisseur', 'type_fournisseur', 'adresse', 'email', 'telephone']
        widgets = {
            'nom_fournisseur': forms.TextInput(attrs={'class': 'form-control'}),
            'type_fournisseur': forms.Select(attrs={'class': 'form-control'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
        }


class AchatStockCarburantHTForm(forms.ModelForm):
    """
    Formulaire pour la création et la modification des achats de stock de carburant HT.
    """
    class Meta:
        model = Achat_Stock_Carburant_HT
        fields = [
            'service', 'fournisseur', 'voucher', 'business_unit', 'dept_id',
            'project_id', 'date_achat', 'libelle', 'type_carburant', 'volume',
            'montant_ht', 'montant_ttc', 'document'
        ]
        widgets = {
            'service': forms.Select(attrs={'class': 'form-control'}),
            'fournisseur': forms.Select(attrs={'class': 'form-control'}),
            'voucher': forms.TextInput(attrs={'class': 'form-control'}),
            'business_unit': forms.TextInput(attrs={'class': 'form-control'}),
            'dept_id': forms.TextInput(attrs={'class': 'form-control'}),
            'project_id': forms.TextInput(attrs={'class': 'form-control'}),
            'date_achat': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'libelle': forms.TextInput(attrs={'class': 'form-control'}),
            'type_carburant': forms.Select(attrs={'class': 'form-control'}),
            'volume': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'montant_ht': forms.NumberInput(attrs={'class': 'form-control'}),
            'montant_ttc': forms.NumberInput(attrs={'class': 'form-control'}),
            'document': forms.FileInput(attrs={'class': 'form-control'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrer les fournisseurs pour n'afficher que ceux de type "Carburant"
        self.fields['fournisseur'].queryset = Fournisseur.objects.filter(type_fournisseur='Carburant')


class AchatCarburantTTCForm(forms.ModelForm):
    """
    Formulaire pour la création et la modification des achats de carburant TTC.
    """
    class Meta:
        model = Achat_Carburant_TTC
        fields = [
            'service', 'libelle', 'fournisseur', 'voucher', 'business_unit',
            'dept_id', 'project_id', 'date_achat', 'type_carburant', 'volume',
            'montant_ttc', 'document'
        ]
        widgets = {
            'service': forms.Select(attrs={'class': 'form-control'}),
            'libelle': forms.TextInput(attrs={'class': 'form-control'}),
            'fournisseur': forms.Select(attrs={'class': 'form-control'}),
            'voucher': forms.TextInput(attrs={'class': 'form-control'}),
            'business_unit': forms.TextInput(attrs={'class': 'form-control'}),
            'dept_id': forms.TextInput(attrs={'class': 'form-control'}),
            'project_id': forms.TextInput(attrs={'class': 'form-control'}),
            'date_achat': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'type_carburant': forms.Select(attrs={'class': 'form-control'}),
            'volume': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'montant_ttc': forms.NumberInput(attrs={'class': 'form-control'}),
            'document': forms.FileInput(attrs={'class': 'form-control'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrer les fournisseurs pour n'afficher que ceux de type "Carburant"
        self.fields['fournisseur'].queryset = Fournisseur.objects.filter(type_fournisseur='Carburant')


class RechargementCarteCarburantHTForm(forms.ModelForm):
    """
    Formulaire pour la création et la modification des rechargements de cartes carburant HT.
    """
    class Meta:
        model = Rechargement_Carte_Carburant_HT
        fields = ['date_rechargement', 'carte_carburant', 'volume', 'prix_unitaire_ttc', 'montant_ttc']
        widgets = {
            'date_rechargement': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'carte_carburant': forms.Select(attrs={'class': 'form-control'}),
            'volume': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'prix_unitaire_ttc': forms.NumberInput(attrs={'class': 'form-control'}),
            'montant_ttc': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class RechargementCarteCarburantTTCForm(forms.ModelForm):
    """
    Formulaire pour la création et la modification des rechargements de cartes carburant TTC.
    """
    class Meta:
        model = Rechargement_Carte_Carburant_TTC
        fields = ['date_rechargement', 'carte_carburant', 'volume', 'prix_unitaire_ttc', 'montant_ttc']
        widgets = {
            'date_rechargement': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'carte_carburant': forms.Select(attrs={'class': 'form-control'}),
            'volume': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'prix_unitaire_ttc': forms.NumberInput(attrs={'class': 'form-control'}),
            'montant_ttc': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class DemandeCarteCarburantCreateForm(forms.ModelForm):
    """
    Formulaire pour la création d'une demande de carte carburant (Phase 1).
    Utilisé par le chauffeur (Driver) pour initier une demande.
    """
    
    class Meta:
        model = Demande_Carte_Carburant
        fields = ['service', 'vehicule', 'motif_demande']
        widgets = {
            'service': forms.Select(attrs={'class': 'form-control'}),
            'vehicule': forms.Select(attrs={'class': 'form-control'}),
            'motif_demande': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtrer les services selon l'utilisateur mais afficher tous les véhicules
        if user:
            services = user.service.all()
            self.fields['service'].queryset = services
            # Afficher tous les véhicules disponibles, indépendamment du service
            self.fields['vehicule'].queryset = Vehicule.objects.all()


class DemandeCarteCarburantTraitementForm(forms.ModelForm):
    """
    Formulaire pour le traitement d'une demande de carte carburant par le gestionnaire
    """
    STATUT_CHOICES = (
        ('En attente', 'En attente'),
        ('Acceptée', 'Acceptée'),
        ('Rejetée', 'Rejetée'),
    )
    
    statut_demande = forms.ChoiceField(
        choices=STATUT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Statut de la demande"
    )
    
    # Champ pour sélectionner un rechargement (dotation)
    dotation = forms.ChoiceField(
        choices=[],
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Dotation",
        required=False
    )
    
    commentaire = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label="Commentaire",
        required=False
    )
    
    class Meta:
        model = Demande_Carte_Carburant
        fields = ['statut_demande', 'commentaire']
    
    def __init__(self, *args, **kwargs):
        self.service = kwargs.pop('service', None)
        super(DemandeCarteCarburantTraitementForm, self).__init__(*args, **kwargs)
        
        if self.service:
            # Initialiser les choix de dotation (rechargements)
            dotation_choices = [('', '---------')]
            
            # Récupérer tous les rechargements HT disponibles
            rechargements_ht = Rechargement_Carte_Carburant_HT.objects.filter(
                carte_carburant__service=self.service,
                carte_carburant__statut='Disponible'
            ).select_related('achat_stock_carburant_ht', 'carte_carburant').order_by('-date_rechargement')
            
            # Ajouter un message de débogage
            print(f"Nombre de rechargements HT trouvés: {rechargements_ht.count()}")
            
            for rechargement in rechargements_ht:
                # Initialiser solde_restant s'il est None
                if rechargement.solde_restant is None:
                    rechargement.solde_restant = rechargement.montant_ttc
                    rechargement.save()
                
                # Ajouter un message de débogage
                print(f"Rechargement HT ID: {rechargement.id_rechargement_ht}, Carte: {rechargement.carte_carburant.numero_carte}, Solde restant: {rechargement.solde_restant}")
                
                # Vérifier que le rechargement a un solde suffisant
                if rechargement.carte_carburant and rechargement.solde_restant and rechargement.solde_restant > 0:
                    dotation_choices.append(
                        (f"HT_{rechargement.id_rechargement_ht}", 
                         f"{rechargement.achat_stock_carburant_ht.libelle} Carte {rechargement.carte_carburant.numero_carte} {rechargement.solde_restant:,} FCFA".replace(",", " "))
                    )
            
            # Récupérer tous les rechargements TTC disponibles
            rechargements_ttc = Rechargement_Carte_Carburant_TTC.objects.filter(
                carte_carburant__service=self.service,
                carte_carburant__statut='Disponible'
            ).select_related('achat_carburant_ttc', 'carte_carburant').order_by('-date_rechargement')
            
            # Ajouter un message de débogage
            print(f"Nombre de rechargements TTC trouvés: {rechargements_ttc.count()}")
            
            for rechargement in rechargements_ttc:
                # Initialiser solde_restant s'il est None
                if rechargement.solde_restant is None:
                    rechargement.solde_restant = rechargement.montant_ttc
                    rechargement.save()
                
                # Ajouter un message de débogage
                print(f"Rechargement TTC ID: {rechargement.id_rechargement_ttc}, Carte: {rechargement.carte_carburant.numero_carte}, Solde restant: {rechargement.solde_restant}")
                
                # Vérifier que le rechargement a un solde suffisant
                if rechargement.carte_carburant and rechargement.solde_restant and rechargement.solde_restant > 0:
                    dotation_choices.append(
                        (f"TTC_{rechargement.id_rechargement_ttc}", 
                         f"{rechargement.achat_carburant_ttc.libelle} Carte {rechargement.carte_carburant.numero_carte} {rechargement.solde_restant:,} FCFA".replace(",", " "))
                    )
            
            # Ajouter un message de débogage
            print(f"Nombre total de choix de dotation: {len(dotation_choices)}")
            
            self.fields['dotation'].choices = dotation_choices
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Récupérer la dotation sélectionnée
        dotation = self.cleaned_data.get('dotation')
        
        if dotation and instance.statut_demande == 'Acceptée':
            dotation_type, dotation_id = dotation.split('_')
            
            # Associer le rechargement approprié à la demande
            if dotation_type == 'HT':
                instance.rechargement_ht = Rechargement_Carte_Carburant_HT.objects.get(id_rechargement_ht=dotation_id)
                instance.rechargement_ttc = None
            elif dotation_type == 'TTC':
                instance.rechargement_ttc = Rechargement_Carte_Carburant_TTC.objects.get(id_rechargement_ttc=dotation_id)
                instance.rechargement_ht = None
        
        if commit:
            instance.save()
        
        return instance


class DemandeCarteCarburantClotureForm(forms.ModelForm):
    """
    Formulaire pour la clôture d'une demande de carte carburant (Phase 3).
    Utilisé après le ravitaillement pour finaliser la demande.
    """
    class Meta:
        model = Demande_Carte_Carburant
        fields = [
            'date_ravitaillement', 'km_vehicule', 'prix_unitaire_ttc',
            'volume', 'montant_ttc', 'station_service', 'document'
        ]
        widgets = {
            'date_ravitaillement': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'km_vehicule': forms.NumberInput(attrs={'class': 'form-control'}),
            'prix_unitaire_ttc': forms.NumberInput(attrs={'class': 'form-control'}),
            'volume': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'montant_ttc': forms.NumberInput(attrs={'class': 'form-control'}),
            'station_service': forms.TextInput(attrs={'class': 'form-control'}),
            'document': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def clean_km_vehicule(self):
        """
        Validation pour s'assurer que le kilométrage saisi n'est pas inférieur 
        au kilométrage actuel du véhicule.
        """
        km_vehicule = self.cleaned_data.get('km_vehicule')
        
        # Si l'instance existe déjà et a un véhicule associé
        if self.instance and self.instance.vehicule:
            km_actuel = self.instance.vehicule.kilometrage
            
            if km_vehicule < km_actuel:
                raise forms.ValidationError(
                    f"Le kilométrage saisi ({km_vehicule} km) ne peut pas être inférieur au kilométrage actuel du véhicule ({km_actuel} km)."
                )
        
        return km_vehicule
    
    def clean(self):
        cleaned_data = super().clean()
        volume = cleaned_data.get('volume')
        prix_unitaire_ttc = cleaned_data.get('prix_unitaire_ttc')
        montant_ttc = cleaned_data.get('montant_ttc')
        
        # Calculer le montant TTC à partir du volume et du prix unitaire
        if volume and prix_unitaire_ttc and not montant_ttc:
            montant_calcule = int(float(volume) * prix_unitaire_ttc)
            cleaned_data['montant_ttc'] = montant_calcule
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Calculer le montant TTC si non fourni
        if instance.volume and instance.prix_unitaire_ttc and not instance.montant_ttc:
            instance.montant_ttc = int(float(instance.volume) * instance.prix_unitaire_ttc)
        
        # Définir le statut comme "Close"
        instance.statut_demande = 'Close'
        instance.date_cloture = timezone.now()
        
        # Mettre à jour le kilométrage du véhicule si nécessaire
        if instance.vehicule and instance.km_vehicule > instance.vehicule.kilometrage:
            vehicule = instance.vehicule
            vehicule.kilometrage = instance.km_vehicule
            vehicule.save()
        
        if commit:
            instance.save()
        
        return instance


class DemandeCourseFormAmeliore(forms.ModelForm):
    """
    Formulaire amélioré pour la création/édition des demandes de course.
    """
    class Meta:
        model = DemandeCourse
        fields = [
            'id_service', 'lieu_depart', 'lieu_arrivee', 'date_heure_prevue',
            'date_heure_fin_retour', 'objet'
        ]
        widgets = {
            'id_service': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'lieu_depart': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Bureau', 'required': True}),
            'lieu_arrivee': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Aéroport FHB', 'required': True}),
            'date_heure_prevue': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local', 'required': True}),
            'date_heure_fin_retour': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local', 'required': True}),
            'objet': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Objet ou motif de la course', 'required': True}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['lieu_depart'].initial = 'Bureau'
        self.fields['id_service'].label = "Service demandeur"
        self.fields['lieu_depart'].label = "Lieu de départ"
        self.fields['lieu_arrivee'].label = "Lieu d'arrivée"
        self.fields['date_heure_prevue'].label = "Date et heure prévue"
        self.fields['date_heure_fin_retour'].label = "Date et heure de retour"
        self.fields['objet'].label = "Objet de la course"
        if user and not user.is_superuser:
            self.fields['id_service'].queryset = user.service.all()

    def clean(self):
        cleaned_data = super().clean()
        date_heure_prevue = cleaned_data.get('date_heure_prevue')
        date_heure_fin_retour = cleaned_data.get('date_heure_fin_retour')

        if date_heure_prevue and date_heure_fin_retour and date_heure_fin_retour <= date_heure_prevue:
            self.add_error('date_heure_fin_retour', "La date/heure de retour doit être postérieure à la date/heure prévue.")

        if date_heure_prevue and date_heure_prevue < timezone.now():
            self.add_error('date_heure_prevue', "La date/heure prévue ne peut pas être dans le passé.")

        return cleaned_data


class DemandeCourseTraitementForm(forms.ModelForm):
    """
    Formulaire pour le traitement des demandes de course.
    """
    STATUT_CHOICES = [
        ("acceptée", "Acceptée"),
        ("rejetée", "Rejetée"),
    ]
    statut = forms.ChoiceField(
        choices=STATUT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Statut de la demande"
    )
    class Meta:
        model = DemandeCourse
        fields = ['statut', 'justification_rejet', 'id_utilisateur', 'id_vehicule']
        widgets = {
            'justification_rejet': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'id_utilisateur': forms.Select(attrs={'class': 'form-control'}),
            'id_vehicule': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        service = self.instance.id_service if self.instance and self.instance.id_service else None

        # Par défaut: limiter aux drivers et véhicules disponibles du service de la demande
        drivers_qs = Utilisateur.objects.filter(models.Q(groupe__nom_groupe__icontains="Driver")).distinct()
        vehicules_qs = Vehicule.objects.filter(statut='Disponible')

        if service is not None:
            drivers_qs = drivers_qs.filter(service=service)
            vehicules_qs = vehicules_qs.filter(service=service)

        # Fallback si aucun résultat strictement par service
        if not drivers_qs.exists():
            drivers_qs = Utilisateur.objects.filter(models.Q(groupe__nom_groupe__icontains="Driver")).distinct()

        self.fields['id_utilisateur'].queryset = drivers_qs
        self.fields['id_vehicule'].queryset = vehicules_qs

        # Justification non requise par défaut
        self.fields['justification_rejet'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        statut = cleaned_data.get('statut')
        justification = cleaned_data.get('justification_rejet')
        id_utilisateur = cleaned_data.get('id_utilisateur')
        id_vehicule = cleaned_data.get('id_vehicule')
        if statut == 'rejetée':
            if not justification:
                self.add_error('justification_rejet', 'La justification du rejet est obligatoire.')
        elif statut == 'acceptée':
            if not id_utilisateur:
                self.add_error('id_utilisateur', 'Veuillez sélectionner un chauffeur.')
            if not id_vehicule:
                self.add_error('id_vehicule', 'Veuillez sélectionner un véhicule.')
        return cleaned_data


class TypeMaintenanceForm(forms.ModelForm):
    """
    Formulaire pour la création et la modification des types de maintenance.
    """
    class Meta:
        model = TypeMaintenance
        fields = ['libelle']
        widgets = {
            'libelle': forms.TextInput(attrs={'class': 'form-control'}),
        }


class MaintenanceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(MaintenanceForm, self).__init__(*args, **kwargs)
        
        # Filtrer les services pour n'afficher que ceux de l'utilisateur connecté
        if user:
            self.fields['service'].queryset = user.service.all()
            
            # Filtrer les véhicules en fonction des services de l'utilisateur
            services_ids = user.service.values_list('id_service', flat=True)
            self.fields['vehicule'].queryset = Vehicule.objects.filter(service__id_service__in=services_ids)
            
            # Filtrer les fournisseurs pour n'afficher que ceux de type 'Maintenance'
            self.fields['fournisseur'].queryset = Fournisseur.objects.filter(type_fournisseur='Maintenance')
    
    def clean(self):
        cleaned_data = super().clean()
        
        return cleaned_data
    
    class Meta:
        model = Maintenance
        fields = ['service', 'vehicule', 'type_maintenance', 'detail', 'fournisseur', 'date', 'km_vehicule', 
                  'montant', 'periodicite_km', 'alerte_km', 'periodicite_mois', 'alerte_mois', 'facture']
        widgets = {
            'service': forms.Select(attrs={'class': 'form-control'}),
            'vehicule': forms.Select(attrs={'class': 'form-control'}),
            'type_maintenance': forms.Select(attrs={'class': 'form-control'}),
            'detail': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'fournisseur': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'km_vehicule': forms.NumberInput(attrs={'class': 'form-control'}),
            'montant': forms.NumberInput(attrs={'class': 'form-control'}),
            'periodicite_km': forms.NumberInput(attrs={'class': 'form-control'}),
            'alerte_km': forms.NumberInput(attrs={'class': 'form-control'}),
            'periodicite_mois': forms.NumberInput(attrs={'class': 'form-control'}),
            'alerte_mois': forms.NumberInput(attrs={'class': 'form-control'}),
            'facture': forms.FileInput(attrs={'class': 'form-control'}),
        }


class PlanificationForm(forms.ModelForm):
    """
    Formulaire pour la création et la modification des planifications de maintenance.
    """
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(PlanificationForm, self).__init__(*args, **kwargs)
        
        # Filtrer les services pour n'afficher que ceux de l'utilisateur connecté
        if user:
            self.fields['service'].queryset = user.service.all()
            
            # Filtrer les véhicules en fonction des services de l'utilisateur
            services_ids = user.service.values_list('id_service', flat=True)
            self.fields['vehicule'].queryset = Vehicule.objects.filter(service__id_service__in=services_ids)
            
            # Filtrer les utilisateurs pour n'afficher que ceux du groupe "Driver Principal" et des services de l'utilisateur
            self.fields['utilisateur'].queryset = Utilisateur.objects.filter(
                groupe__nom_groupe='Driver Principal',
                service__id_service__in=services_ids
            ).distinct()
    
    class Meta:
        model = Planification
        fields = ['service', 'utilisateur', 'vehicule', 'type_maintenance', 
                 'prochaine_echeance_km', 'prochaine_echeance_date', 'alerte_km', 'alerte_mois']
        widgets = {
            'service': forms.Select(attrs={'class': 'form-control'}),
            'utilisateur': forms.Select(attrs={'class': 'form-control'}),
            'vehicule': forms.Select(attrs={'class': 'form-control'}),
            'type_maintenance': forms.Select(attrs={'class': 'form-control'}),
            'prochaine_echeance_km': forms.NumberInput(attrs={'class': 'form-control'}),
            'prochaine_echeance_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'alerte_km': forms.NumberInput(attrs={'class': 'form-control'}),
            'alerte_mois': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class PlanificationCourseForm(forms.ModelForm):
    """
    Formulaire pour la création et la modification des planifications de course.
    """
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Si création manuelle (pas de demande fournie), masquer le champ demande et statut.
        if not self.instance.demande_id:
            self.fields['demande'].widget = forms.HiddenInput()
            self.fields['statut'].widget = forms.HiddenInput()
            self.initial['statut'] = 'planifiée'
        # Filtrer les utilisateurs pour n'afficher que ceux des groupes "Driver" ou "Driver Principal"
        self.fields['utilisateur'].queryset = Utilisateur.objects.filter(groupe__nom_groupe__startswith='Driver').distinct().order_by('nom_complet')

        if user and not user.is_superuser:
            user_services = user.service.all()
            self.fields['vehicule'].queryset = Vehicule.objects.filter(service__in=user_services).order_by('immatriculation')
            self.fields['utilisateur'].queryset = self.fields['utilisateur'].queryset.filter(service__in=user_services).distinct()

    class Meta:
        model = PlanificationCourse
        fields = ['demande', 'date_heure', 'utilisateur', 'vehicule', 'statut', 'lieu_arrivee']
        widgets = {
            'date_heure': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'lieu_arrivee': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ExecutionCourseForm(forms.ModelForm):
    """
    Formulaire pour la saisie de l'exécution de course.
    """
    class Meta:
        model = ExecutionCourse
        fields = [
            'date_heure_debut',
            'date_heure_fin',
            'kilometrage_debut',
            'kilometrage_fin',
            'remarques_chauffeur',
        ]
        widgets = {
            'date_heure_debut': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'date_heure_fin': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'kilometrage_debut': forms.NumberInput(attrs={'class': 'form-control'}),
            'kilometrage_fin': forms.NumberInput(attrs={'class': 'form-control'}),
            'remarques_chauffeur': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.planification = kwargs.pop('planification', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        date_heure_debut = cleaned_data.get('date_heure_debut')
        date_heure_fin = cleaned_data.get('date_heure_fin')
        kilometrage_debut = cleaned_data.get('kilometrage_debut')
        kilometrage_fin = cleaned_data.get('kilometrage_fin')

        if date_heure_debut and date_heure_fin and date_heure_fin <= date_heure_debut:
            self.add_error('date_heure_fin', "La date/heure de fin doit être postérieure à la date/heure de début.")

        if kilometrage_debut is not None and kilometrage_fin is not None and kilometrage_fin < kilometrage_debut:
            self.add_error('kilometrage_fin', "Le kilométrage de fin ne peut pas être inférieur au kilométrage de début.")

        if self.planification and self.planification.vehicule and kilometrage_debut is not None:
            kilometrage_actuel = self.planification.vehicule.kilometrage
            if kilometrage_debut < kilometrage_actuel:
                self.add_error(
                    'kilometrage_debut',
                    f"Le kilométrage de début ({kilometrage_debut}) ne peut pas être inférieur au kilométrage actuel du véhicule ({kilometrage_actuel})."
                )

        return cleaned_data
