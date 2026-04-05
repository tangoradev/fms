#!/usr/bin/env python3
"""
Script de vérification de la configuration CSRF pour FMS
Usage: python verifier_config_csrf.py [chemin_vers_settings.py]
"""

import sys
import re
from pathlib import Path

def verifier_settings(fichier_path):
    """Vérifie la configuration CSRF dans settings.py"""
    
    print("=" * 60)
    print("VÉRIFICATION DE LA CONFIGURATION CSRF")
    print("=" * 60)
    print(f"\nFichier analysé : {fichier_path}")
    print("-" * 60)
    
    try:
        with open(fichier_path, 'r', encoding='utf-8') as f:
            contenu = f.read()
    except FileNotFoundError:
        print(f"❌ ERREUR : Fichier non trouvé : {fichier_path}")
        return False
    except Exception as e:
        print(f"❌ ERREUR : Impossible de lire le fichier : {e}")
        return False
    
    erreurs = []
    avertissements = []
    succes = []
    
    # Vérification 1 : ALLOWED_HOSTS
    print("\n1. Vérification ALLOWED_HOSTS...")
    if "ALLOWED_HOSTS" in contenu:
        if "fms.undpciv.org" in contenu:
            succes.append("✅ fms.undpciv.org présent dans ALLOWED_HOSTS")
        else:
            erreurs.append("❌ fms.undpciv.org MANQUANT dans ALLOWED_HOSTS")
    else:
        erreurs.append("❌ ALLOWED_HOSTS non trouvé")
    
    # Vérification 2 : CSRF_TRUSTED_ORIGINS (CRITIQUE)
    print("2. Vérification CSRF_TRUSTED_ORIGINS...")
    if "CSRF_TRUSTED_ORIGINS" in contenu:
        succes.append("✅ CSRF_TRUSTED_ORIGINS présent")
        
        # Vérifier les domaines
        if "fms.undpciv.org" in contenu:
            succes.append("✅ fms.undpciv.org dans CSRF_TRUSTED_ORIGINS")
        else:
            erreurs.append("❌ fms.undpciv.org MANQUANT dans CSRF_TRUSTED_ORIGINS")
    else:
        erreurs.append("❌ CSRF_TRUSTED_ORIGINS MANQUANT (CRITIQUE !)")
    
    # Vérification 3 : CSRF_COOKIE_SECURE
    print("3. Vérification CSRF_COOKIE_SECURE...")
    if re.search(r'CSRF_COOKIE_SECURE\s*=\s*True', contenu):
        succes.append("✅ CSRF_COOKIE_SECURE = True (bon pour HTTPS)")
    elif re.search(r'CSRF_COOKIE_SECURE\s*=\s*False', contenu):
        avertissements.append("⚠️  CSRF_COOKIE_SECURE = False (mettre True si HTTPS)")
    else:
        avertissements.append("⚠️  CSRF_COOKIE_SECURE non défini")
    
    # Vérification 4 : CSRF_COOKIE_HTTPONLY
    print("4. Vérification CSRF_COOKIE_HTTPONLY...")
    if "CSRF_COOKIE_HTTPONLY" in contenu:
        if re.search(r'CSRF_COOKIE_HTTPONLY\s*=\s*False', contenu):
            succes.append("✅ CSRF_COOKIE_HTTPONLY = False (permet accès JavaScript)")
        else:
            avertissements.append("⚠️  CSRF_COOKIE_HTTPONLY = True (peut bloquer certaines fonctionnalités)")
    else:
        avertissements.append("⚠️  CSRF_COOKIE_HTTPONLY non défini")
    
    # Vérification 5 : CSRF_COOKIE_SAMESITE
    print("5. Vérification CSRF_COOKIE_SAMESITE...")
    if "CSRF_COOKIE_SAMESITE" in contenu:
        succes.append("✅ CSRF_COOKIE_SAMESITE défini")
    else:
        avertissements.append("⚠️  CSRF_COOKIE_SAMESITE non défini")
    
    # Vérification 6 : DEBUG
    print("6. Vérification DEBUG...")
    if re.search(r'DEBUG\s*=\s*False', contenu):
        succes.append("✅ DEBUG = False (bon pour production)")
    elif re.search(r'DEBUG\s*=\s*True', contenu):
        avertissements.append("⚠️  DEBUG = True (à désactiver en production)")
    
    # Vérification 7 : SESSION_COOKIE_SECURE
    print("7. Vérification SESSION_COOKIE_SECURE...")
    if re.search(r'SESSION_COOKIE_SECURE\s*=\s*True', contenu):
        succes.append("✅ SESSION_COOKIE_SECURE = True (bon pour HTTPS)")
    else:
        avertissements.append("⚠️  SESSION_COOKIE_SECURE non défini ou False")
    
    # Affichage des résultats
    print("\n" + "=" * 60)
    print("RÉSULTATS DE LA VÉRIFICATION")
    print("=" * 60)
    
    if succes:
        print("\n✅ SUCCÈS :")
        for s in succes:
            print(f"   {s}")
    
    if avertissements:
        print("\n⚠️  AVERTISSEMENTS :")
        for a in avertissements:
            print(f"   {a}")
    
    if erreurs:
        print("\n❌ ERREURS CRITIQUES :")
        for e in erreurs:
            print(f"   {e}")
    
    print("\n" + "=" * 60)
    
    if erreurs:
        print("❌ STATUT : CONFIGURATION INCORRECTE")
        print("\n🔧 ACTIONS REQUISES :")
        print("   1. Ajoutez CSRF_TRUSTED_ORIGINS dans settings.py")
        print("   2. Redémarrez l'application")
        print("   3. Testez la connexion")
        print("\n📖 Consultez INSTRUCTIONS_CORRECTION_IMMEDIATE.md pour les détails")
        return False
    elif avertissements:
        print("⚠️  STATUT : CONFIGURATION FONCTIONNELLE MAIS PEUT ÊTRE AMÉLIORÉE")
        print("\n💡 RECOMMANDATIONS :")
        for a in avertissements:
            print(f"   - {a}")
        return True
    else:
        print("✅ STATUT : CONFIGURATION PARFAITE !")
        return True
    
    print("=" * 60)

def main():
    """Point d'entrée du script"""
    
    if len(sys.argv) > 1:
        fichier = sys.argv[1]
    else:
        # Chercher settings.py dans le répertoire courant
        fichier = Path("fms/settings.py")
        if not fichier.exists():
            fichier = Path("settings.py")
        if not fichier.exists():
            print("❌ ERREUR : Fichier settings.py non trouvé")
            print("\nUsage : python verifier_config_csrf.py [chemin_vers_settings.py]")
            print("\nExemples :")
            print("  python verifier_config_csrf.py fms/settings.py")
            print("  python verifier_config_csrf.py /var/www/fms/fms/settings.py")
            sys.exit(1)
    
    resultat = verifier_settings(fichier)
    sys.exit(0 if resultat else 1)

if __name__ == "__main__":
    main()
