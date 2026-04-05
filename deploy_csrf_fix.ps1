# Script PowerShell de déploiement de la correction CSRF
# Usage: .\deploy_csrf_fix.ps1

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Déploiement de la correction CSRF pour FMS" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Variables à configurer
$SERVER_USER = "votre_utilisateur"
$SERVER_HOST = "fms.undpciv.org"
$SERVER_PATH = "/chemin/vers/fms"

Write-Host "Configuration actuelle:" -ForegroundColor Yellow
Write-Host "  Utilisateur: $SERVER_USER"
Write-Host "  Serveur: $SERVER_HOST"
Write-Host "  Chemin: $SERVER_PATH"
Write-Host ""

$confirmation = Read-Host "Voulez-vous continuer avec cette configuration? (o/n)"
if ($confirmation -ne 'o' -and $confirmation -ne 'O') {
    Write-Host "Déploiement annulé." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Étape 1: Sauvegarde des fichiers actuels sur le serveur..." -ForegroundColor Yellow

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$sshCommand1 = "cp $SERVER_PATH/fms/settings.py $SERVER_PATH/fms/settings.py.backup.$timestamp"
$sshCommand2 = "cp $SERVER_PATH/core/templates/core/base.html $SERVER_PATH/core/templates/core/base.html.backup.$timestamp"

ssh "$SERVER_USER@$SERVER_HOST" $sshCommand1
ssh "$SERVER_USER@$SERVER_HOST" $sshCommand2

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Sauvegarde réussie" -ForegroundColor Green
} else {
    Write-Host "✗ Erreur lors de la sauvegarde" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Étape 2: Transfert des fichiers modifiés..." -ForegroundColor Yellow

# Transfert de settings.py
scp "fms/settings.py" "${SERVER_USER}@${SERVER_HOST}:${SERVER_PATH}/fms/settings.py"
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ settings.py transféré" -ForegroundColor Green
} else {
    Write-Host "✗ Erreur lors du transfert de settings.py" -ForegroundColor Red
    exit 1
}

# Transfert de base.html
scp "core/templates/core/base.html" "${SERVER_USER}@${SERVER_HOST}:${SERVER_PATH}/core/templates/core/base.html"
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ base.html transféré" -ForegroundColor Green
} else {
    Write-Host "✗ Erreur lors du transfert de base.html" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Étape 3: Redémarrage de l'application..." -ForegroundColor Yellow

$restartScript = @"
if systemctl is-active --quiet gunicorn; then
    echo 'Redémarrage de Gunicorn...'
    sudo systemctl restart gunicorn
elif systemctl is-active --quiet apache2; then
    echo 'Redémarrage d Apache...'
    sudo systemctl restart apache2
elif systemctl is-active --quiet nginx; then
    echo 'Redémarrage de Nginx...'
    sudo systemctl restart nginx
else
    echo 'Serveur web non détecté. Veuillez redémarrer manuellement.'
fi
"@

ssh "$SERVER_USER@$SERVER_HOST" $restartScript

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Application redémarrée" -ForegroundColor Green
} else {
    Write-Host "✗ Erreur lors du redémarrage" -ForegroundColor Red
    Write-Host "Veuillez redémarrer manuellement l'application" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "Déploiement terminé !" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Prochaines étapes:" -ForegroundColor Yellow
Write-Host "1. Testez la connexion sur http://fms.undpciv.org/login/"
Write-Host "2. Videz le cache de votre navigateur (Ctrl + Shift + Delete)"
Write-Host "3. Si le problème persiste, consultez le fichier CORRECTION_CSRF.md"
Write-Host ""
Write-Host "Pour consulter les logs:" -ForegroundColor Yellow
Write-Host "  ssh $SERVER_USER@$SERVER_HOST 'tail -f $SERVER_PATH/debug.log'"
Write-Host ""
