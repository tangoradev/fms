from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .carburant_service import apply_consumption


@transaction.atomic
def validate_demande(demande, utilisateur_traitant, commentaire=None):
    """Valide une demande en attente."""
    if demande.statut_demande == "Close":
        raise ValidationError("Une demande clôturée ne peut pas être validée.")

    demande.statut_demande = "Acceptée"
    demande.utilisateur_traitant = utilisateur_traitant
    demande.date_traitement = demande.date_traitement or timezone.now()
    if commentaire is not None:
        demande.commentaire = commentaire
    demande.save()
    return demande


@transaction.atomic
def reject_demande(demande, utilisateur_traitant, commentaire):
    """Rejette une demande avec commentaire obligatoire."""
    if not (commentaire or "").strip():
        raise ValidationError("Un commentaire est obligatoire pour rejeter la demande.")

    demande.statut_demande = "Rejetée"
    demande.utilisateur_traitant = utilisateur_traitant
    demande.commentaire = commentaire.strip()
    demande.date_traitement = demande.date_traitement or timezone.now()
    demande.date_cloture = demande.date_cloture or timezone.now()
    demande.save()
    return demande


@transaction.atomic
def close_demande(demande, rechargement=None):
    """Clôture une demande et applique la consommation si un rechargement est lié."""
    if demande.statut_demande not in ("Acceptée", "Close"):
        raise ValidationError("Seules les demandes acceptées peuvent être clôturées.")

    if demande.montant_ttc is None or demande.montant_ttc <= 0:
        raise ValidationError("Le montant TTC doit être supérieur à zéro.")

    if demande.volume is None or demande.volume <= 0:
        raise ValidationError("Le volume doit être supérieur à zéro.")

    if demande.km_vehicule is None or demande.km_vehicule <= 0:
        raise ValidationError("Le kilométrage doit être supérieur à zéro.")

    if not (demande.station_service or "").strip():
        raise ValidationError("La station service est obligatoire.")

    demande.statut_demande = "Close"
    demande.date_cloture = demande.date_cloture or timezone.now()

    if rechargement is not None:
        apply_consumption(demande, rechargement)

    demande.save()
    demande.regenerer_fiche_ravitaillement()
    return demande
