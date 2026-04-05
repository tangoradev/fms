#!/bin/bash

# Script de déploiement de la correction CSRF
# Usage: ./deploy_csrf_fix.sh

echo "=========================================="
echo "Déploiement de la correction CSRF pour FMS"
echo "=========================================="
echo ""

# Variables à configurer
SERVER_USER="votre_utilisateur"
SERVER_HOST="fms.undpciv.org"
SERVER_PATH="/chemin/vers/fms"

# Couleurs pour les messages
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Configuration actuelle:${NC}"
echo "  Utilisateur: $SERVER_USER"
echo "  Serveur: $SERVER_HOST"
echo "  Chemin: $SERVER_PATH"
echo ""

read -p "Voulez-vous continuer avec cette configuration? (o/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Oo]$ ]]
then
    echo -e "${RED}Déploiement annulé.${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Étape 1: Sauvegarde des fichiers actuels sur le serveur...${NC}"
ssh $SERVER_USER@$SERVER_HOST "cp $SERVER_PATH/fms/settings.py $SERVER_PATH/fms/settings.py.backup.$(date +%Y%m%d_%H%M%S)"
ssh $SERVER_USER@$SERVER_HOST "cp $SERVER_PATH/core/templates/core/base.html $SERVER_PATH/core/templates/core/base.html.backup.$(date +%Y%m%d_%H%M%S)"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Sauvegarde réussie${NC}"
else
    echo -e "${RED}✗ Erreur lors de la sauvegarde${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Étape 2: Transfert des fichiers modifiés...${NC}"

# Transfert de settings.py
scp fms/settings.py $SERVER_USER@$SERVER_HOST:$SERVER_PATH/fms/settings.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ settings.py transféré${NC}"
else
    echo -e "${RED}✗ Erreur lors du transfert de settings.py${NC}"
    exit 1
fi

# Transfert de base.html
scp core/templates/core/base.html $SERVER_USER@$SERVER_HOST:$SERVER_PATH/core/templates/core/base.html
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ base.html transféré${NC}"
else
    echo -e "${RED}✗ Erreur lors du transfert de base.html${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Étape 3: Redémarrage de l'application...${NC}"

# Détection du type de serveur et redémarrage
ssh $SERVER_USER@$SERVER_HOST << 'EOF'
if systemctl is-active --quiet gunicorn; then
    echo "Redémarrage de Gunicorn..."
    sudo systemctl restart gunicorn
elif systemctl is-active --quiet apache2; then
    echo "Redémarrage d'Apache..."
    sudo systemctl restart apache2
elif systemctl is-active --quiet nginx; then
    echo "Redémarrage de Nginx..."
    sudo systemctl restart nginx
else
    echo "Serveur web non détecté. Veuillez redémarrer manuellement."
fi
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Application redémarrée${NC}"
else
    echo -e "${RED}✗ Erreur lors du redémarrage${NC}"
    echo -e "${YELLOW}Veuillez redémarrer manuellement l'application${NC}"
fi

echo ""
echo -e "${GREEN}=========================================="
echo "Déploiement terminé !"
echo "==========================================${NC}"
echo ""
echo -e "${YELLOW}Prochaines étapes:${NC}"
echo "1. Testez la connexion sur http://fms.undpciv.org/login/"
echo "2. Videz le cache de votre navigateur (Ctrl + Shift + Delete)"
echo "3. Si le problème persiste, consultez le fichier CORRECTION_CSRF.md"
echo ""
echo -e "${YELLOW}Pour consulter les logs:${NC}"
echo "  ssh $SERVER_USER@$SERVER_HOST 'tail -f $SERVER_PATH/debug.log'"
echo ""
