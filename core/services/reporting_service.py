import datetime
from calendar import monthrange
from decimal import Decimal

from django.core.exceptions import ValidationError

from core.models import (
    Achat_Carburant_TTC,
    Achat_Stock_Carburant_HT,
    Carte_Carburant,
    Demande_Carte_Carburant,
    Rechargement_Carte_Carburant_HT,
    Rechargement_Carte_Carburant_TTC,
    Service,
)
from core.utils import get_french_month_name


def _compute_releve_for_rechargement(rechargement, demandes_avant, demandes_mois):
    if not demandes_avant.exists():
        solde_ouverture_montant = rechargement.montant_ttc
        solde_ouverture_volume = rechargement.volume
    else:
        derniere_demande = demandes_avant.first()
        solde_ouverture_montant = derniere_demande.nouveau_solde_carte or 0
        ratio = solde_ouverture_montant / rechargement.montant_ttc if rechargement.montant_ttc > 0 else 0
        solde_ouverture_volume = rechargement.volume * Decimal(str(ratio))

    volume_consommation = sum(demande.volume or 0 for demande in demandes_mois)
    montant_consommation = sum(demande.montant_ttc or 0 for demande in demandes_mois)

    solde_cloture_montant = solde_ouverture_montant - montant_consommation
    solde_cloture_volume = solde_ouverture_volume - volume_consommation

    return {
        "ouverture": {"volume": solde_ouverture_volume, "montant": solde_ouverture_montant},
        "consommation": {"volume": volume_consommation, "montant": montant_consommation},
        "cloture": {"volume": solde_cloture_volume, "montant": solde_cloture_montant},
    }


def build_releve_consommation_context(dotation_type, dotation_id, mois, annee, service_id=None):
    """Construit le contexte du relevé de consommation pour une dotation et un mois."""
    try:
        dotation_id = int(dotation_id)
        mois = int(mois)
        annee = int(annee)
    except (TypeError, ValueError) as exc:
        raise ValidationError("Paramètres de relevé invalides.") from exc

    debut_mois = datetime.date(annee, mois, 1)
    _, nb_jours = monthrange(annee, mois)
    fin_mois = datetime.date(annee, mois, nb_jours)

    service_obj = None
    if service_id:
        try:
            service_obj = Service.objects.get(pk=service_id)
        except Service.DoesNotExist as exc:
            raise ValidationError("Le service spécifié n'existe pas.") from exc

    dotation = None
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

    if dotation_type == "ht":
        try:
            dotation = Achat_Stock_Carburant_HT.objects.get(pk=dotation_id)
        except Achat_Stock_Carburant_HT.DoesNotExist as exc:
            raise ValidationError("La dotation spécifiée n'existe pas.") from exc

        rechargements = Rechargement_Carte_Carburant_HT.objects.filter(achat_stock_carburant_ht=dotation)
        cartes_query = Carte_Carburant.objects.filter(rechargements_ht__achat_stock_carburant_ht=dotation)
        if service_obj:
            cartes_query = cartes_query.filter(service=service_obj)
        cartes = cartes_query.distinct()

        for carte in cartes:
            rechargement = rechargements.filter(carte_carburant=carte).first()
            if not rechargement:
                continue

            demandes_avant = Demande_Carte_Carburant.objects.filter(
                rechargement_ht=rechargement,
                date_ravitaillement__lt=debut_mois,
            ).order_by("-date_ravitaillement")
            demandes_mois = Demande_Carte_Carburant.objects.filter(
                rechargement_ht=rechargement,
                date_ravitaillement__gte=debut_mois,
                date_ravitaillement__lte=fin_mois,
            ).order_by("date_ravitaillement")

            releve = _compute_releve_for_rechargement(rechargement, demandes_avant, demandes_mois)
            soldes_ouverture[carte.numero_carte] = releve["ouverture"]
            consommations[carte.numero_carte] = releve["consommation"]
            soldes_cloture[carte.numero_carte] = releve["cloture"]

            total_volume_ouverture += releve["ouverture"]["volume"]
            total_montant_ouverture += releve["ouverture"]["montant"]
            total_volume_consommation += releve["consommation"]["volume"]
            total_montant_consommation += releve["consommation"]["montant"]
            total_volume_cloture += releve["cloture"]["volume"]
            total_montant_cloture += releve["cloture"]["montant"]

    elif dotation_type == "ttc":
        try:
            dotation = Achat_Carburant_TTC.objects.get(pk=dotation_id)
        except Achat_Carburant_TTC.DoesNotExist as exc:
            raise ValidationError("La dotation spécifiée n'existe pas.") from exc

        rechargements = Rechargement_Carte_Carburant_TTC.objects.filter(achat_carburant_ttc=dotation)
        cartes_query = Carte_Carburant.objects.filter(rechargements_ttc__achat_carburant_ttc=dotation)
        if service_obj:
            cartes_query = cartes_query.filter(service=service_obj)
        cartes = cartes_query.distinct()

        for carte in cartes:
            rechargement = rechargements.filter(carte_carburant=carte).first()
            if not rechargement:
                continue

            demandes_avant = Demande_Carte_Carburant.objects.filter(
                rechargement_ttc=rechargement,
                date_ravitaillement__lt=debut_mois,
            ).order_by("-date_ravitaillement")
            demandes_mois = Demande_Carte_Carburant.objects.filter(
                rechargement_ttc=rechargement,
                date_ravitaillement__gte=debut_mois,
                date_ravitaillement__lte=fin_mois,
            ).order_by("date_ravitaillement")

            releve = _compute_releve_for_rechargement(rechargement, demandes_avant, demandes_mois)
            soldes_ouverture[carte.numero_carte] = releve["ouverture"]
            consommations[carte.numero_carte] = releve["consommation"]
            soldes_cloture[carte.numero_carte] = releve["cloture"]

            total_volume_ouverture += releve["ouverture"]["volume"]
            total_montant_ouverture += releve["ouverture"]["montant"]
            total_volume_consommation += releve["consommation"]["volume"]
            total_montant_consommation += releve["consommation"]["montant"]
            total_volume_cloture += releve["cloture"]["volume"]
            total_montant_cloture += releve["cloture"]["montant"]
    else:
        raise ValidationError("Type de dotation invalide.")

    nom_mois = f"{get_french_month_name(mois)} {annee}"
    return {
        "dotation": dotation,
        "dotation_type": dotation_type,
        "mois": nom_mois,
        "cartes": cartes,
        "service": service_obj,
        "soldes_ouverture": soldes_ouverture,
        "consommations": consommations,
        "soldes_cloture": soldes_cloture,
        "total_volume_ouverture": total_volume_ouverture,
        "total_montant_ouverture": total_montant_ouverture,
        "total_volume_consommation": total_volume_consommation,
        "total_montant_consommation": total_montant_consommation,
        "total_volume_cloture": total_volume_cloture,
        "total_montant_cloture": total_montant_cloture,
        "title": f"Relevé de consommation de carburant - {nom_mois}",
        "safe": True,
    }
