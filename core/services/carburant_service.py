from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction


@transaction.atomic
def create_rechargement(rechargement):
    """Crée un rechargement en appliquant la logique modèle atomiquement."""
    rechargement.save()
    return rechargement


@transaction.atomic
def close_dotation_if_needed(achat):
    """Recalcule et ferme/ouvre une dotation via la logique save du modèle."""
    achat.save()
    return achat.statut


@transaction.atomic
def apply_consumption(demande, rechargement):
    """Applique une consommation de demande sur un rechargement et recalcule la carte."""
    if demande.montant_ttc is None or demande.montant_ttc <= 0:
        raise ValidationError("Le montant TTC doit être supérieur à zéro.")

    if demande.volume is None or demande.volume <= 0:
        raise ValidationError("Le volume doit être supérieur à zéro.")

    if rechargement.solde_restant is None:
        rechargement.solde_restant = rechargement.montant_ttc

    demande.ancien_solde_carte = demande.ancien_solde_carte or rechargement.solde_restant
    demande.nouveau_solde_carte = max(
        Decimal("0"),
        Decimal(str(demande.ancien_solde_carte)) - Decimal(str(demande.montant_ttc)),
    )

    if rechargement.montant_ttc > 0:
        ratio = Decimal(str(demande.montant_ttc)) / Decimal(str(rechargement.montant_ttc))
        current_volume_restant = rechargement.volume_restant if rechargement.volume_restant is not None else rechargement.volume
        rechargement.volume_restant = max(Decimal("0"), Decimal(str(current_volume_restant)) - (Decimal(str(rechargement.volume)) * ratio))

    rechargement.solde_restant = int(demande.nouveau_solde_carte)
    rechargement.save()

    carte = rechargement.carte_carburant
    carte.recalculer_solde()

    return demande, rechargement, carte
