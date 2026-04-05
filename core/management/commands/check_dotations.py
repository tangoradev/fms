from django.core.management.base import BaseCommand
from core.models import Service, Achat_Stock_Carburant_HT, Achat_Carburant_TTC, Rechargement_Carte_Carburant
from django.db.models import Sum

class Command(BaseCommand):
    help = 'Vérifie et affiche les dotations disponibles pour un service donné'

    def add_arguments(self, parser):
        parser.add_argument('service_id', type=int, help='ID du service à vérifier')

    def handle(self, *args, **options):
        service_id = options['service_id']
        
        try:
            service = Service.objects.get(id_service=service_id)
            self.stdout.write(self.style.SUCCESS(f"Service: {service.nom_service} (ID: {service.id_service})"))
            
            # Vérifier les dotations HT
            self.stdout.write("\nDotations HT:")
            achats_ht = Achat_Stock_Carburant_HT.objects.filter(service=service).order_by('-date_achat')
            self.stdout.write(f"Nombre d'achats HT trouvés: {achats_ht.count()}")
            
            for achat in achats_ht:
                total_rechargements = Rechargement_Carte_Carburant.objects.filter(
                    achat_stock_carburant_ht=achat
                ).aggregate(total=Sum('montant_ttc'))['total'] or 0
                
                solde_restant = achat.montant_ttc - total_rechargements
                self.stdout.write(f"ID: {achat.id_achat_stock_carburant_ht}, Libellé: {achat.libelle}")
                self.stdout.write(f"  Montant TTC: {achat.montant_ttc} FCFA")
                self.stdout.write(f"  Montant utilisé: {total_rechargements} FCFA")
                self.stdout.write(f"  Solde restant: {solde_restant} FCFA")
                self.stdout.write(f"  Disponible pour sélection: {'Oui' if solde_restant > 0 else 'Non'}")
            
            # Vérifier les dotations TTC
            self.stdout.write("\nDotations TTC:")
            achats_ttc = Achat_Carburant_TTC.objects.filter(service=service).order_by('-date_achat')
            self.stdout.write(f"Nombre d'achats TTC trouvés: {achats_ttc.count()}")
            
            for achat in achats_ttc:
                total_rechargements = Rechargement_Carte_Carburant.objects.filter(
                    achat_carburant_ttc=achat
                ).aggregate(total=Sum('montant_ttc'))['total'] or 0
                
                solde_restant = achat.montant_ttc - total_rechargements
                self.stdout.write(f"ID: {achat.id_achat_carburant_ttc}, Libellé: {achat.libelle}")
                self.stdout.write(f"  Montant TTC: {achat.montant_ttc} FCFA")
                self.stdout.write(f"  Montant utilisé: {total_rechargements} FCFA")
                self.stdout.write(f"  Solde restant: {solde_restant} FCFA")
                self.stdout.write(f"  Disponible pour sélection: {'Oui' if solde_restant > 0 else 'Non'}")
            
            # Vérifier toutes les dotations (pour référence)
            self.stdout.write("\nToutes les dotations HT dans le système:")
            all_ht = Achat_Stock_Carburant_HT.objects.all()
            self.stdout.write(f"Nombre total: {all_ht.count()}")
            for achat in all_ht:
                self.stdout.write(f"ID: {achat.id_achat_stock_carburant_ht}, Service: {achat.service.nom_service}, Libellé: {achat.libelle}")
            
            self.stdout.write("\nToutes les dotations TTC dans le système:")
            all_ttc = Achat_Carburant_TTC.objects.all()
            self.stdout.write(f"Nombre total: {all_ttc.count()}")
            for achat in all_ttc:
                self.stdout.write(f"ID: {achat.id_achat_carburant_ttc}, Service: {achat.service.nom_service}, Libellé: {achat.libelle}")
                
        except Service.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Service avec ID {service_id} non trouvé"))
