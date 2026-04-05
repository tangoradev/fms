"""
Script pour corriger l'erreur d'indentation dans views.py
"""

# Chemin du fichier à modifier
file_path = 'core/views.py'

# Lire le contenu du fichier
with open(file_path, 'r', encoding='utf-8') as file:
    lines = file.readlines()

# Identifier et corriger les lignes problématiques
fixed_lines = []
in_problematic_section = False
for line in lines:
    if "# Convertir le ratio (float) en Decimal pour éviter l\\'erreur de type" in line:
        # Nous avons trouvé le début de la section problématique
        in_problematic_section = True
        # Conserver l'indentation correcte (24 espaces)
        fixed_lines.append(line)
    elif in_problematic_section and ("from decimal import Decimal" in line or 
                                    "ratio_decimal = Decimal(str(ratio))" in line or 
                                    "solde_ouverture_volume = rechargement.volume * ratio_decimal" in line):
        # Corriger l'indentation pour ces lignes (24 espaces)
        fixed_lines.append("                        " + line.lstrip())
        # Si c'est la dernière ligne de la section problématique
        if "solde_ouverture_volume = rechargement.volume * ratio_decimal" in line:
            in_problematic_section = False
    else:
        # Conserver les autres lignes telles quelles
        fixed_lines.append(line)

# Écrire le contenu corrigé dans le fichier
with open(file_path, 'w', encoding='utf-8') as file:
    file.writelines(fixed_lines)

print("Correction de l'indentation terminée!")

# Faire la même chose pour la partie TTC si elle existe
# (Code similaire pour la partie TTC si nécessaire)
