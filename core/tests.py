from datetime import timedelta
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .forms import DemandeCarteCarburantTraitementForm
from .services import build_releve_consommation_context, close_demande, reject_demande, validate_demande
from .models import (
    Achat_Stock_Carburant_HT,
    Achat_Carburant_TTC,
    Carte_Carburant,
    Demande_Carte_Carburant,
    Fournisseur,
    Groupe,
    Rechargement_Carte_Carburant_HT,
    Rechargement_Carte_Carburant_TTC,
    Service,
    Utilisateur,
    Vehicule,
    VehiculeAffectation,
    VehiculeDocument,
)


class FleetModuleTests(TestCase):
    def setUp(self):
        self.service_a = Service.objects.create(nom_service="Service A")
        self.service_b = Service.objects.create(nom_service="Service B")
        self.driver_group = Groupe.objects.create(nom_groupe="Driver")

        self.user_a = Utilisateur.objects.create_user(
            email="usera@example.com",
            nom_complet="User A",
            password="pass12345",
        )
        self.user_a.groupe.add(self.driver_group)
        self.user_a.service.add(self.service_a)

        self.user_b = Utilisateur.objects.create_user(
            email="userb@example.com",
            nom_complet="User B",
            password="pass12345",
        )
        self.user_b.groupe.add(self.driver_group)
        self.user_b.service.add(self.service_b)

        self.vehicule_a = Vehicule.objects.create(
            service=self.service_a,
            marque="Toyota",
            modele="Hilux",
            chassis="CHASSIS-A",
            immatriculation="AA-123-BB",
            type_carburant="Gasoil",
            date_mise_en_service=timezone.now().date() - timedelta(days=365),
            kilometrage=10000,
            statut="Disponible",
        )
        self.vehicule_b = Vehicule.objects.create(
            service=self.service_b,
            marque="Nissan",
            modele="Navara",
            chassis="CHASSIS-B",
            immatriculation="CC-456-DD",
            type_carburant="Gasoil",
            date_mise_en_service=timezone.now().date() - timedelta(days=200),
            kilometrage=15000,
            statut="Disponible",
        )

    def test_vehicule_accepts_extended_status(self):
        self.vehicule_a.statut = "En maintenance"
        self.vehicule_a.full_clean()
        self.vehicule_a.save()
        self.assertEqual(self.vehicule_a.statut, "En maintenance")

    def test_vehicule_future_service_date_invalid(self):
        self.vehicule_a.date_mise_en_service = timezone.now().date() + timedelta(days=2)
        with self.assertRaises(ValidationError):
            self.vehicule_a.full_clean()

    def test_single_active_affectation_per_vehicle(self):
        VehiculeAffectation.objects.create(
            vehicule=self.vehicule_a,
            service=self.service_a,
            chauffeur=self.user_a,
        )
        second = VehiculeAffectation(
            vehicule=self.vehicule_a,
            service=self.service_b,
            chauffeur=self.user_b,
        )
        with self.assertRaises(ValidationError):
            second.full_clean()

    def test_vehicules_list_is_filtered_by_user_service(self):
        self.client.force_login(self.user_a)
        response = self.client.get(reverse('vehicules_list'))
        self.assertContains(response, "AA-123-BB")
        self.assertNotContains(response, "CC-456-DD")

    def test_create_vehicle_document_view(self):
        self.client.force_login(self.user_a)
        response = self.client.post(
            reverse('vehicule_document_create', args=[self.vehicule_a.pk]),
            {
                'type_document': 'assurance',
                'reference': 'POL-001',
                'date_emission': timezone.now().date() - timedelta(days=30),
                'date_expiration': timezone.now().date() + timedelta(days=30),
                'commentaire': 'Police valide',
                'est_actif': 'on',
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(VehiculeDocument.objects.filter(vehicule=self.vehicule_a).count(), 1)


class FuelModuleTests(TestCase):
    def setUp(self):
        self.service = Service.objects.create(nom_service="Service Carburant")
        self.gestionnaire_group = Groupe.objects.create(nom_groupe="Gestionnaire Carburant")
        self.driver_group = Groupe.objects.create(nom_groupe="Driver")

        self.user = Utilisateur.objects.create_user(
            email="gestionnaire.carburant@example.com",
            nom_complet="Gestionnaire Carburant",
            password="pass12345",
        )
        self.user.groupe.add(self.gestionnaire_group)
        self.user.service.add(self.service)

        self.driver = Utilisateur.objects.create_user(
            email="driver.carburant@example.com",
            nom_complet="Driver Carburant",
            password="pass12345",
        )
        self.driver.groupe.add(self.driver_group)
        self.driver.service.add(self.service)

        self.vehicule = Vehicule.objects.create(
            service=self.service,
            marque="Toyota",
            modele="Hilux",
            chassis="CHS-CARB-001",
            immatriculation="CB-001-AA",
            type_carburant="Gasoil",
            date_mise_en_service=timezone.now().date() - timedelta(days=120),
            kilometrage=10000,
            statut="Disponible",
        )

        self.fournisseur = Fournisseur.objects.create(
            nom_fournisseur="Total Energies",
            type_fournisseur="Carburant",
        )

    def test_carte_bloquee_status_is_preserved_on_save(self):
        carte = Carte_Carburant.objects.create(
            service=self.service,
            numero_carte="CARD-BLOCK-001",
            solde=5000,
            statut="Bloquée",
        )

        carte.solde = 0
        carte.save()
        carte.refresh_from_db()

        self.assertEqual(carte.statut, "Bloquée")

    def test_rechargement_ttc_cannot_exceed_dotation_amount(self):
        achat = Achat_Carburant_TTC.objects.create(
            service=self.service,
            fournisseur=self.fournisseur,
            voucher="VCH-TTC-001",
            business_unit="BU-01",
            dept_id="D-01",
            project_id="P-01",
            date_achat=timezone.now().date(),
            libelle="Dotation TTC test",
            type_carburant="Gasoil",
            volume=100,
            montant_ttc=1000,
        )

        carte_1 = Carte_Carburant.objects.create(
            service=self.service,
            numero_carte="CARD-TTC-001",
            solde=0,
            statut="Disponible",
        )
        carte_2 = Carte_Carburant.objects.create(
            service=self.service,
            numero_carte="CARD-TTC-002",
            solde=0,
            statut="Disponible",
        )

        Rechargement_Carte_Carburant_TTC.objects.create(
            achat_carburant_ttc=achat,
            carte_carburant=carte_1,
            date_rechargement=timezone.now().date(),
            volume=40,
            prix_unitaire_ttc=20,
            montant_ttc=800,
        )

        rechargement_depassement = Rechargement_Carte_Carburant_TTC(
            achat_carburant_ttc=achat,
            carte_carburant=carte_2,
            date_rechargement=timezone.now().date(),
            volume=20,
            prix_unitaire_ttc=15,
            montant_ttc=300,
        )

        with self.assertRaises(ValidationError):
            rechargement_depassement.full_clean()

    def test_dashboard_carburant_renders_without_consumption_data(self):
        self.client.force_login(self.user)
        with patch('core.views.render', return_value=HttpResponse(status=200)):
            response = self.client.get(reverse('dashboard_carburant'))
        self.assertEqual(response.status_code, 200)

    def test_rechargement_ht_forbidden_when_ttc_dotation_active(self):
        achat_ttc = Achat_Carburant_TTC.objects.create(
            service=self.service,
            fournisseur=self.fournisseur,
            voucher="VCH-TTC-LOCK-001",
            business_unit="BU-01",
            dept_id="D-01",
            project_id="P-01",
            date_achat=timezone.now().date(),
            libelle="Dotation TTC active",
            type_carburant="Gasoil",
            volume=100,
            montant_ttc=2000,
        )
        achat_ht = Achat_Stock_Carburant_HT.objects.create(
            service=self.service,
            fournisseur=self.fournisseur,
            voucher="VCH-HT-001",
            business_unit="BU-01",
            dept_id="D-01",
            project_id="P-01",
            date_achat=timezone.now().date(),
            libelle="Dotation HT test",
            type_carburant="Gasoil",
            volume=100,
            montant_ht=1000,
            montant_ttc=1200,
        )
        carte = Carte_Carburant.objects.create(
            service=self.service,
            numero_carte="CARD-MUTEX-001",
            solde=0,
            statut="Disponible",
        )

        Rechargement_Carte_Carburant_TTC.objects.create(
            achat_carburant_ttc=achat_ttc,
            carte_carburant=carte,
            date_rechargement=timezone.now().date(),
            volume=30,
            prix_unitaire_ttc=20,
            montant_ttc=600,
        )

        rechargement_ht = Rechargement_Carte_Carburant_HT(
            achat_stock_carburant_ht=achat_ht,
            carte_carburant=carte,
            date_rechargement=timezone.now().date(),
            volume=10,
            prix_unitaire_ttc=20,
            montant_ttc=200,
        )

        with self.assertRaises(ValidationError):
            rechargement_ht.full_clean()

    def test_demande_traitement_requires_comment_on_reject(self):
        demande = Demande_Carte_Carburant.objects.create(
            service=self.service,
            utilisateur_demandeur=self.driver,
            vehicule=self.vehicule,
            motif_demande="Ravitaillement mission",
            statut_demande="En attente",
        )

        form = DemandeCarteCarburantTraitementForm(
            data={
                'statut_demande': 'Rejetée',
                'dotation': '',
                'commentaire': '',
            },
            instance=demande,
            service=self.service,
        )

        self.assertFalse(form.is_valid())
        self.assertIn('commentaire', form.errors)

    def test_demande_services_validate_and_reject(self):
        demande = Demande_Carte_Carburant.objects.create(
            service=self.service,
            utilisateur_demandeur=self.driver,
            vehicule=self.vehicule,
            motif_demande="Besoin carburant",
            statut_demande="En attente",
        )

        validate_demande(demande, utilisateur_traitant=self.user, commentaire="OK")
        demande.refresh_from_db()
        self.assertEqual(demande.statut_demande, "Acceptée")
        self.assertEqual(demande.utilisateur_traitant, self.user)

        demande_2 = Demande_Carte_Carburant.objects.create(
            service=self.service,
            utilisateur_demandeur=self.driver,
            vehicule=self.vehicule,
            motif_demande="Autre besoin",
            statut_demande="En attente",
        )
        reject_demande(demande_2, utilisateur_traitant=self.user, commentaire="Incomplet")
        demande_2.refresh_from_db()
        self.assertEqual(demande_2.statut_demande, "Rejetée")
        self.assertEqual(demande_2.commentaire, "Incomplet")

    def test_close_demande_applies_consumption(self):
        achat = Achat_Carburant_TTC.objects.create(
            service=self.service,
            fournisseur=self.fournisseur,
            voucher="VCH-CLOSE-001",
            business_unit="BU-01",
            dept_id="D-01",
            project_id="P-01",
            date_achat=timezone.now().date(),
            libelle="Dotation close",
            type_carburant="Gasoil",
            volume=100,
            montant_ttc=1000,
        )
        carte = Carte_Carburant.objects.create(
            service=self.service,
            numero_carte="CARD-CLOSE-001",
            solde=0,
            statut="Disponible",
        )
        rechargement = Rechargement_Carte_Carburant_TTC.objects.create(
            achat_carburant_ttc=achat,
            carte_carburant=carte,
            date_rechargement=timezone.now().date(),
            volume=50,
            prix_unitaire_ttc=20,
            montant_ttc=1000,
        )
        demande = Demande_Carte_Carburant.objects.create(
            service=self.service,
            utilisateur_demandeur=self.driver,
            vehicule=self.vehicule,
            motif_demande="Conso mission",
            statut_demande="Acceptée",
            rechargement_ttc=rechargement,
            date_ravitaillement=timezone.now().date(),
            km_vehicule=11000,
            volume=10,
            montant_ttc=200,
            station_service="Station X",
        )

        with patch.object(Demande_Carte_Carburant, 'regenerer_fiche_ravitaillement', return_value=None):
            close_demande(demande, rechargement=rechargement)

        demande.refresh_from_db()
        rechargement.refresh_from_db()
        carte.refresh_from_db()

        self.assertEqual(demande.statut_demande, "Close")
        self.assertEqual(rechargement.solde_restant, 800)
        self.assertEqual(carte.solde, 800)

    def test_reporting_service_build_context(self):
        achat = Achat_Stock_Carburant_HT.objects.create(
            service=self.service,
            fournisseur=self.fournisseur,
            voucher="VCH-RPT-001",
            business_unit="BU-01",
            dept_id="D-01",
            project_id="P-01",
            date_achat=timezone.now().date(),
            libelle="Dotation report",
            type_carburant="Gasoil",
            volume=100,
            montant_ht=1000,
            montant_ttc=1200,
        )
        carte = Carte_Carburant.objects.create(
            service=self.service,
            numero_carte="CARD-RPT-001",
            solde=0,
            statut="Disponible",
        )
        rechargement = Rechargement_Carte_Carburant_HT.objects.create(
            achat_stock_carburant_ht=achat,
            carte_carburant=carte,
            date_rechargement=timezone.now().date(),
            volume=60,
            prix_unitaire_ttc=20,
            montant_ttc=1200,
        )
        Demande_Carte_Carburant.objects.create(
            service=self.service,
            utilisateur_demandeur=self.driver,
            vehicule=self.vehicule,
            motif_demande="Conso report",
            statut_demande="Close",
            rechargement_ht=rechargement,
            date_ravitaillement=timezone.now().date(),
            km_vehicule=11500,
            volume=6,
            montant_ttc=120,
            station_service="Station Y",
            ancien_solde_carte=1200,
            nouveau_solde_carte=1080,
        )

        context = build_releve_consommation_context(
            dotation_type='ht',
            dotation_id=achat.id_achat_stock_carburant_ht,
            mois=timezone.now().month,
            annee=timezone.now().year,
            service_id=self.service.id_service,
        )

        self.assertEqual(context['dotation'], achat)
        self.assertIn('CARD-RPT-001', context['consommations'])
