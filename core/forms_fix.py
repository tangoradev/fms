# Fichier temporaire pour corriger le calcul des soldes théoriques

def calculate_theoretical_balance(achat_ht):
    from core.models import Rechargement_Carte_Carburant
    from django.db.models import Sum
    
    # Récupérer le montant total des rechargements pour cette dotation
    total_rechargements = Rechargement_Carte_Carburant.objects.filter(
        achat_stock_carburant_ht=achat_ht
    ).aggregate(total=Sum('montant_ttc'))['total'] or 0
    
    # Calculer le solde théorique
    solde_theorique = achat_ht.montant_ttc - total_rechargements
    
    # Formater le solde avec des séparateurs de milliers
    solde_formatte = '{:,.0f}'.format(solde_theorique).replace(',', ' ')
    
    return solde_theorique, solde_formatte

def calculate_theoretical_balance_ttc(achat_ttc):
    from core.models import Rechargement_Carte_Carburant
    from django.db.models import Sum
    
    # Récupérer le montant total des rechargements pour cette dotation
    total_rechargements = Rechargement_Carte_Carburant.objects.filter(
        achat_carburant_ttc=achat_ttc
    ).aggregate(total=Sum('montant_ttc'))['total'] or 0
    
    # Calculer le solde théorique
    solde_theorique = achat_ttc.montant_ttc - total_rechargements
    
    # Formater le solde avec des séparateurs de milliers
    solde_formatte = '{:,.0f}'.format(solde_theorique).replace(',', ' ')
    
    return solde_theorique, solde_formatte
