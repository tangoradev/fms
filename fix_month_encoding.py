"""
Script pour corriger le problu00e8me d'encodage des noms de mois en franu00e7ais
"""

# Chemin du fichier u00e0 modifier
file_path = 'core/views.py'

# Lire le contenu du fichier
with open(file_path, 'r', encoding='utf-8') as file:
    content = file.read()

# Remplacer l'utilisation de calendar.month_name par une fonction personnalisu00e9e
import re

# Ajouter la fonction get_french_month_name apru00e8s les imports
after_imports = """from datetime import datetime, date, timedelta
from decimal import Decimal

def get_french_month_name(month_number):
    """
    Retourne le nom du mois en franu00e7ais avec le bon encodage
    """
    french_months = {
        1: 'Janvier',
        2: 'Fu00e9vrier',
        3: 'Mars',
        4: 'Avril',
        5: 'Mai',
        6: 'Juin',
        7: 'Juillet',
        8: 'Aou00fbt',
        9: 'Septembre',
        10: 'Octobre',
        11: 'Novembre',
        12: 'Du00e9cembre'
    }
    return french_months.get(month_number, '')
"""

# Remplacer les imports existants par notre version augmentu00e9e
import_pattern = r'from datetime import datetime, date, timedelta\s*\nfrom decimal import Decimal'
if re.search(import_pattern, content):
    content = re.sub(import_pattern, after_imports, content)
else:
    # Si le pattern exact n'est pas trouvu00e9, ajouter la fonction apru00e8s les imports
    import_section_end = content.find('\n\n', content.find('import'))
    if import_section_end != -1:
        content = content[:import_section_end] + '\n' + after_imports + content[import_section_end:]

# Remplacer l'utilisation de calendar.month_name par notre fonction
month_pattern = r'calendar\.month_name\[([^\]]+)\]'
replacement = r'get_french_month_name(\1)'
content = re.sub(month_pattern, replacement, content)

# Remplacer u00e9galement la gu00e9nu00e9ration du mois dans le contexte du template
month_context_pattern = r'(mois = )([^\n]+)'

# Fonction pour remplacer le contexte du mois
def replace_month_context(match):
    prefix = match.group(1)
    month_expr = match.group(2)
    
    # Si c'est du00e9ju00e0 un appel u00e0 get_french_month_name, ne rien faire
    if 'get_french_month_name' in month_expr:
        return match.group(0)
    
    # Si c'est un numu00e9ro de mois simple, remplacer par notre fonction
    if month_expr.strip().isdigit() or month_expr.strip() == 'mois':
        return f"{prefix}get_french_month_name({month_expr.strip()})"
    
    return match.group(0)

# Chercher les endroits ou00f9 le mois est passu00e9 au contexte du template
releve_pattern = r'(\"mois\": )([^,\n]+)'
content = re.sub(releve_pattern, r'\1get_french_month_name(mois) + " " + str(annee)', content)

# u00c9crire le contenu modifiu00e9 dans le fichier
with open(file_path, 'w', encoding='utf-8') as file:
    file.write(content)

print("Correction de l'encodage des noms de mois terminu00e9e!")
