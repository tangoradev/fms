from django.core.management.base import BaseCommand
from core.models import Achat_Stock_Carburant_HT, Achat_Carburant_TTC

class Command(BaseCommand):
    help = 'Met à jour le statut des dotations en fonction du solde théorique'

    def handle(self, *args, **options):
        # Mettre à jour les dotations HT
        dotations_ht = Achat_Stock_Carburant_HT.objects.all()
        self.stdout.write(f"Mise à jour de {dotations_ht.count()} dotations HT...")
        
        for dotation in dotations_ht:
            old_status = dotation.statut
            # Le fait d'appeler save() va déclencher la mise à jour du statut
            dotation.save()
            if old_status != dotation.statut:
                self.stdout.write(self.style.SUCCESS(
                    f"Dotation HT {dotation.id_achat_stock_carburant_ht} - {dotation.libelle}: "
                    f"statut changé de {old_status} à {dotation.statut}"
                ))
            else:
                self.stdout.write(
                    f"Dotation HT {dotation.id_achat_stock_carburant_ht} - {dotation.libelle}: "
                    f"statut inchangé ({dotation.statut})"
                )
        
        # Mettre à jour les dotations TTC
        dotations_ttc = Achat_Carburant_TTC.objects.all()
        self.stdout.write(f"Mise à jour de {dotations_ttc.count()} dotations TTC...")
        
        for dotation in dotations_ttc:
            old_status = dotation.statut
            # Le fait d'appeler save() va déclencher la mise à jour du statut
            dotation.save()
            if old_status != dotation.statut:
                self.stdout.write(self.style.SUCCESS(
                    f"Dotation TTC {dotation.id_achat_carburant_ttc} - {dotation.libelle}: "
                    f"statut changé de {old_status} à {dotation.statut}"
                ))
            else:
                self.stdout.write(
                    f"Dotation TTC {dotation.id_achat_carburant_ttc} - {dotation.libelle}: "
                    f"statut inchangé ({dotation.statut})"
                )
        
        self.stdout.write(self.style.SUCCESS('Mise à jour des statuts terminée avec succès!'))
