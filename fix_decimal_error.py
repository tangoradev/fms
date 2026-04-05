"""
Script pour corriger l'erreur de type decimal.Decimal et float dans views.py
"""
import re

# Chemin du fichier à modifier
file_path = 'core/views.py'

# Lire le contenu du fichier
with open(file_path, 'r', encoding='utf-8') as file:
    content = file.read()

# Motif à rechercher
pattern = r'(ratio = solde_ouverture_montant / rechargement\.montant_ttc if rechargement\.montant_ttc > 0 else 0\n\s+)(solde_ouverture_volume = rechargement\.volume \* ratio)'

# Remplacement avec conversion en Decimal
replacement = r'\1# Convertir le ratio (float) en Decimal pour éviter l\'erreur de type\n        from decimal import Decimal\n        ratio_decimal = Decimal(str(ratio))\n        solde_ouverture_volume = rechargement.volume * ratio_decimal'

# Effectuer le remplacement
new_content = re.sub(pattern, replacement, content)

# Vérifier si le remplacement a été effectué
if content == new_content:
    print("Aucun remplacement effectué. Vérifiez le motif de recherche.")
else:
    # Écrire le contenu modifié dans le fichier
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(new_content)
    print("Correction appliquée avec succès!")

# Faire la même chose pour la partie TTC si elle existe
pattern_ttc = r'(ratio_ttc = solde_ouverture_montant_ttc / rechargement_ttc\.montant_ttc if rechargement_ttc\.montant_ttc > 0 else 0\n\s+)(solde_ouverture_volume_ttc = rechargement_ttc\.volume \* ratio_ttc)'

replacement_ttc = r'\1# Convertir le ratio (float) en Decimal pour éviter l\'erreur de type\n        from decimal import Decimal\n        ratio_ttc_decimal = Decimal(str(ratio_ttc))\n        solde_ouverture_volume_ttc = rechargement_ttc.volume * ratio_ttc_decimal'

new_content = re.sub(pattern_ttc, replacement_ttc, new_content)

# Écrire le contenu modifié dans le fichier
with open(file_path, 'w', encoding='utf-8') as file:
    file.write(new_content)
print("Vérification des parties TTC terminée.")
