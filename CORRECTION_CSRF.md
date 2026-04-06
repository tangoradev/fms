# Correction de l'erreur CSRF en production

## Problème identifié
L'erreur "La vérification CSRF a échoué. La requête a été interrompue." se produit car Django ne reconnaît pas le domaine `fms.undpciv.org` comme une origine de confiance.

## Modifications apportées

### 1. Fichier `fms/settings.py`

#### a) Ajout du domaine dans ALLOWED_HOSTS (ligne 29)
```python
ALLOWED_HOSTS = ['127.0.0.1', '10.20.160.77', 'localhost', 'fms.undpciv.org', 'www.fms.undpciv.org']
```

#### b) Ajout des configurations CSRF (après ligne 150)
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

### 2. Fichier `core/templates/core/base.html`

#### Ajout du meta tag CSRF dans le <head> (ligne 6)
```html
<meta name="csrf-token" content="{{ csrf_token }}">
```

## Étapes de déploiement sur le serveur distant

### 1. Transférer les fichiers modifiés
```bash
# Depuis votre machine locale, transférez les fichiers vers le serveur
scp fms/settings.py utilisateur@fms.undpciv.org:/chemin/vers/fms/fms/settings.py
scp core/templates/core/base.html utilisateur@fms.undpciv.org:/chemin/vers/fms/core/templates/core/base.html
```

### 2. Sur le serveur distant, redémarrer l'application

#### Si vous utilisez Gunicorn avec systemd:
```bash
sudo systemctl restart gunicorn
# ou
sudo systemctl restart fms
```

#### Si vous utilisez Apache avec mod_wsgi:
```bash
sudo systemctl restart apache2
```

#### Si vous utilisez Nginx + Gunicorn:
```bash
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

### 3. Vider le cache du navigateur
Après le redémarrage, demandez aux utilisateurs de:
- Vider le cache du navigateur (Ctrl + Shift + Delete)
- Ou utiliser le mode navigation privée pour tester

### 4. Tester la connexion
1. Accédez à `http://fms.undpciv.org/login/`
2. Essayez de vous connecter
3. L'erreur CSRF ne devrait plus apparaître

## Si le problème persiste

### Vérification 1: Vérifier que les modifications sont bien déployées
```bash
# Sur le serveur, vérifiez le contenu de settings.py
grep "CSRF_TRUSTED_ORIGINS" /chemin/vers/fms/fms/settings.py
```

### Vérification 2: Vérifier les logs
```bash
# Consultez les logs de l'application
tail -f /chemin/vers/fms/debug.log

# Ou les logs du serveur web
sudo tail -f /var/log/nginx/error.log
# ou
sudo tail -f /var/log/apache2/error.log
```

### Vérification 3: Si vous utilisez HTTPS
Si votre site utilise HTTPS (https://fms.undpciv.org), modifiez dans settings.py:
```python
CSRF_COOKIE_SECURE = True  # Au lieu de False
SESSION_COOKIE_SECURE = True  # Ajoutez cette ligne également
```

### Vérification 4: Vérifier la configuration du proxy inverse
Si vous utilisez Nginx ou Apache comme proxy inverse, assurez-vous que les headers sont correctement transmis:

#### Pour Nginx:
```nginx
location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

#### Pour Apache:
```apache
ProxyPass / http://127.0.0.1:8000/
ProxyPassReverse / http://127.0.0.1:8000/
ProxyPreserveHost On
RequestHeader set X-Forwarded-Proto "http"
```

## Notes importantes

1. **Sécurité**: En production, il est recommandé d'utiliser HTTPS et de définir `CSRF_COOKIE_SECURE = True`
2. **DEBUG**: Pensez à mettre `DEBUG = False` en production après avoir résolu tous les problèmes
3. **SECRET_KEY**: Changez la SECRET_KEY en production et ne la partagez jamais

## Support
Si le problème persiste après ces modifications, vérifiez:
- Les logs d'erreur du serveur web
- Les logs de l'application Django (debug.log)
- La configuration du pare-feu
- Les permissions des fichiers
- fin
