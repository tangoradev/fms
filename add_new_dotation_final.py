# Script pour ajouter une nouvelle dotation avec un solde positif

import os
import django
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fms.settings')
django.setup()

from core.models import Achat_Stock_Carburant_HT, Service, Fournisseur
from django.utils import timezone

# Ru00e9cupu00e9rer le service PNUD CIV
try:
    service = Service.objects.get(nom_service='PNUD CIV')
    print(f"Service trouvu00e9: {service.nom_service} (ID: {service.id_service})")
    
    # Ru00e9cupu00e9rer ou cru00e9er le fournisseur
    fournisseur, created = Fournisseur.objects.get_or_create(
        nom_fournisseur='TotalEnergies Cu00f4te d\'Ivoire',
        defaults={
            'adresse': 'Abidjan, Cu00f4te d\'Ivoire',
            'telephone': '+225 27 20 20 20 20',
            'email': 'contact@totalenergies.ci',
            'type_fournisseur': 'Carburant'
        }
    )
    print(f"Fournisseur {'cru00e9u00e9' if created else 'trouvu00e9'}: {fournisseur.nom_fournisseur} (ID: {fournisseur.id_fournisseur})")
    
    # Cru00e9er une nouvelle dotation pour le 4e trimestre 2024
    nouvelle_dotation = Achat_Stock_Carburant_HT(
        service=service,
        fournisseur=fournisseur,
        date_achat=timezone.now(),
        type_carburant='Gasoil',
        volume=1000,
        montant_ht=2000000,
        montant_ttc=2360000,
        statut='Ouverte',
        libelle='CARBURANT GASOIL 4e TRIMESTRE 2024',
        voucher=f'DV-{datetime.now().strftime("%Y%m%d")}-001',
        business_unit='PNUD',
        dept_id='FIN',
        project_id='CARB-2024'
    )
    nouvelle_dotation.save()
    
    print(f"Nouvelle dotation cru00e9u00e9e avec succu00e8s:")
    print(f"ID: {nouvelle_dotation.id_achat_stock_carburant_ht}, Libellu00e9: {nouvelle_dotation.libelle}")
    print(f"Montant TTC: {nouvelle_dotation.montant_ttc} FCFA, Solde: {nouvelle_dotation.montant_ttc} FCFA")
    
    # Cru00e9er une dotation pour l'essence aussi
    nouvelle_dotation_essence = Achat_Stock_Carburant_HT(
        service=service,
        fournisseur=fournisseur,
        date_achat=timezone.now(),
        type_carburant='Essence',
        volume=500,
        montant_ht=1000000,
        montant_ttc=1180000,
        statut='Ouverte',
        libelle='CARBURANT SUPER 4e TRIMESTRE 2024',
        voucher=f'DV-{datetime.now().strftime("%Y%m%d")}-002',
        business_unit='PNUD',
        dept_id='FIN',
        project_id='CARB-2024'
    )
    nouvelle_dotation_essence.save()
    
    print(f"Nouvelle dotation essence cru00e9u00e9e avec succu00e8s:")
    print(f"ID: {nouvelle_dotation_essence.id_achat_stock_carburant_ht}, Libellu00e9: {nouvelle_dotation_essence.libelle}")
    print(f"Montant TTC: {nouvelle_dotation_essence.montant_ttc} FCFA, Solde: {nouvelle_dotation_essence.montant_ttc} FCFA")
    
except Service.DoesNotExist:
    print("Service PNUD CIV non trouvu00e9")
except Exception as e:
    print(f"Erreur: {e}")
