# Guide de déploiement manuel - Correction CSRF

## Méthode 1: Déploiement via script automatique

### Sur Windows (PowerShell)
1. Ouvrez PowerShell en tant qu'administrateur
2. Naviguez vers le dossier du projet:
   ```powershell
   cd d:\fms
   ```
3. Modifiez le script `deploy_csrf_fix.ps1` et configurez:
   - `$SERVER_USER` : votre nom d'utilisateur SSH
   - `$SERVER_HOST` : fms.undpciv.org
   - `$SERVER_PATH` : le chemin complet vers FMS sur le serveur
4. Exécutez le script:
   ```powershell
   .\deploy_csrf_fix.ps1
   ```

### Sur Linux/Mac (Bash)
1. Ouvrez un terminal
2. Naviguez vers le dossier du projet:
   ```bash
   cd /chemin/vers/fms
   ```
3. Rendez le script exécutable:
   ```bash
   chmod +x deploy_csrf_fix.sh
   ```
4. Modifiez le script et configurez les variables
5. Exécutez le script:
   ```bash
   ./deploy_csrf_fix.sh
   ```

---

## Méthode 2: Déploiement manuel pas à pas

### Étape 1: Connexion au serveur
```bash
ssh votre_utilisateur@fms.undpciv.org
```

### Étape 2: Localiser le projet FMS
```bash
# Trouvez où est installé FMS (exemples courants)
cd /var/www/fms
# ou
cd /home/utilisateur/fms
# ou
cd /opt/fms
```

### Étape 3: Sauvegarder les fichiers actuels
```bash
# Créer un dossier de sauvegarde
mkdir -p backups/$(date +%Y%m%d_%H%M%S)

# Sauvegarder settings.py
cp fms/settings.py backups/$(date +%Y%m%d_%H%M%S)/settings.py.backup

# Sauvegarder base.html
cp core/templates/core/base.html backups/$(date +%Y%m%d_%H%M%S)/base.html.backup
```

### Étape 4: Modifier settings.py
```bash
nano fms/settings.py
# ou
vi fms/settings.py
```

**Modifications à apporter:**

1. Ligne 29 - Modifier `ALLOWED_HOSTS`:
```python
ALLOWED_HOSTS = ['127.0.0.1', '10.20.160.77', 'localhost', 'fms.undpciv.org', 'www.fms.undpciv.org']
```

2. Après la ligne 150 (après `BASE_URL`), ajouter:
```python
# Configuration CSRF pour la production
CSRF_TRUSTED_ORIGINS = [
    'http://fms.undpciv.org',
    'https://fms.undpciv.org',
    'http://www.fms.undpciv.org',
    'https://www.fms.undpciv.org',
    'http://10.20.160.77:8000',
]

# Configuration des cookies CSRF
CSRF_COOKIE_SECURE = False  # Mettre True si vous utilisez HTTPS
CSRF_COOKIE_HTTPONLY = False  # Doit être False pour que JavaScript puisse accéder au token
CSRF_COOKIE_SAMESITE = 'Lax'  # Protection contre les attaques CSRF cross-site
```

Sauvegarder et quitter (Ctrl+X puis Y pour nano, :wq pour vi)

### Étape 5: Modifier base.html
```bash
nano core/templates/core/base.html
# ou
vi core/templates/core/base.html
```

**Modification à apporter:**

Dans la section `<head>`, après la ligne 5, ajouter:
```html
<meta name="csrf-token" content="{{ csrf_token }}">
```

Le `<head>` devrait ressembler à:
```html
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="csrf-token" content="{{ csrf_token }}">
    <title>{% block title %}FMS - Système de Gestion de Flotte{% endblock %}</title>
    ...
```

Sauvegarder et quitter

### Étape 6: Redémarrer l'application

#### Si vous utilisez Gunicorn:
```bash
sudo systemctl restart gunicorn
# Vérifier le statut
sudo systemctl status gunicorn
```

#### Si vous utilisez Apache:
```bash
sudo systemctl restart apache2
# Vérifier le statut
sudo systemctl status apache2
```

#### Si vous utilisez Nginx + Gunicorn:
```bash
sudo systemctl restart gunicorn
sudo systemctl restart nginx
# Vérifier les statuts
sudo systemctl status gunicorn
sudo systemctl status nginx
```

### Étape 7: Vérifier les logs
```bash
# Logs de l'application Django
tail -f debug.log

# Logs du serveur web (selon votre configuration)
sudo tail -f /var/log/nginx/error.log
# ou
sudo tail -f /var/log/apache2/error.log
```

### Étape 8: Tester
1. Ouvrez votre navigateur
2. Videz le cache (Ctrl + Shift + Delete)
3. Accédez à http://fms.undpciv.org/login/
4. Essayez de vous connecter

---

## Méthode 3: Déploiement via FTP/SFTP (si pas d'accès SSH)

### Avec FileZilla ou WinSCP:

1. **Télécharger les fichiers actuels du serveur** (sauvegarde):
   - `fms/settings.py` → sauvegarder sur votre PC
   - `core/templates/core/base.html` → sauvegarder sur votre PC

2. **Modifier les fichiers localement**:
   - Ouvrez `d:\fms\fms\settings.py` avec un éditeur de texte
   - Appliquez les modifications décrites dans l'Étape 4 ci-dessus
   - Ouvrez `d:\fms\core\templates\core\base.html`
   - Appliquez les modifications décrites dans l'Étape 5 ci-dessus

3. **Uploader les fichiers modifiés**:
   - Uploadez `fms/settings.py` vers le serveur
   - Uploadez `core/templates/core/base.html` vers le serveur

4. **Redémarrer l'application**:
   - Via le panneau de contrôle de votre hébergeur
   - Ou contactez votre administrateur système

---

## Vérification après déploiement

### Checklist:
- [ ] Les fichiers ont été sauvegardés
- [ ] `settings.py` a été modifié avec les bonnes valeurs
- [ ] `base.html` contient le meta tag CSRF
- [ ] L'application a été redémarrée
- [ ] Le cache du navigateur a été vidé
- [ ] La page de login s'affiche sans erreur CSRF
- [ ] La connexion fonctionne

### En cas de problème:

1. **Restaurer les sauvegardes**:
```bash
cp backups/YYYYMMDD_HHMMSS/settings.py.backup fms/settings.py
cp backups/YYYYMMDD_HHMMSS/base.html.backup core/templates/core/base.html
sudo systemctl restart gunicorn  # ou apache2
```

2. **Consulter les logs**:
```bash
tail -100 debug.log
```

3. **Vérifier la configuration**:
```bash
# Vérifier que les modifications sont présentes
grep "CSRF_TRUSTED_ORIGINS" fms/settings.py
grep "csrf-token" core/templates/core/base.html
```

---

## Support

Si le problème persiste après avoir suivi toutes ces étapes:

1. Consultez le fichier `CORRECTION_CSRF.md` pour plus de détails
2. Vérifiez les logs d'erreur
3. Assurez-vous que le serveur web transmet correctement les headers
4. Vérifiez que le pare-feu n'interfère pas

## Notes importantes

- ⚠️ Si vous utilisez HTTPS, changez `CSRF_COOKIE_SECURE = True`
- ⚠️ En production, mettez `DEBUG = False` après avoir résolu tous les problèmes
- ⚠️ Changez la `SECRET_KEY` en production
