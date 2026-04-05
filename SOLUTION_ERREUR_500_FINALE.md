# 🔧 Solution Finale - Erreur 500 sur Achats Carburant

## 🔍 Diagnostic complet effectué

### ✅ Vérifications locales
- ✅ Modèles : Les méthodes `get_absolute_url()`, `get_update_url()`, `get_delete_url()` existent
- ✅ Vues : Les vues `achats_carburant_ht_list` et `achats_carburant_ttc_list` existent
- ✅ URLs : Les routes sont correctement configurées
- ✅ Templates : Les fichiers `list.html` et `list_base.html` existent
- ✅ Context processors : Le fichier `context_processors.py` est correct

### ❌ Problème identifié sur le serveur
- Le fichier `core/context_processors.py` **n'existe probablement PAS** sur le serveur
- OU le fichier `settings.py` sur le serveur ne contient pas les context processors

---

## 🎯 Solution

### Étape 1 : Vérifier si context_processors.py existe sur le serveur

```bash
ls -la core/context_processors.py
```

### Étape 2 : Si le fichier n'existe pas, le créer

```bash
cat > core/context_processors.py << 'EOF'
from django.conf import settings

def media_variables(request):
    """
    Ajoute les variables liées aux médias au contexte de tous les templates.
    """
    return {
        'MEDIA_URL': settings.MEDIA_URL,
        'STATIC_URL': settings.STATIC_URL,
    }
EOF
```

### Étape 3 : Vérifier settings.py sur le serveur

```bash
grep -A 10 "context_processors" fms/settings.py
```

Le résultat devrait contenir :
```python
'context_processors': [
    'django.template.context_processors.debug',
    'django.template.context_processors.request',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    'django.template.context_processors.media',
    'core.context_processors.media_variables',
],
```

### Étape 4 : Si la ligne manque, l'ajouter

```bash
nano fms/settings.py
```

Cherchez la section `TEMPLATES` et assurez-vous que `'core.context_processors.media_variables'` est présent.

### Étape 5 : Redémarrer l'application

```bash
mkdir -p tmp && touch tmp/restart.txt
sleep 5
```

---

## 🚀 Commandes complètes à exécuter

```bash
# 1. Vérifier si le fichier existe
ls -la core/context_processors.py

# 2. Si le fichier n'existe pas, le créer
cat > core/context_processors.py << 'EOF'
from django.conf import settings

def media_variables(request):
    """
    Ajoute les variables liées aux médias au contexte de tous les templates.
    """
    return {
        'MEDIA_URL': settings.MEDIA_URL,
        'STATIC_URL': settings.STATIC_URL,
    }
EOF

# 3. Vérifier les permissions
chmod 644 core/context_processors.py

# 4. Vérifier le contenu
cat core/context_processors.py

# 5. Redémarrer
mkdir -p tmp && touch tmp/restart.txt

# 6. Attendre
sleep 5

# 7. Tester
curl -I https://fms.undpciv.org/achats-carburant-ttc/
```

---

## 🆘 Solution alternative : Supprimer le context processor

Si le fichier ne peut pas être créé, modifiez `settings.py` pour retirer la référence :

```bash
nano fms/settings.py
```

Dans la section `TEMPLATES`, **supprimez** la ligne :
```python
'core.context_processors.media_variables',
```

Gardez seulement :
```python
'context_processors': [
    'django.template.context_processors.debug',
    'django.template.context_processors.request',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    'django.template.context_processors.media',
],
```

Puis redémarrez :
```bash
mkdir -p tmp && touch tmp/restart.txt
```

---

## 📋 Checklist

- [ ] Vérifier si `core/context_processors.py` existe
- [ ] Créer le fichier s'il n'existe pas
- [ ] Vérifier `settings.py` contient le context processor
- [ ] Redémarrer l'application
- [ ] Tester les pages

---

## 🎯 Résultat attendu

Après ces modifications :
- ✅ https://fms.undpciv.org/achats-carburant-ht/ fonctionne
- ✅ https://fms.undpciv.org/achats-carburant-ttc/ fonctionne
- ✅ Toutes les pages de liste fonctionnent
