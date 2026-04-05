#!/bin/bash
# Commandes à exécuter sur le serveur mutualisé
# Copiez-collez ces commandes une par une dans votre terminal

# 1. Vérifier que vous êtes dans le bon répertoire
pwd
# Devrait afficher: /home/c2501100c/fms

# 2. Sauvegarder le fichier actuel
echo "Sauvegarde de settings.py..."
cp fms/settings.py fms/settings.py.backup.$(date +%Y%m%d_%H%M%S)
echo "✓ Sauvegarde créée"

# 3. Vérifier la sauvegarde
ls -lh fms/settings.py.backup.*
echo "✓ Fichier sauvegardé"

# 4. Éditer le fichier (cette commande ouvrira nano)
echo "Ouverture de l'éditeur..."
nano fms/settings.py

# Après avoir modifié et sauvegardé le fichier avec nano:

# 5. Vérifier que la modification est présente
echo "Vérification de la modification..."
grep -A 5 "CSRF_TRUSTED_ORIGINS" fms/settings.py

# 6. Créer le répertoire tmp s'il n'existe pas
mkdir -p tmp

# 7. Redémarrer l'application Passenger
echo "Redémarrage de l'application..."
touch tmp/restart.txt
echo "✓ Application redémarrée"

# 8. Vérifier le fichier restart.txt
ls -lh tmp/restart.txt

# 9. Attendre quelques secondes
echo "Attente du redémarrage..."
sleep 5

# 10. Vérifier les logs
echo "Vérification des logs..."
tail -20 debug.log

echo ""
echo "✅ Correction appliquée !"
echo "Testez maintenant sur https://fms.undpciv.org/login/"
echo "N'oubliez pas de vider le cache de votre navigateur !"
