from dateutil.relativedelta import relativedelta

from django.core.exceptions import ValidationError
from django.db import transaction

from core.models import Planification, Utilisateur


def _resolve_driver_principal(service, fallback_user=None):
    principal = (
        Utilisateur.objects.filter(
            groupe__nom_groupe='Driver Principal',
            service=service,
        )
        .distinct()
        .first()
    )
    return principal or fallback_user


def _compute_next_deadlines(maintenance):
    next_km = 0
    next_date = None

    if maintenance.periodicite_km:
        next_km = maintenance.km_vehicule + maintenance.periodicite_km

    if maintenance.periodicite_mois:
        next_date = maintenance.date + relativedelta(months=maintenance.periodicite_mois)

    return next_km, next_date


@transaction.atomic
def sync_planification_for_maintenance(maintenance, fallback_user=None):
    if not (maintenance.periodicite_km or maintenance.periodicite_mois):
        return None, False

    utilisateur = _resolve_driver_principal(maintenance.service, fallback_user=fallback_user)
    if utilisateur is None:
        raise ValidationError("Aucun responsable n'a pu être associé à la planification.")

    prochaine_echeance_km, prochaine_echeance_date = _compute_next_deadlines(maintenance)

    planification, created = Planification.objects.update_or_create(
        vehicule=maintenance.vehicule,
        type_maintenance=maintenance.type_maintenance,
        defaults={
            'service': maintenance.service,
            'utilisateur': utilisateur,
            'prochaine_echeance_km': prochaine_echeance_km,
            'prochaine_echeance_date': prochaine_echeance_date,
            'alerte_km': maintenance.alerte_km,
            'alerte_mois': maintenance.alerte_mois,
        },
    )
    return planification, created


@transaction.atomic
def persist_maintenance_with_business_rules(maintenance, fallback_user=None):
    maintenance.save()

    vehicule = maintenance.vehicule
    if maintenance.km_vehicule and maintenance.km_vehicule > vehicule.kilometrage:
        vehicule.kilometrage = maintenance.km_vehicule
        vehicule.save(update_fields=['kilometrage'])

    return sync_planification_for_maintenance(maintenance, fallback_user=fallback_user)
