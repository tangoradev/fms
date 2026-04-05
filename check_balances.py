# Script pour vu00e9rifier les soldes thu00e9oriques des dotations

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fms.settings')
django.setup()

from core.models import Achat_Stock_Carburant_HT, Achat_Carburant_TTC, Rechargement_Carte_Carburant
from django.db.models import Sum

# Vu00e9rifier les soldes des dotations HT
print("=== Soldes thu00e9oriques des dotations HT ===\n")
achats_ht = Achat_Stock_Carburant_HT.objects.filter(statut='Ouverte').order_by('-date_achat')
print(f"Nombre d'achats HT trouvu00e9s avec statut 'Ouverte': {achats_ht.count()}")

for achat in achats_ht:
    # Ru00e9cupu00e9rer le montant total des rechargements pour cette dotation
    total_rechargements = Rechargement_Carte_Carburant.objects.filter(
        achat_stock_carburant_ht=achat
    ).aggregate(total=Sum('montant_ttc'))['total'] or 0
    
    # Calculer le solde thu00e9orique
    solde_theorique = achat.montant_ttc - total_rechargements
    
    # Formater le solde avec des su00e9parateurs de milliers
    solde_formatte = '{:,.0f}'.format(solde_theorique).replace(',', ' ')
    
    print(f"ID: {achat.id_achat_stock_carburant_ht}, Libellu00e9: {achat.libelle}")
    print(f"Service: {achat.service.nom_service}, Type: {achat.type_carburant}")
    print(f"Montant TTC: {achat.montant_ttc}, Total rechargements: {total_rechargements}")
    print(f"Solde thu00e9orique: {solde_theorique}, Formatu00e9: {solde_formatte} FCFA")
    print("---")

# Vu00e9rifier les soldes des dotations TTC
print("\n=== Soldes thu00e9oriques des dotations TTC ===\n")
achats_ttc = Achat_Carburant_TTC.objects.filter(statut='Ouverte').order_by('-date_achat')
print(f"Nombre d'achats TTC trouvu00e9s avec statut 'Ouverte': {achats_ttc.count()}")

for achat in achats_ttc:
    # Ru00e9cupu00e9rer le montant total des rechargements pour cette dotation
    total_rechargements = Rechargement_Carte_Carburant.objects.filter(
        achat_carburant_ttc=achat
    ).aggregate(total=Sum('montant_ttc'))['total'] or 0
    
    # Calculer le solde thu00e9orique
    solde_theorique = achat.montant_ttc - total_rechargements
    
    # Formater le solde avec des su00e9parateurs de milliers
    solde_formatte = '{:,.0f}'.format(solde_theorique).replace(',', ' ')
    
    print(f"ID: {achat.id_achat_carburant_ttc}, Libellu00e9: {achat.libelle}")
    print(f"Service: {achat.service.nom_service}, Type: {achat.type_carburant}")
    print(f"Montant TTC: {achat.montant_ttc}, Total rechargements: {total_rechargements}")
    print(f"Solde thu00e9orique: {solde_theorique}, Formatu00e9: {solde_formatte} FCFA")
    print("---")
