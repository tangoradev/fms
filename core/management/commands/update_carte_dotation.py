from django.core.management.base import BaseCommand
from django.db.models import Max
from core.models import Carte_Carburant, Rechargement_Carte_Carburant

class Command(BaseCommand):
    help = 'Met u00e0 jour les associations entre cartes et dotations actives en fonction des rechargements existants'

    def handle(self, *args, **options):
        # Ru00e9cupu00e9rer toutes les cartes carburant
        cartes = Carte_Carburant.objects.all()
        self.stdout.write(f"Mise u00e0 jour de {cartes.count()} cartes carburant...")
        
        for carte in cartes:
            # Si la carte a un solde de 0, elle ne doit pas u00eatre associu00e9e u00e0 une dotation
            if carte.solde == 0:
                if carte.dotation_active_ht or carte.dotation_active_ttc:
                    old_dotation = carte.dotation_active_ht or carte.dotation_active_ttc
                    carte.dotation_active_ht = None
                    carte.dotation_active_ttc = None
                    carte.save()
                    self.stdout.write(self.style.SUCCESS(
                        f"Carte {carte.numero_carte}: solde 0, association u00e0 la dotation {old_dotation} supprimu00e9e"
                    ))
                else:
                    self.stdout.write(f"Carte {carte.numero_carte}: solde 0, aucune association u00e0 mettre u00e0 jour")
                continue
            
            # Ru00e9cupu00e9rer le dernier rechargement de la carte
            dernier_rechargement = Rechargement_Carte_Carburant.objects.filter(
                carte_carburant=carte
            ).order_by('-date_rechargement').first()
            
            if not dernier_rechargement:
                self.stdout.write(f"Carte {carte.numero_carte}: aucun rechargement trouvu00e9")
                continue
            
            # Mettre u00e0 jour l'association de la carte avec la dotation active
            if dernier_rechargement.achat_stock_carburant_ht:
                if carte.dotation_active_ht != dernier_rechargement.achat_stock_carburant_ht or carte.dotation_active_ttc is not None:
                    old_dotation = carte.dotation_active_ht or carte.dotation_active_ttc
                    carte.dotation_active_ht = dernier_rechargement.achat_stock_carburant_ht
                    carte.dotation_active_ttc = None
                    carte.save()
                    self.stdout.write(self.style.SUCCESS(
                        f"Carte {carte.numero_carte}: association mise u00e0 jour de {old_dotation} u00e0 "
                        f"HT {dernier_rechargement.achat_stock_carburant_ht.id_achat_stock_carburant_ht}"
                    ))
                else:
                    self.stdout.write(f"Carte {carte.numero_carte}: du00e9ju00e0 associu00e9e u00e0 la bonne dotation HT")
            elif dernier_rechargement.achat_carburant_ttc:
                if carte.dotation_active_ttc != dernier_rechargement.achat_carburant_ttc or carte.dotation_active_ht is not None:
                    old_dotation = carte.dotation_active_ttc or carte.dotation_active_ht
                    carte.dotation_active_ttc = dernier_rechargement.achat_carburant_ttc
                    carte.dotation_active_ht = None
                    carte.save()
                    self.stdout.write(self.style.SUCCESS(
                        f"Carte {carte.numero_carte}: association mise u00e0 jour de {old_dotation} u00e0 "
                        f"TTC {dernier_rechargement.achat_carburant_ttc.id_achat_carburant_ttc}"
                    ))
                else:
                    self.stdout.write(f"Carte {carte.numero_carte}: du00e9ju00e0 associu00e9e u00e0 la bonne dotation TTC")
        
        self.stdout.write(self.style.SUCCESS('Mise u00e0 jour des associations cartes-dotations terminu00e9e avec succu00e8s!'))
