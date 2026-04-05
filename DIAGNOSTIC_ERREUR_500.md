# 🔍 Diagnostic Erreur 500 - Achats Carburant HT

## ✅ Vérification effectuée

Le fichier `models.py` sur le serveur **contient déjà** les méthodes nécessaires :
- ✅ `get_absolute_url()` - ligne 357 (Achat_Stock_Carburant_HT)
- ✅ `get_update_url()` - ligne 362 (Achat_Stock_Carburant_HT)
- ✅ `get_delete_url()` - ligne 367 (Achat_Stock_Carburant_HT)
- ✅ `get_absolute_url()` - ligne 449 (Achat_Carburant_TTC)
- ✅ `get_update_url()` - ligne 454 (Achat_Carburant_TTC)
- ✅ `get_delete_url()` - ligne 459 (Achat_Carburant_TTC)

**Conclusion** : Le problème n'est PAS lié aux méthodes manquantes.

---

## 🔍 Causes possibles de l'erreur 500

### 1. **L'application n'a pas été redémarrée**
Les modifications du code Python nécessitent un redémarrage de l'application.

**Solution** :
```bash
mkdir -p tmp && touch tmp/restart.txt
```

### 2. **Erreur dans le template**
Le template `achats_carburant_ht/list.html` peut avoir une erreur.

**À vérifier** : Ligne 32 du template utilise `get_statut_display` qui est une méthode Django automatique pour les champs avec `choices`.

### 3. **Problème avec les context processors**
Le fichier `settings.py` doit avoir les context processors nécessaires.

### 4. **Erreur dans la vue**
La vue `achats_carburant_ht_list` peut avoir un problème.

### 5. **Base de données vide ou corrompue**
Il n'y a peut-être aucun achat dans la base de données.

---

## 🚀 Commandes de diagnostic à exécuter

### Sur le serveur (vous êtes déjà connecté)

#### 1. Redémarrer l'application
```bash
mkdir -p tmp && touch tmp/restart.txt
sleep 5
```

#### 2. Consulter les logs d'erreur
```bash
tail -50 debug.log
```

#### 3. Vérifier les logs en temps réel
```bash
tail -f debug.log
```
Puis dans votre navigateur, rechargez la page `/achats-carburant-ht/`
Vous verrez l'erreur exacte s'afficher dans le terminal.

#### 4. Vérifier si des achats existent dans la base
```bash
python manage.py shell
```
Puis dans le shell Python :
```python
from core.models import Achat_Stock_Carburant_HT
print(Achat_Stock_Carburant_HT.objects.count())
print(Achat_Stock_Carburant_HT.objects.all())
exit()
```

#### 5. Tester la vue directement
```bash
python manage.py shell
```
Puis :
```python
from core.views import achats_carburant_ht_list
from django.test import RequestFactory
from core.models import Utilisateur

factory = RequestFactory()
request = factory.get('/achats-carburant-ht/')
request.user = Utilisateur.objects.first()

try:
    response = achats_carburant_ht_list(request)
    print("Vue OK:", response.status_code)
except Exception as e:
    print("ERREUR:", str(e))
    import traceback
    traceback.print_exc()
exit()
```

---

## 📋 Checklist de vérification

- [ ] Application redémarrée (`touch tmp/restart.txt`)
- [ ] Logs consultés (`tail -50 debug.log`)
- [ ] Erreur exacte identifiée dans les logs
- [ ] Base de données contient des données
- [ ] Template existe et est correct
- [ ] Context processors configurés

---

## 🎯 Prochaines étapes

**ÉTAPE 1** : Redémarrez l'application
```bash
mkdir -p tmp && touch tmp/restart.txt
```

**ÉTAPE 2** : Attendez 5 secondes et testez
Rechargez https://fms.undpciv.org/achats-carburant-ht/

**ÉTAPE 3** : Si l'erreur persiste, consultez les logs
```bash
tail -50 debug.log
```

**ÉTAPE 4** : Partagez-moi le contenu des logs
Copiez les dernières lignes d'erreur et envoyez-les moi.

---

## 💡 Erreurs courantes et solutions

### Erreur : "No such table: core_achat_stock_carburant_ht"
**Cause** : Les migrations n'ont pas été appliquées
**Solution** :
```bash
python manage.py migrate
```

### Erreur : "TemplateDoesNotExist"
**Cause** : Le template n'existe pas ou n'est pas au bon endroit
**Solution** : Vérifier que `core/templates/core/achats_carburant_ht/list.html` existe

### Erreur : "AttributeError: 'Achat_Stock_Carburant_HT' object has no attribute..."
**Cause** : Une méthode ou propriété est appelée mais n'existe pas
**Solution** : Vérifier le template et le modèle

### Erreur : "ImportError" ou "ModuleNotFoundError"
**Cause** : Un module Python manquant
**Solution** : Installer les dépendances manquantes

---

## 📞 Que faire maintenant ?

**Option 1** : Redémarrez et testez
```bash
mkdir -p tmp && touch tmp/restart.txt
```
Puis testez la page.

**Option 2** : Consultez les logs et partagez-les moi
```bash
tail -50 debug.log
```
Copiez le résultat et envoyez-le moi.

**Option 3** : Testez en temps réel
```bash
tail -f debug.log
```
Rechargez la page et observez les erreurs qui s'affichent.

---

**Quelle option choisissez-vous ? 🚀**
