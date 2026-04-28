from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings

# Create your models here.

class Service(models.Model):
    """
    Modèle représentant un service dans l'organisation.
    """
    id_service = models.AutoField(primary_key=True)
    nom_service = models.CharField(max_length=100, verbose_name="Nom du service")
    description = models.TextField(verbose_name="Description", blank=True, null=True)
    
    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Services"
        
    def __str__(self):
        return self.nom_service


class Groupe(models.Model):
    """
    Modèle représentant un groupe d'utilisateurs.
    """
    id_groupe = models.AutoField(primary_key=True)
    nom_groupe = models.CharField(max_length=100, verbose_name="Nom du groupe")
    description = models.TextField(verbose_name="Description", blank=True, null=True)
    
    class Meta:
        verbose_name = "Groupe"
        verbose_name_plural = "Groupes"
        
    def __str__(self):
        return self.nom_groupe


class UtilisateurManager(BaseUserManager):
    """
    Manager personnalisé pour le modèle Utilisateur.
    """
    def create_user(self, email, nom_complet, password=None, **extra_fields):
        if not email:
            raise ValueError('L\'adresse email est obligatoire')
        email = self.normalize_email(email)
        user = self.model(email=email, nom_complet=nom_complet, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, nom_complet, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('statut', 'Actif')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Le superutilisateur doit avoir is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Le superutilisateur doit avoir is_superuser=True.')
        
        return self.create_user(email, nom_complet, password, **extra_fields)


class Utilisateur(AbstractBaseUser, PermissionsMixin):
    """
    Modèle personnalisé pour les utilisateurs du système FMS.
    """
    STATUT_CHOICES = (
        ('Actif', 'Actif'),
        ('Inactif', 'Inactif'),
    )
    
    id_utilisateur = models.AutoField(primary_key=True)
    nom_complet = models.CharField(max_length=200, verbose_name="Nom complet")
    email = models.EmailField(unique=True, verbose_name="Adresse email")
    fonction = models.CharField(max_length=100, verbose_name="Fonction", blank=True, null=True)
    groupe = models.ManyToManyField(Groupe, verbose_name="Groupes", related_name="utilisateurs")
    service = models.ManyToManyField(Service, verbose_name="Services", related_name="utilisateurs")
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default='Actif', verbose_name="Statut")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    
    objects = UtilisateurManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nom_complet']
    
    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        
    def __str__(self):
        return self.nom_complet
    
    def get_full_name(self):
        return self.nom_complet
    
    def get_short_name(self):
        # Retourne le premier mot du nom complet comme nom court
        return self.nom_complet.split()[0] if self.nom_complet else ""


class Vehicule(models.Model):
    """
    Modèle représentant un véhicule de la flotte.
    """
    TYPE_CARBURANT_CHOICES = (
        ('Essence', 'Essence'),
        ('Gasoil', 'Gasoil'),
    )
    
    STATUT_CHOICES = (
        ('Disponible', 'Disponible'),
        ('En service', 'En service'),
        ('En maintenance', 'En maintenance'),
        ('Non Disponible', 'Non Disponible'),
        ('Réformé', 'Réformé'),
    )
    
    id_vehicule = models.AutoField(primary_key=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='vehicules', verbose_name="Service")
    marque = models.CharField(max_length=100, verbose_name="Marque")
    modele = models.CharField(max_length=100, verbose_name="Modèle")
    chassis = models.CharField(max_length=100, unique=True, verbose_name="Numéro de châssis")
    immatriculation = models.CharField(max_length=50, unique=True, verbose_name="Immatriculation")
    type_carburant = models.CharField(max_length=10, choices=TYPE_CARBURANT_CHOICES, verbose_name="Type de carburant")
    date_mise_en_service = models.DateField(verbose_name="Date de mise en service")
    kilometrage = models.PositiveIntegerField(verbose_name="Kilométrage")
    statut = models.CharField(max_length=15, choices=STATUT_CHOICES, default='Disponible', verbose_name="Statut")
    document = models.FileField(upload_to='vehicules/documents/', blank=True, null=True, verbose_name="Document")
    photo = models.ImageField(upload_to='vehicules/photos/', blank=True, null=True, verbose_name="Photo")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    
    class Meta:
        verbose_name = "Véhicule"
        verbose_name_plural = "Véhicules"
        
    def __str__(self):
        return f"{self.marque} {self.modele} - {self.immatriculation}"

    def clean(self):
        super().clean()
        if self.date_mise_en_service and self.date_mise_en_service > timezone.now().date():
            raise ValidationError({
                'date_mise_en_service': "La date de mise en service ne peut pas être dans le futur."
            })

    @property
    def documents_actifs(self):
        return self.documents.filter(est_actif=True)

    @property
    def affectation_active(self):
        return self.affectations.filter(date_fin__isnull=True).order_by('-date_debut').first()

    def est_disponible(self):
        return self.statut == 'Disponible'


class VehiculeAffectation(models.Model):
    """
    Historique des affectations de véhicules (service/chauffeur principal).
    Une seule affectation active est autorisée par véhicule.
    """
    id_affectation = models.AutoField(primary_key=True)
    vehicule = models.ForeignKey(Vehicule, on_delete=models.CASCADE, related_name='affectations')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='affectations_vehicules')
    chauffeur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='affectations_vehicules',
        verbose_name="Chauffeur principal"
    )
    date_debut = models.DateField(default=timezone.now)
    date_fin = models.DateField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    est_active = models.BooleanField(default=True)
    cree_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='affectations_creees'
    )
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Affectation véhicule"
        verbose_name_plural = "Affectations véhicules"
        ordering = ['-date_debut', '-date_creation']

    def __str__(self):
        return f"{self.vehicule} -> {self.service} ({self.date_debut} - {self.date_fin or 'en cours'})"

    def clean(self):
        super().clean()
        if self.date_fin and self.date_fin < self.date_debut:
            raise ValidationError({
                'date_fin': "La date de fin ne peut pas être antérieure à la date de début."
            })

        if self.est_active and self.date_fin:
            raise ValidationError({
                'est_active': "Une affectation avec date de fin renseignée ne peut pas rester active."
            })

        if self.est_active:
            active_qs = VehiculeAffectation.objects.filter(vehicule=self.vehicule, est_active=True)
            if self.pk:
                active_qs = active_qs.exclude(pk=self.pk)
            if active_qs.exists():
                raise ValidationError("Ce véhicule possède déjà une affectation active.")

    def save(self, *args, **kwargs):
        self.est_active = self.date_fin is None
        super().save(*args, **kwargs)


class VehiculeDocument(models.Model):
    """
    Documents de conformité d'un véhicule (assurance, visite technique, etc.).
    """
    TYPE_CHOICES = (
        ('assurance', 'Assurance'),
        ('visite_technique', 'Visite technique'),
        ('carte_grise', 'Carte grise'),
        ('autre', 'Autre'),
    )

    id_document_vehicule = models.AutoField(primary_key=True)
    vehicule = models.ForeignKey(Vehicule, on_delete=models.CASCADE, related_name='documents')
    type_document = models.CharField(max_length=30, choices=TYPE_CHOICES)
    reference = models.CharField(max_length=100, blank=True, null=True)
    date_emission = models.DateField(blank=True, null=True)
    date_expiration = models.DateField(blank=True, null=True)
    fichier = models.FileField(upload_to='vehicules/conformite/', blank=True, null=True)
    commentaire = models.TextField(blank=True, null=True)
    est_actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Document véhicule"
        verbose_name_plural = "Documents véhicules"
        ordering = ['date_expiration', '-date_creation']

    def __str__(self):
        return f"{self.vehicule} - {self.get_type_document_display()}"

    def clean(self):
        super().clean()
        if self.date_emission and self.date_expiration and self.date_expiration < self.date_emission:
            raise ValidationError({
                'date_expiration': "La date d'expiration ne peut pas être antérieure à la date d'émission."
            })

    def est_expire(self):
        return bool(self.date_expiration and self.date_expiration < timezone.now().date())

    def expire_bientot(self, jours=30):
        if not self.date_expiration:
            return False
        delta = (self.date_expiration - timezone.now().date()).days
        return 0 <= delta <= jours


class Carte_Carburant(models.Model):
    """
    Modèle représentant une carte de carburant.
    """
    TYPE_CARBURANT_CHOICES = (
        ('Essence', 'Essence'),
        ('Gasoil', 'Gasoil'),
    )
    
    STATUT_CHOICES = (
        ('Disponible', 'Disponible'),
        ('Attribué', 'Attribué'),
        ('Non disponible', 'Non disponible'),
        ('Bloquée', 'Bloquée'),
    )
    
    id_carte_carburant = models.AutoField(primary_key=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='cartes_carburant', verbose_name="Service")
    numero_carte = models.CharField(max_length=50, unique=True, verbose_name="Numéro de carte")
    solde = models.PositiveIntegerField(default=0, verbose_name="Solde (FCFA)")
    vehicule = models.ForeignKey(Vehicule, on_delete=models.SET_NULL, related_name='cartes_carburant', null=True, blank=True, verbose_name="Véhicule")
    statut = models.CharField(max_length=15, choices=STATUT_CHOICES, default='Disponible', verbose_name="Statut")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    dotation_active_ht = models.ForeignKey('Achat_Stock_Carburant_HT', on_delete=models.SET_NULL, related_name='cartes_actives', null=True, blank=True, verbose_name="Dotation HT active")
    dotation_active_ttc = models.ForeignKey('Achat_Carburant_TTC', on_delete=models.SET_NULL, related_name='cartes_actives', null=True, blank=True, verbose_name="Dotation TTC active")
    
    class Meta:
        verbose_name = "Carte carburant"
        verbose_name_plural = "Cartes carburant"
        constraints = [
            models.CheckConstraint(
                check=models.Q(dotation_active_ht__isnull=True) | models.Q(dotation_active_ttc__isnull=True),
                name='one_dotation_active_at_a_time'
            )
        ]
        
    def __str__(self):
        return f"Carte {self.numero_carte} - {self.service.nom_service}"
    
    def format_solde(self):
        """Formater le solde avec séparateur de milliers"""
        return f"{self.solde:,} FCFA".replace(',', ' ')
    
    def get_absolute_url(self):
        """Retourne l'URL de la page de détail de la carte carburant"""
        from django.urls import reverse
        return reverse('carte_carburant_detail', args=[str(self.id_carte_carburant)])
    
    def get_update_url(self):
        """Retourne l'URL de la page de modification de la carte carburant"""
        from django.urls import reverse
        return reverse('carte_carburant_update', args=[str(self.id_carte_carburant)])
    
    def get_delete_url(self):
        """Retourne l'URL de la page de suppression de la carte carburant"""
        from django.urls import reverse
        return reverse('carte_carburant_delete', args=[str(self.id_carte_carburant)])
    
    def get_rechargement_actif(self):
        """Retourne le rechargement associé à la dotation active"""
        if self.dotation_active_ht:
            return self.rechargements_ht.filter(achat_stock_carburant_ht=self.dotation_active_ht).first()
        elif self.dotation_active_ttc:
            return self.rechargements_ttc.filter(achat_carburant_ttc=self.dotation_active_ttc).first()
        return None
    
    def get_solde_actif(self):
        """Retourne le solde du rechargement actif ou le solde total si aucun rechargement actif"""
        rechargement = self.get_rechargement_actif()
        if rechargement:
            # Utiliser solde_restant au lieu de montant_ttc pour refléter le solde réel disponible
            if rechargement.solde_restant is not None:
                return rechargement.solde_restant
            return rechargement.montant_ttc
        return self.solde

    def recalculer_solde(self, save=True):
        """Recalcule le solde carte à partir des soldes restants de tous les rechargements."""
        total_ht = self.rechargements_ht.aggregate(total=models.Sum('solde_restant'))['total'] or 0
        total_ttc = self.rechargements_ttc.aggregate(total=models.Sum('solde_restant'))['total'] or 0
        self.solde = max(0, int(total_ht + total_ttc))

        # Si la carte est épuisée, détacher les dotations actives
        if self.solde == 0:
            self.dotation_active_ht = None
            self.dotation_active_ttc = None

        if save:
            self.save(update_fields=['solde', 'dotation_active_ht', 'dotation_active_ttc'])
        return self.solde
    
    def get_solde_actif_formate(self):
        """Retourne le solde du rechargement actif formaté ou le solde total formaté si aucun rechargement actif"""
        rechargement = self.get_rechargement_actif()
        if rechargement:
            # Utiliser solde_restant au lieu de montant_ttc pour refléter le solde réel disponible
            if rechargement.solde_restant is not None:
                return rechargement.format_montant(rechargement.solde_restant)
            return rechargement.format_montant_ttc()
        return self.format_solde()
    
    def save(self, *args, **kwargs):
        """Surcharge de la méthode save pour mettre à jour le statut des dotations"""
        # Vérifier si c'est une modification (pas une création)
        is_update = self.pk is not None
        
        # Définir le statut par défaut en fonction du solde (sauf carte explicitement bloquée)
        if self.statut != 'Bloquée':
            if self.solde == 0:
                self.statut = 'Non disponible'
            elif self.solde > 0 and self.statut == 'Non disponible':
                self.statut = 'Disponible'
        
        # Si c'est une mise à jour et que le solde est 0, réinitialiser les dotations actives
        if is_update and self.solde == 0:
            # Sauvegarder les références aux dotations avant de les réinitialiser
            dotation_ht = self.dotation_active_ht
            dotation_ttc = self.dotation_active_ttc
            
            # Réinitialiser les dotations actives
            self.dotation_active_ht = None
            self.dotation_active_ttc = None
        
        super().save(*args, **kwargs)


class Fournisseur(models.Model):
    """
    Modèle représentant un fournisseur.
    """
    TYPE_FOURNISSEUR_CHOICES = (
        ('Carburant', 'Carburant'),
        ('Maintenance', 'Maintenance'),
        ('Assurance', 'Assurance'),
    )
    
    id_fournisseur = models.AutoField(primary_key=True)
    nom_fournisseur = models.CharField(max_length=100, verbose_name="Nom du fournisseur")
    type_fournisseur = models.CharField(max_length=20, choices=TYPE_FOURNISSEUR_CHOICES, verbose_name="Type de fournisseur")
    adresse = models.TextField(verbose_name="Adresse", blank=True, null=True)
    email = models.EmailField(verbose_name="Email", blank=True, null=True)
    telephone = models.CharField(max_length=20, verbose_name="Téléphone", blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    
    class Meta:
        verbose_name = "Fournisseur"
        verbose_name_plural = "Fournisseurs"
        
    def __str__(self):
        return f"{self.nom_fournisseur} ({self.type_fournisseur})"


class Achat_Stock_Carburant_HT(models.Model):
    """
    Modèle représentant un achat de stock de carburant HT.
    """
    TYPE_CARBURANT_CHOICES = (
        ('Essence', 'Essence'),
        ('Gasoil', 'Gasoil'),
    )
    
    STATUS_CHOICES = (
        ('Ouverte', 'Ouverte'),
        ('Close', 'Close'),
    )
    
    id_achat_stock_carburant_ht = models.AutoField(primary_key=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='achats_stock_carburant_ht', verbose_name="Service")
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.CASCADE, related_name='achats_stock_carburant_ht', verbose_name="Fournisseur")
    voucher = models.CharField(max_length=100, verbose_name="Numéro de voucher")
    business_unit = models.CharField(max_length=100, verbose_name="Business Unit")
    dept_id = models.CharField(max_length=100, verbose_name="Département ID")
    project_id = models.CharField(max_length=100, verbose_name="Projet ID")
    date_achat = models.DateField(verbose_name="Date d'achat")
    libelle = models.CharField(max_length=255, verbose_name="Libellé")
    type_carburant = models.CharField(max_length=10, choices=TYPE_CARBURANT_CHOICES, verbose_name="Type de carburant")
    volume = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Volume (litres)")
    montant_ht = models.PositiveIntegerField(verbose_name="Montant HT (FCFA)")
    montant_ttc = models.PositiveIntegerField(verbose_name="Montant TTC (FCFA)")
    document = models.FileField(upload_to='achats/documents/', blank=True, null=True, verbose_name="Document")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    statut = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Ouverte', verbose_name="Statut")
    
    class Meta:
        verbose_name = "Achat stock carburant HT"
        verbose_name_plural = "Achats stock carburant HT"
        
    def __str__(self):
        return f"{self.libelle}"
    
    @staticmethod
    def format_montant(montant):
        """Formater un montant avec séparateur de milliers"""
        if montant is None:
            return "0 FCFA"
        return f"{int(montant):,} FCFA".replace(',', ' ')
    
    def tx_taxe(self):
        """Calculer le taux de taxe"""
        if self.montant_ht > 0:
            return self.montant_ttc / self.montant_ht
        return 0
    
    def format_montant_ht(self):
        """Formater le montant HT avec séparateur de milliers"""
        return self.format_montant(self.montant_ht)
    
    def format_montant_ttc(self):
        """Formater le montant TTC avec séparateur de milliers"""
        return self.format_montant(self.montant_ttc)

    def clean(self):
        super().clean()
        if self.montant_ttc <= 0:
            raise ValidationError({'montant_ttc': "Le montant TTC doit être supérieur à zéro."})
        if self.montant_ht <= 0:
            raise ValidationError({'montant_ht': "Le montant HT doit être supérieur à zéro."})
        if self.volume <= 0:
            raise ValidationError({'volume': "Le volume doit être supérieur à zéro."})
        if self.montant_ttc < self.montant_ht:
            raise ValidationError({'montant_ttc': "Le montant TTC ne peut pas être inférieur au montant HT."})
    
    @property
    def solde_theorique(self):
        """Calculer le solde théorique restant de la dotation."""
        from django.db.models import Sum
        montant_recharge = self.rechargements_ht.aggregate(total=Sum('montant_ttc'))['total'] or 0
        return max(0, self.montant_ttc - montant_recharge)
    
    def format_solde_theorique(self):
        """Formater le solde théorique avec séparateur de milliers"""
        return self.format_montant(self.solde_theorique)
    
    def get_absolute_url(self):
        """Retourne l'URL de la page de détail de l'achat carburant HT"""
        from django.urls import reverse
        return reverse('achat_carburant_ht_detail', args=[str(self.id_achat_stock_carburant_ht)])
    
    def get_update_url(self):
        """Retourne l'URL de la page de modification de l'achat carburant HT"""
        from django.urls import reverse
        return reverse('achat_carburant_ht_update', args=[str(self.id_achat_stock_carburant_ht)])
    
    def get_delete_url(self):
        """Retourne l'URL de la page de suppression de l'achat carburant HT"""
        from django.urls import reverse
        return reverse('achat_carburant_ht_delete', args=[str(self.id_achat_stock_carburant_ht)])
    
    def save(self, *args, **kwargs):
        """Surcharge de la méthode save pour mettre à jour le statut en fonction du solde théorique"""
        if self.pk is None:
            self.statut = 'Ouverte'
        elif self.solde_theorique <= 0:
            self.statut = 'Close'
        else:
            self.statut = 'Ouverte'
        
        super().save(*args, **kwargs)


class Achat_Carburant_TTC(models.Model):
    """
    Modèle représentant un achat de carburant TTC.
    """
    TYPE_CARBURANT_CHOICES = (
        ('Essence', 'Essence'),
        ('Gasoil', 'Gasoil'),
    )
    
    STATUS_CHOICES = (
        ('Ouverte', 'Ouverte'),
        ('Close', 'Close'),
    )
    
    id_achat_carburant_ttc = models.AutoField(primary_key=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='achats_carburant_ttc', verbose_name="Service")
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.CASCADE, related_name='achats_carburant_ttc', verbose_name="Fournisseur")
    voucher = models.CharField(max_length=100, verbose_name="Numéro de voucher")
    business_unit = models.CharField(max_length=100, verbose_name="Business Unit")
    dept_id = models.CharField(max_length=100, verbose_name="Département ID")
    project_id = models.CharField(max_length=100, verbose_name="Projet ID")
    date_achat = models.DateField(verbose_name="Date d'achat")
    libelle = models.CharField(max_length=255, verbose_name="Libellé")
    type_carburant = models.CharField(max_length=10, choices=TYPE_CARBURANT_CHOICES, verbose_name="Type de carburant")
    volume = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Volume (litres)")
    montant_ttc = models.PositiveIntegerField(verbose_name="Montant TTC (FCFA)")
    document = models.FileField(upload_to='achats/documents/', blank=True, null=True, verbose_name="Document")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    statut = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Ouverte', verbose_name="Statut")
    
    class Meta:
        verbose_name = "Achat carburant TTC"
        verbose_name_plural = "Achats carburant TTC"
        
    def __str__(self):
        return f"Achat TTC {self.voucher} - {self.date_achat}"
    
    @staticmethod
    def format_montant(montant):
        """Formater un montant avec séparateur de milliers"""
        if montant is None:
            return "0 FCFA"
        return f"{int(montant):,} FCFA".replace(',', ' ')
    
    def format_montant_ttc(self):
        """Formater le montant TTC avec séparateur de milliers"""
        return self.format_montant(self.montant_ttc)
    
    @property
    def solde_theorique(self):
        """Calculer le solde théorique restant de la dotation."""
        from django.db.models import Sum
        montant_recharge = self.rechargements_ttc.aggregate(total=Sum('montant_ttc'))['total'] or 0
        return max(0, self.montant_ttc - montant_recharge)
    
    def format_solde_theorique(self):
        """Formater le solde théorique avec séparateur de milliers"""
        return self.format_montant(self.solde_theorique)
    
    def get_absolute_url(self):
        """Retourne l'URL de la page de détail de l'achat carburant TTC"""
        from django.urls import reverse
        return reverse('achat_carburant_ttc_detail', args=[str(self.id_achat_carburant_ttc)])
    
    def get_update_url(self):
        """Retourne l'URL de la page de modification de l'achat carburant TTC"""
        from django.urls import reverse
        return reverse('achat_carburant_ttc_update', args=[str(self.id_achat_carburant_ttc)])
    
    def get_delete_url(self):
        """Retourne l'URL de la page de suppression de l'achat carburant TTC"""
        from django.urls import reverse
        return reverse('achat_carburant_ttc_delete', args=[str(self.id_achat_carburant_ttc)])
    
    def save(self, *args, **kwargs):
        """Surcharge de la méthode save pour mettre à jour le statut en fonction du solde théorique"""
        if self.pk is None:
            self.statut = 'Ouverte'
        elif self.solde_theorique <= 0:
            self.statut = 'Close'
        else:
            self.statut = 'Ouverte'
        
        super().save(*args, **kwargs)


class Rechargement_Carte_Carburant_HT(models.Model):
    """
    Modèle représentant un rechargement de carte de carburant à partir d'un achat stock carburant HT.
    """
    id_rechargement_ht = models.AutoField(primary_key=True)
    achat_stock_carburant_ht = models.ForeignKey(Achat_Stock_Carburant_HT, on_delete=models.CASCADE, related_name='rechargements_ht', verbose_name="Achat stock carburant HT")
    carte_carburant = models.ForeignKey(Carte_Carburant, on_delete=models.CASCADE, related_name='rechargements_ht', verbose_name="Carte carburant")
    date_rechargement = models.DateField(verbose_name="Date de rechargement")
    volume = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Volume (litres)")
    prix_unitaire_ttc = models.PositiveIntegerField(verbose_name="Prix unitaire TTC (FCFA)")
    montant_ttc = models.PositiveIntegerField(verbose_name="Montant TTC (FCFA)")
    solde_restant = models.PositiveIntegerField(null=True, blank=True, verbose_name="Solde restant")
    volume_restant = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Volume restant (litres)")
    
    class Meta:
        verbose_name = "Rechargement de carte carburant HT"
        verbose_name_plural = "Rechargements de cartes carburant HT"
        constraints = [
            models.UniqueConstraint(
                fields=['achat_stock_carburant_ht', 'carte_carburant'],
                name='unique_ht_carte_rechargement'
            ),
        ]
        
    def __str__(self):
        return f"Rechargement HT de {self.volume} L pour la carte {self.carte_carburant.numero_carte} le {self.date_rechargement}"
    
    @staticmethod
    def format_montant(montant):
        """Formater un montant avec séparateur de milliers"""
        if montant is None:
            return "0 FCFA"
        return f"{int(montant):,} FCFA".replace(',', ' ')
    
    def format_montant_ttc(self):
        """Formater le montant TTC avec séparateur de milliers"""
        return self.format_montant(self.montant_ttc)

    def clean(self):
        super().clean()
        if self.montant_ttc <= 0:
            raise ValidationError({'montant_ttc': "Le montant TTC doit être supérieur à zéro."})
        if self.volume <= 0:
            raise ValidationError({'volume': "Le volume doit être supérieur à zéro."})

        if self.carte_carburant and self.achat_stock_carburant_ht and self.carte_carburant.service_id != self.achat_stock_carburant_ht.service_id:
            raise ValidationError("La carte et la dotation HT doivent appartenir au même service.")

        deja_recharge = Rechargement_Carte_Carburant_HT.objects.filter(
            achat_stock_carburant_ht=self.achat_stock_carburant_ht,
            carte_carburant=self.carte_carburant,
        )
        if self.pk:
            deja_recharge = deja_recharge.exclude(pk=self.pk)
        if deja_recharge.exists():
            raise ValidationError("Cette carte a déjà été rechargée avec cette dotation HT.")

        if self.carte_carburant and self.carte_carburant.dotation_active_ttc:
            raise ValidationError("Cette carte est liée à une dotation TTC active.")

        recharge_existant = Rechargement_Carte_Carburant_HT.objects.filter(
            achat_stock_carburant_ht=self.achat_stock_carburant_ht,
        )
        if self.pk:
            recharge_existant = recharge_existant.exclude(pk=self.pk)
        montant_deja_recharge = recharge_existant.aggregate(total=models.Sum('montant_ttc'))['total'] or 0
        if montant_deja_recharge + self.montant_ttc > self.achat_stock_carburant_ht.montant_ttc:
            raise ValidationError("Le montant rechargé dépasse le montant disponible de la dotation HT.")
        
    def save(self, *args, **kwargs):
        """
        Surcharge de la méthode save pour initialiser le volume_restant et mettre à jour la carte
        et le solde de la carte lors d'un rechargement.
        """
        self.full_clean()

        # Vérifier si c'est un nouveau rechargement (pas d'ID)
        is_new = self.pk is None
        previous = None if is_new else Rechargement_Carte_Carburant_HT.objects.get(pk=self.pk)
        
        # Si c'est un nouveau rechargement, initialiser le volume_restant
        if is_new and self.volume_restant is None:
            self.volume_restant = self.volume
            
        # Si le solde_restant est None, l'initialiser
        if self.solde_restant is None:
            self.solde_restant = self.montant_ttc
        
        # Sauvegarder d'abord le rechargement
        super().save(*args, **kwargs)
        
        if previous and previous.carte_carburant_id != self.carte_carburant_id:
            previous.carte_carburant.recalculer_solde()

        carte = self.carte_carburant
        carte.dotation_active_ht = self.achat_stock_carburant_ht
        carte.dotation_active_ttc = None
        carte.recalculer_solde()

        # Mettre à jour le statut de la dotation en fonction du restant
        self.achat_stock_carburant_ht.save()

    def delete(self, *args, **kwargs):
        carte = self.carte_carburant
        achat = self.achat_stock_carburant_ht
        super().delete(*args, **kwargs)
        if carte:
            carte.recalculer_solde()
        if achat:
            achat.save()


class Rechargement_Carte_Carburant_TTC(models.Model):
    """
    Modèle représentant un rechargement de carte de carburant à partir d'un achat carburant TTC.
    """
    id_rechargement_ttc = models.AutoField(primary_key=True)
    achat_carburant_ttc = models.ForeignKey(Achat_Carburant_TTC, on_delete=models.CASCADE, related_name='rechargements_ttc', verbose_name="Achat carburant TTC")
    carte_carburant = models.ForeignKey(Carte_Carburant, on_delete=models.CASCADE, related_name='rechargements_ttc', verbose_name="Carte carburant")
    date_rechargement = models.DateField(verbose_name="Date de rechargement")
    volume = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Volume (litres)")
    prix_unitaire_ttc = models.PositiveIntegerField(verbose_name="Prix unitaire TTC (FCFA)")
    montant_ttc = models.PositiveIntegerField(verbose_name="Montant TTC (FCFA)")
    solde_restant = models.PositiveIntegerField(null=True, blank=True, verbose_name="Solde restant")
    volume_restant = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Volume restant (litres)")
    
    class Meta:
        verbose_name = "Rechargement de carte carburant TTC"
        verbose_name_plural = "Rechargements de cartes carburant TTC"
        constraints = [
            models.UniqueConstraint(
                fields=['achat_carburant_ttc', 'carte_carburant'],
                name='unique_ttc_carte_rechargement'
            ),
        ]
        
    def __str__(self):
        return f"Rechargement TTC de {self.volume} L pour la carte {self.carte_carburant.numero_carte} le {self.date_rechargement}"
    
    @staticmethod
    def format_montant(montant):
        """Formater un montant avec séparateur de milliers"""
        if montant is None:
            return "0 FCFA"
        return f"{int(montant):,} FCFA".replace(',', ' ')
    
    def format_montant_ttc(self):
        """Formater le montant TTC avec séparateur de milliers"""
        return self.format_montant(self.montant_ttc)

    def clean(self):
        super().clean()
        if self.montant_ttc <= 0:
            raise ValidationError({'montant_ttc': "Le montant TTC doit être supérieur à zéro."})
        if self.volume <= 0:
            raise ValidationError({'volume': "Le volume doit être supérieur à zéro."})

        if self.carte_carburant and self.achat_carburant_ttc and self.carte_carburant.service_id != self.achat_carburant_ttc.service_id:
            raise ValidationError("La carte et la dotation TTC doivent appartenir au même service.")

        deja_recharge = Rechargement_Carte_Carburant_TTC.objects.filter(
            achat_carburant_ttc=self.achat_carburant_ttc,
            carte_carburant=self.carte_carburant,
        )
        if self.pk:
            deja_recharge = deja_recharge.exclude(pk=self.pk)
        if deja_recharge.exists():
            raise ValidationError("Cette carte a déjà été rechargée avec cette dotation TTC.")

        if self.carte_carburant and self.carte_carburant.dotation_active_ht:
            raise ValidationError("Cette carte est liée à une dotation HT active.")

        recharge_existant = Rechargement_Carte_Carburant_TTC.objects.filter(
            achat_carburant_ttc=self.achat_carburant_ttc,
        )
        if self.pk:
            recharge_existant = recharge_existant.exclude(pk=self.pk)
        montant_deja_recharge = recharge_existant.aggregate(total=models.Sum('montant_ttc'))['total'] or 0
        if montant_deja_recharge + self.montant_ttc > self.achat_carburant_ttc.montant_ttc:
            raise ValidationError("Le montant rechargé dépasse le montant disponible de la dotation TTC.")
        
    def save(self, *args, **kwargs):
        """
        Surcharge de la méthode save pour initialiser le volume_restant et mettre à jour la carte
        et le solde de la carte lors d'un rechargement.
        """
        self.full_clean()

        # Vérifier si c'est un nouveau rechargement (pas d'ID)
        is_new = self.pk is None
        previous = None if is_new else Rechargement_Carte_Carburant_TTC.objects.get(pk=self.pk)
        
        # Si c'est un nouveau rechargement, initialiser le volume_restant
        if is_new and self.volume_restant is None:
            self.volume_restant = self.volume
            
        # Si le solde_restant est None, l'initialiser
        if self.solde_restant is None:
            self.solde_restant = self.montant_ttc
        
        # Sauvegarder d'abord le rechargement
        super().save(*args, **kwargs)
        
        if previous and previous.carte_carburant_id != self.carte_carburant_id:
            previous.carte_carburant.recalculer_solde()

        carte = self.carte_carburant
        carte.dotation_active_ttc = self.achat_carburant_ttc
        carte.dotation_active_ht = None
        carte.recalculer_solde()

        # Mettre à jour le statut de la dotation en fonction du restant
        self.achat_carburant_ttc.save()

    def delete(self, *args, **kwargs):
        carte = self.carte_carburant
        achat = self.achat_carburant_ttc
        super().delete(*args, **kwargs)
        if carte:
            carte.recalculer_solde()
        if achat:
            achat.save()


class Demande_Carte_Carburant(models.Model):
    """
    Modèle représentant une demande de carte carburant.
    Ce modèle évolue en 3 phases avec 2 acteurs différents:
    1. Le chauffeur (Driver) qui initie la demande
    2. Le gestionnaire de carburant qui traite la demande (accepte ou rejette)
    3. Finalisation du processus avec le ravitaillement et la clôture
    """
    # Choix pour le statut de la demande
    STATUT_CHOICES = (
        ('En attente', 'En attente'),
        ('Acceptée', 'Acceptée'),
        ('Rejetée', 'Rejetée'),
        ('Close', 'Clôturée'),  
    )
    
    # Phase 1: Initiation de la demande par le chauffeur (Driver)
    id_demande = models.AutoField(primary_key=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='demandes_carte_carburant', verbose_name="Service")
    utilisateur_demandeur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='demandes_initiees', verbose_name="Chauffeur demandeur")
    date_demande = models.DateTimeField(auto_now_add=True, verbose_name="Date de la demande")
    vehicule = models.ForeignKey(Vehicule, on_delete=models.CASCADE, related_name='demandes_carte_carburant', verbose_name="Véhicule")
    motif_demande = models.TextField(verbose_name="Motif de la demande")
    statut_demande = models.CharField(max_length=20, choices=STATUT_CHOICES, default='En attente', verbose_name="Statut de la demande")
    
    # Phase 2: Traitement de la demande par le gestionnaire de carburant
    date_traitement = models.DateTimeField(null=True, blank=True, verbose_name="Date de traitement")
    utilisateur_traitant = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True, related_name='demandes_traitees', verbose_name="Gestionnaire traitant")
    commentaire = models.TextField(blank=True, null=True, verbose_name="Commentaire")
    
    # Relation avec les rechargements (HT ou TTC)
    rechargement_ht = models.ForeignKey(Rechargement_Carte_Carburant_HT, on_delete=models.SET_NULL, null=True, blank=True, related_name='demandes', verbose_name="Rechargement HT")
    rechargement_ttc = models.ForeignKey(Rechargement_Carte_Carburant_TTC, on_delete=models.SET_NULL, null=True, blank=True, related_name='demandes', verbose_name="Rechargement TTC")
    
    # Phase 3: Ravitaillement et clôture
    date_ravitaillement = models.DateField(null=True, blank=True, verbose_name="Date de ravitaillement")
    km_vehicule = models.PositiveIntegerField(null=True, blank=True, verbose_name="Kilométrage du véhicule")
    prix_unitaire_ttc = models.PositiveIntegerField(null=True, blank=True, verbose_name="Prix unitaire TTC (FCFA)")
    volume = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Volume (litres)")
    montant_ttc = models.PositiveIntegerField(null=True, blank=True, verbose_name="Montant TTC (FCFA)")
    ancien_solde_carte = models.PositiveIntegerField(null=True, blank=True, verbose_name="Ancien solde de la carte")
    nouveau_solde_carte = models.PositiveIntegerField(null=True, blank=True, verbose_name="Nouveau solde de la carte")
    document = models.FileField(upload_to='demandes/documents/', blank=True, null=True, verbose_name="Document justificatif")
    date_cloture = models.DateTimeField(null=True, blank=True, verbose_name="Date de clôture")
    fiche_ravitaillement = models.FileField(upload_to='fiches_ravitaillement/', blank=True, null=True, verbose_name="Fiche de ravitaillement")
    station_service = models.CharField(max_length=100, blank=True, null=True, verbose_name="Station service")
    
    class Meta:
        verbose_name = "Demande de carte carburant"
        verbose_name_plural = "Demandes de cartes carburant"
        ordering = ['-date_demande']
        
    def __str__(self):
        return f"Demande #{self.id_demande} - {self.utilisateur_demandeur.nom_complet} - {self.date_demande.strftime('%d/%m/%Y')}"
    
    @property
    def dotation(self):
        """Retourne le libellé de la dotation associée (achat HT ou TTC)"""
        if self.rechargement_ht:
            return self.rechargement_ht.achat_stock_carburant_ht.libelle
        elif self.rechargement_ttc:
            return self.rechargement_ttc.achat_carburant_ttc.libelle
        return None
    
    @property
    def format_montant_ttc(self):
        """Formater le montant TTC avec séparateur de milliers"""
        if self.montant_ttc:
            return f"{self.montant_ttc:,} FCFA".replace(",", " ")
        return "Non défini"
    
    @property
    def get_carte_carburant(self):
        """Retourne la carte carburant associée à cette demande via le rechargement"""
        if self.rechargement_ht:
            return self.rechargement_ht.carte_carburant
        elif self.rechargement_ttc:
            return self.rechargement_ttc.carte_carburant
        return None
    
    @property
    def get_dotation_libelle(self):
        """Retourne le libellé de la dotation associée à cette demande"""
        if self.rechargement_ht and self.rechargement_ht.achat_stock_carburant_ht:
            return self.rechargement_ht.achat_stock_carburant_ht.libelle
        elif self.rechargement_ttc and self.rechargement_ttc.achat_carburant_ttc:
            return self.rechargement_ttc.achat_carburant_ttc.libelle
        return "Non défini"
    
    @property
    def get_solde_initial(self):
        """Retourne le solde initial de la carte avant le traitement de la demande"""
        carte = self.get_carte_carburant
        if carte:
            if self.rechargement_ht:
                return self.rechargement_ht.montant_ttc
            elif self.rechargement_ttc:
                return self.rechargement_ttc.montant_ttc
        return None
    
    @property
    def format_solde_initial(self):
        solde = self.get_solde_initial
        if solde is not None:
            return f"{solde:,} FCFA".replace(",", " ")
        return "Non défini"
    
    @property
    def get_nouveau_solde(self):
        """Retourne le nouveau solde de la carte après le traitement de la demande"""
        carte = self.get_carte_carburant
        if carte and self.montant_ttc:
            if self.rechargement_ht or self.rechargement_ttc:
                solde_initial = self.get_solde_initial or 0
                return solde_initial - self.montant_ttc
        return None
    
    @property
    def format_nouveau_solde_carte(self):
        solde = self.get_nouveau_solde
        if solde is not None:
            return f"{solde:,} FCFA".replace(",", " ")
        return "Non défini"
    
    @property
    def get_fiche_ravitaillement_url(self):
        """Retourne l'URL pour télécharger la fiche de ravitaillement"""
        if self.fiche_ravitaillement:
            from django.urls import reverse
            return reverse('telecharger_fiche_ravitaillement', args=[self.id_demande])
        return None
    
    def save(self, *args, **kwargs):
        # Si le statut passe à "Acceptée", enregistrer la date de traitement
        if self.statut_demande == 'Acceptée' and not self.date_traitement:
            self.date_traitement = timezone.now()
        
        # Si le statut passe à "Rejetée", enregistrer la date de traitement et de clôture
        elif self.statut_demande == 'Rejetée' and not self.date_traitement:
            self.date_traitement = timezone.now()
            self.date_cloture = timezone.now()
        
        # Si le statut passe à "Close", enregistrer la date de clôture et mettre à jour les soldes
        elif self.statut_demande == 'Close' and not self.date_cloture:
            self.date_cloture = timezone.now()
            
            # Calculer le montant TTC si volume et prix unitaire sont renseignés
            if self.volume and self.prix_unitaire_ttc and not self.montant_ttc:
                self.montant_ttc = int(float(self.volume) * self.prix_unitaire_ttc)
        
        super().save(*args, **kwargs)
    
    def regenerer_fiche_ravitaillement(self):
        """
        Force la régénération de la fiche de ravitaillement
        """
        from django.template.loader import render_to_string
        from django.core.files.base import ContentFile
        from io import BytesIO
        from xhtml2pdf import pisa
        
        # Supprimer l'ancienne fiche si elle existe
        if self.fiche_ravitaillement:
            self.fiche_ravitaillement.delete(save=False)
            self.fiche_ravitaillement = None
        
        # Préparer le contexte avec toutes les informations nécessaires
        context = {
            'demande': self,
            'carte_carburant': self.get_carte_carburant,
            'service': self.service,
            'vehicule': self.vehicule,
        }
        
        # Générer le HTML
        fiche_html = render_to_string('core/demandes_carte_carburant/fiche_ravitaillement.html', context)
        
        # Créer un fichier PDF temporaire
        pdf_file = BytesIO()
        pisa.CreatePDF(fiche_html, dest=pdf_file)
        
        # Sauvegarder le PDF dans le champ fiche_ravitaillement
        pdf_file.seek(0)
        self.fiche_ravitaillement.save(
            f'fiche_ravitaillement_{self.id_demande}.pdf',
            ContentFile(pdf_file.read()),
            save=False
        )
        
        # Sauvegarder la demande
        self.save()
        
        return self.fiche_ravitaillement


class EmailLog(models.Model):
    """
    Modèle pour enregistrer les logs d'emails envoyés par le système.
    """
    id_email = models.AutoField(primary_key=True)
    sujet = models.CharField(max_length=255, verbose_name="Sujet de l'email")
    destinataire = models.CharField(max_length=255, verbose_name="Destinataire")
    contenu = models.TextField(verbose_name="Contenu de l'email")
    statut = models.CharField(max_length=20, verbose_name="Statut de l'envoi")
    date_envoi = models.DateTimeField(verbose_name="Date d'envoi")
    erreur = models.TextField(blank=True, null=True, verbose_name="Message d'erreur")
    
    class Meta:
        verbose_name = "Log d'email"
        verbose_name_plural = "Logs d'emails"
        
    def __str__(self):
        return f"{self.sujet} - {self.destinataire} - {self.date_envoi}"


class TypeMaintenance(models.Model):
    """
    Modèle représentant un type de maintenance pour les véhicules.
    """
    id = models.AutoField(primary_key=True)
    libelle = models.CharField(max_length=100, verbose_name="Libellé")
    
    class Meta:
        verbose_name = "Type de maintenance"
        verbose_name_plural = "Types de maintenance"
        
    def __str__(self):
        return self.libelle


class Maintenance(models.Model):
    """
    Modèle représentant une opération de maintenance effectuée sur un véhicule.
    """
    id = models.AutoField(primary_key=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='maintenances', verbose_name="Service")
    vehicule = models.ForeignKey(Vehicule, on_delete=models.CASCADE, related_name='maintenances', verbose_name="Véhicule")
    type_maintenance = models.ForeignKey(TypeMaintenance, on_delete=models.CASCADE, related_name='maintenances', verbose_name="Type de maintenance")
    detail = models.TextField(verbose_name="Détail de la maintenance")
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.CASCADE, related_name='maintenances', verbose_name="Fournisseur", 
                                   limit_choices_to={'type_fournisseur': 'Maintenance'})
    date = models.DateField(verbose_name="Date de maintenance")
    km_vehicule = models.PositiveIntegerField(verbose_name="Kilométrage après intervention")
    montant = models.PositiveIntegerField(verbose_name="Montant (FCFA)")
    periodicite_km = models.PositiveIntegerField(verbose_name="Périodicité kilométrique", blank=True, null=True,
                                              help_text="Kilométrage avant la prochaine maintenance de ce type")
    alerte_km = models.PositiveIntegerField(verbose_name="Marge d'alerte kilométrique", blank=True, null=True,
                                         help_text="Marge d'alerte en kilomètres avant l'échéance")
    periodicite_mois = models.PositiveIntegerField(verbose_name="Périodicité en mois", blank=True, null=True,
                                                help_text="Nombre de mois avant la prochaine maintenance de ce type")
    alerte_mois = models.PositiveIntegerField(verbose_name="Marge d'alerte en mois", blank=True, null=True,
                                           help_text="Marge d'alerte en mois avant l'échéance")
    facture = models.FileField(upload_to='factures_maintenance/', verbose_name="Facture", 
                             help_text="Document obligatoire")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    
    class Meta:
        verbose_name = "Maintenance"
        verbose_name_plural = "Maintenances"
        ordering = ['-date']
    
    def __str__(self):
        return f"Maintenance {self.type_maintenance} - {self.vehicule} - {self.date}"

    def clean(self):
        super().clean()

        if self.vehicule_id and self.service_id and self.vehicule.service_id != self.service_id:
            raise ValidationError("Le véhicule sélectionné n'appartient pas au service de la maintenance.")

        if self.fournisseur_id and self.fournisseur.type_fournisseur != 'Maintenance':
            raise ValidationError({'fournisseur': "Le fournisseur doit être de type maintenance."})

        if self.km_vehicule is not None and self.km_vehicule <= 0:
            raise ValidationError({'km_vehicule': "Le kilométrage doit être supérieur à zéro."})

        if self.montant is not None and self.montant <= 0:
            raise ValidationError({'montant': "Le montant doit être supérieur à zéro."})

        if self.periodicite_km and self.alerte_km and self.alerte_km >= self.periodicite_km:
            raise ValidationError({'alerte_km': "L'alerte km doit être strictement inférieure à la périodicité km."})

        if self.periodicite_mois and self.alerte_mois and self.alerte_mois >= self.periodicite_mois:
            raise ValidationError({'alerte_mois': "L'alerte mois doit être strictement inférieure à la périodicité en mois."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

        if self.vehicule and self.km_vehicule and self.km_vehicule > self.vehicule.kilometrage:
            self.vehicule.kilometrage = self.km_vehicule
            self.vehicule.save(update_fields=['kilometrage'])
    
    def format_montant(self):
        """
        Formater le montant avec séparateur de milliers
        """
        if self.montant is None:
            return "0 FCFA"
        return f"{self.montant:,}".replace(',', ' ') + " FCFA"


class Planification(models.Model):
    """
    Modèle représentant une planification de maintenance pour un véhicule.
    Permet de suivre les échéances de maintenance basées sur le kilométrage et la date.
    """
    id = models.AutoField(primary_key=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='planifications', verbose_name="Service")
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='planifications', 
                                  verbose_name="Utilisateur", limit_choices_to={'groupe__nom_groupe': 'Driver Principal'})
    vehicule = models.ForeignKey(Vehicule, on_delete=models.CASCADE, related_name='planifications', verbose_name="Véhicule")
    type_maintenance = models.ForeignKey(TypeMaintenance, on_delete=models.CASCADE, related_name='planifications', 
                                       verbose_name="Type de maintenance")
    prochaine_echeance_km = models.PositiveIntegerField(verbose_name="Prochaine échéance kilométrique", 
                                                     help_text="Kilométrage auquel la prochaine maintenance doit être effectuée")
    prochaine_echeance_date = models.DateField(verbose_name="Prochaine échéance de date", null=True, blank=True,
                                            help_text="Date à laquelle la prochaine maintenance doit être effectuée")
    alerte_km = models.PositiveIntegerField(verbose_name="Marge d'alerte kilométrique", null=True, blank=True,
                                         help_text="Marge d'alerte en kilomètres avant l'échéance")
    alerte_mois = models.PositiveIntegerField(verbose_name="Marge d'alerte en mois", null=True, blank=True,
                                           help_text="Marge d'alerte en mois avant l'échéance")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    
    class Meta:
        verbose_name = "Planification de maintenance"
        verbose_name_plural = "Planifications de maintenance"
        ordering = ['prochaine_echeance_km']
    
    def __str__(self):
        return f"Planification {self.type_maintenance} - {self.vehicule} - Échéance: {self.prochaine_echeance_km} km"

    def clean(self):
        super().clean()

        if self.vehicule_id and self.service_id and self.vehicule.service_id != self.service_id:
            raise ValidationError("Le véhicule sélectionné n'appartient pas au service de la planification.")

        if self.utilisateur_id and self.service_id and not self.utilisateur.service.filter(id_service=self.service_id).exists():
            raise ValidationError({'utilisateur': "L'utilisateur responsable doit appartenir au service sélectionné."})

        if self.prochaine_echeance_km is not None and self.prochaine_echeance_km <= 0:
            raise ValidationError({'prochaine_echeance_km': "L'échéance kilométrique doit être supérieure à zéro."})

        if self.alerte_km and self.prochaine_echeance_km and self.alerte_km >= self.prochaine_echeance_km:
            raise ValidationError({'alerte_km': "L'alerte km doit être strictement inférieure à l'échéance km."})
    
    def est_en_alerte_km(self):
        """
        Vérifie si la planification est en alerte kilométrique.
        """
        if not self.alerte_km:
            return False
        
        # Calculer le kilométrage d'alerte
        km_alerte = self.prochaine_echeance_km - self.alerte_km
        
        # Vérifier si le kilométrage actuel du véhicule dépasse le seuil d'alerte
        return self.vehicule.kilometrage >= km_alerte
    
    def est_en_alerte_date(self):
        """
        Vérifie si la planification est en alerte de date.
        """
        if not self.prochaine_echeance_date or not self.alerte_mois:
            return False
        
        # Calculer la date d'alerte
        from datetime import datetime, timedelta
        from dateutil.relativedelta import relativedelta
        
        date_alerte = self.prochaine_echeance_date - relativedelta(months=self.alerte_mois)
        
        # Vérifier si la date actuelle dépasse le seuil d'alerte
        return datetime.now().date() >= date_alerte
    
    def est_en_retard_km(self):
        """
        Vérifie si la maintenance est en retard par rapport au kilométrage.
        """
        return self.vehicule.kilometrage >= self.prochaine_echeance_km
    
    def est_en_retard_date(self):
        """
        Vérifie si la maintenance est en retard par rapport à la date.
        """
        if not self.prochaine_echeance_date:
            return False
        
        from datetime import datetime
        return datetime.now().date() > self.prochaine_echeance_date
    
    def get_statut(self):
        """
        Retourne le statut de la planification.
        """
        if self.est_en_retard_km() or self.est_en_retard_date():
            return "En retard"
        elif self.est_en_alerte_km() or self.est_en_alerte_date():
            return "En alerte"
        else:
            return "Planifiée"
    
    def get_pourcentage_progression_km(self):
        """
        Calcule le pourcentage de progression vers la prochaine échéance kilométrique.
        """
        # Récupérer la dernière maintenance de ce type pour ce véhicule
        try:
            derniere_maintenance = Maintenance.objects.filter(
                vehicule=self.vehicule,
                type_maintenance=self.type_maintenance
            ).latest('date')
            
            km_initial = derniere_maintenance.km_vehicule
            km_actuel = self.vehicule.kilometrage
            km_cible = self.prochaine_echeance_km
            
            # Calculer le pourcentage
            if km_cible > km_initial:  # Éviter la division par zéro
                progression = (km_actuel - km_initial) / (km_cible - km_initial) * 100
                return min(max(0, progression), 100)  # Limiter entre 0 et 100%
            
        except Maintenance.DoesNotExist:
            pass
        
        return 0


class DemandeCourse(models.Model):
    STATUT_CHOICES = [
        ("soumise", "Soumise"),
        ("rejetée", "Rejetée"),
        ("acceptée", "Acceptée"),
        ("planifiée", "Planifiée"),
        ("terminée", "Terminée"),
    ]

    id_demande_course = models.AutoField(primary_key=True)
    id_service = models.ForeignKey('Service', on_delete=models.CASCADE)
    id_utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='courses_assignees')
    id_auteur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='courses_auteur', null=True, blank=True)
    date_demande = models.DateTimeField(auto_now_add=True)
    lieu_depart = models.CharField(max_length=255)
    lieu_arrivee = models.CharField(max_length=255)
    date_heure_prevue = models.DateTimeField()
    date_heure_fin_retour = models.DateTimeField()
    objet = models.TextField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default="soumise")
    justification_rejet = models.TextField(blank=True, null=True)
    id_vehicule = models.ForeignKey('Vehicule', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f"Demande {self.id_demande_course} - {self.statut}"


class PlanificationCourse(models.Model):
    STATUT_CHOICES = [
        ("planifiée", "Planifiée"),
        ("terminée", "Terminée"),
    ]
    id_planification = models.AutoField(primary_key=True)
    demande = models.OneToOneField('DemandeCourse', on_delete=models.CASCADE, blank=True, null=True)
    date_heure = models.DateTimeField()
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    vehicule = models.ForeignKey('Vehicule', on_delete=models.CASCADE)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default="planifiée")
    lieu_arrivee = models.CharField(max_length=255, blank=True, null=True, verbose_name="Lieu d'arrivée")

    def save(self, *args, **kwargs):
        # Auto-populate lieu_arrivee from demande if not set
        if self.demande and (not self.lieu_arrivee):
            self.lieu_arrivee = self.demande.lieu_arrivee
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Planification {self.id_planification} - {self.statut}"


class ExecutionCourse(models.Model):
    """
    Entité représentant l'exécution effective d'une course planifiée.
    """
    id_execution = models.AutoField(primary_key=True)
    id_planification = models.ForeignKey('PlanificationCourse', on_delete=models.CASCADE, related_name='executions')
    date_heure_debut = models.DateTimeField(verbose_name="Date et heure de début")
    date_heure_fin = models.DateTimeField(verbose_name="Date et heure de fin")
    kilometrage_debut = models.PositiveIntegerField(verbose_name="Kilométrage début")
    kilometrage_fin = models.PositiveIntegerField(verbose_name="Kilométrage fin")
    remarques_chauffeur = models.TextField(blank=True, null=True, verbose_name="Remarques du chauffeur")

    class Meta:
        verbose_name = "Exécution de Course"
        verbose_name_plural = "Exécutions de Course"

    def __str__(self):
        return f"Exécution {self.id_execution} (Planification {self.id_planification_id})"
