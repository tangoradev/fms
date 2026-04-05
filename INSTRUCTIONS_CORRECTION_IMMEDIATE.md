# 🚨 CORRECTION IMMÉDIATE - Erreur CSRF

## Problème identifié
Votre `settings.py` sur le serveur distant **manque la configuration `CSRF_TRUSTED_ORIGINS`** qui est **obligatoire** pour Django 4.x en production.

---

## ✅ Solution rapide (3 étapes)

### Étape 1: Connectez-vous au serveur
```bash
ssh votre_utilisateur@fms.undpciv.org
```

### Étape 2: Éditez le fichier settings.py
```bash
cd /chemin/vers/fms  # Adaptez le chemin
nano fms/settings.py
# ou
vi fms/settings.py
```

### Étape 3: Ajoutez ces lignes APRÈS `CSRF_COOKIE_SECURE = True`

Cherchez cette section dans votre fichier :
```python
# Sécurité supplémentaire en prod
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

Et ajoutez **JUSTE APRÈS** :
```python
# Configuration CSRF pour la production (OBLIGATOIRE pour Django 4.x)
CSRF_TRUSTED_ORIGINS = [
    'http://fms.undpciv.org',
    'https://fms.undpciv.org',
    'http://www.fms.undpciv.org',
    'https://www.fms.undpciv.org',
]

# Configuration supplémentaire des cookies CSRF
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'Lax'

# Configuration de l'authentification
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

# URL de base pour les liens dans les emails
BASE_URL = 'https://fms.undpciv.org'
```

**Sauvegardez le fichier** :
- Nano : `Ctrl+X`, puis `Y`, puis `Entrée`
- Vi : `Esc`, puis `:wq`, puis `Entrée`

---

## 🔄 Redémarrage de l'application

### Si vous utilisez Gunicorn avec systemd :
```bash
sudo systemctl restart gunicorn
sudo systemctl status gunicorn
```

### Si vous utilisez Apache :
```bash
sudo systemctl restart apache2
sudo systemctl status apache2
```

### Si vous utilisez un autre service :
```bash
# Trouvez le nom du service
sudo systemctl list-units | grep fms

# Redémarrez-le
sudo systemctl restart nom_du_service
```

---

## 🧪 Test

1. **Videz le cache de votre navigateur** (Ctrl + Shift + Delete)
2. Accédez à : https://fms.undpciv.org/login/
3. Essayez de vous connecter
4. ✅ L'erreur CSRF devrait disparaître !

---

## 📋 Fichiers de référence créés

J'ai créé 2 fichiers pour vous aider :

1. **`settings_production_patch.txt`** 
   - Contient uniquement les lignes à ajouter
   - Pratique pour copier-coller

2. **`settings_production_complet.py`**
   - Fichier settings.py complet avec toutes les corrections
   - Peut remplacer entièrement votre fichier actuel

---

## ⚠️ Notes importantes

### Différences entre votre settings.py actuel et local :

1. **Manque dans votre settings.py serveur** :
   - ❌ `CSRF_TRUSTED_ORIGINS` (CRITIQUE - cause l'erreur)
   - ❌ Context processors pour les médias
   - ❌ Configuration de logging
   - ❌ LOGIN_URL, LOGIN_REDIRECT_URL

2. **Différences de configuration** :
   - ✅ Vous utilisez MySQL (bien)
   - ✅ DEBUG = False (bien)
   - ✅ WhiteNoise configuré (bien)
   - ✅ CSRF_COOKIE_SECURE = True (bien pour HTTPS)

---

## 🆘 Si le problème persiste

### Vérification 1 : Confirmez que la modification est bien prise en compte
```bash
grep "CSRF_TRUSTED_ORIGINS" /chemin/vers/fms/fms/settings.py
```
Devrait afficher la liste des origines.

### Vérification 2 : Consultez les logs
```bash
# Logs Django
tail -50 /chemin/vers/fms/debug.log

# Logs du serveur web
sudo tail -50 /var/log/apache2/error.log
# ou
sudo tail -50 /var/log/nginx/error.log
```

### Vérification 3 : Vérifiez que le service a bien redémarré
```bash
sudo systemctl status gunicorn
# ou
sudo systemctl status apache2
```

### Vérification 4 : Testez avec curl
```bash
curl -I https://fms.undpciv.org/login/
```
Devrait retourner un code 200.

---

## 📞 Besoin d'aide ?

Si vous rencontrez des difficultés :

1. **Partagez les logs d'erreur** :
   ```bash
   tail -100 /chemin/vers/fms/debug.log
   ```

2. **Vérifiez la configuration du serveur web** (Nginx/Apache)

3. **Assurez-vous que le fichier base.html contient** :
   ```html
   <meta name="csrf-token" content="{{ csrf_token }}">
   ```

---

## ✨ Après la correction

Une fois que tout fonctionne :

1. ✅ Testez toutes les fonctionnalités principales
2. ✅ Vérifiez que les formulaires fonctionnent
3. ✅ Testez les demandes de carburant
4. ✅ Testez les demandes de courses
5. ✅ Vérifiez les uploads de fichiers

---

## 🎯 Résumé en 1 minute

```bash
# 1. Connexion
ssh user@fms.undpciv.org

# 2. Édition
nano /chemin/vers/fms/fms/settings.py

# 3. Ajoutez après CSRF_COOKIE_SECURE = True :
CSRF_TRUSTED_ORIGINS = [
    'http://fms.undpciv.org',
    'https://fms.undpciv.org',
    'http://www.fms.undpciv.org',
    'https://www.fms.undpciv.org',
]

# 4. Sauvegardez (Ctrl+X, Y, Entrée)

# 5. Redémarrez
sudo systemctl restart gunicorn

# 6. Testez
# Videz cache navigateur + https://fms.undpciv.org/login/
```

**C'est tout ! 🎉**
