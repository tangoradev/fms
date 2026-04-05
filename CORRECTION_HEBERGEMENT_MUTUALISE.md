# 🔧 Correction CSRF - Hébergement Mutualisé

## Informations détectées
- **Utilisateur**: c2501100c
- **Serveur**: web57
- **Environnement virtuel**: Python 3.11
- **Chemin projet**: /home/c2501100c/fms
- **Type**: Hébergement mutualisé (pas de systemctl)

---

## 📝 Commandes à exécuter

### Étape 1: Sauvegarde du fichier actuel
```bash
cp fms/settings.py fms/settings.py.backup.$(date +%Y%m%d_%H%M%S)
```

### Étape 2: Édition du fichier settings.py
```bash
nano fms/settings.py
```

### Étape 3: Localiser et modifier
Cherchez cette section (vers la fin du fichier) :
```python
# Sécurité supplémentaire en prod
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Pour WhiteNoise (servir les fichiers statiques)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### Étape 4: Ajouter APRÈS CSRF_COOKIE_SECURE = True
Insérez ces lignes :
```python

# Configuration CSRF pour Django 4.x (OBLIGATOIRE)
CSRF_TRUSTED_ORIGINS = [
    'http://fms.undpciv.org',
    'https://fms.undpciv.org',
    'http://www.fms.undpciv.org',
    'https://www.fms.undpciv.org',
]

# Configuration supplémentaire CSRF
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'Lax'

# Configuration de l'authentification
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

# URL de base pour les emails
BASE_URL = 'https://fms.undpciv.org'

# Configuration du logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/home/c2501100c/fms/debug.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'core': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

### Étape 5: Sauvegarder
- Appuyez sur `Ctrl+X`
- Tapez `Y` (pour Yes)
- Appuyez sur `Entrée`

### Étape 6: Vérifier la modification
```bash
grep "CSRF_TRUSTED_ORIGINS" fms/settings.py
```
Devrait afficher la liste des domaines.

### Étape 7: Redémarrer l'application (hébergement mutualisé)
```bash
# Méthode 1: Via le fichier passenger_wsgi.py
touch tmp/restart.txt

# OU Méthode 2: Redémarrer Passenger
mkdir -p tmp
touch tmp/restart.txt

# OU Méthode 3: Si vous avez accès au panneau de contrôle
# Allez dans cPanel → Application Python → Restart
```

### Étape 8: Vérifier les logs
```bash
tail -50 debug.log
```

---

## ✅ Vérification finale

1. Videz le cache du navigateur (Ctrl + Shift + Delete)
2. Accédez à https://fms.undpciv.org/login/
3. Essayez de vous connecter
4. L'erreur CSRF devrait disparaître !

---

## 🆘 Si le problème persiste

### Vérifier que Passenger a redémarré :
```bash
ls -la tmp/restart.txt
```
Le fichier doit exister et avoir une date/heure récente.

### Forcer un redémarrage complet :
```bash
rm -f tmp/restart.txt
touch tmp/restart.txt
```

### Consulter les logs d'erreur :
```bash
tail -100 debug.log
# ou
tail -100 logs/error.log
```

---

## 📌 Notes spécifiques hébergement mutualisé

- Pas d'accès à `systemctl` (normal)
- Utiliser `touch tmp/restart.txt` pour redémarrer
- Les logs sont dans le répertoire du projet
- Passenger redémarre automatiquement après modification de restart.txt
