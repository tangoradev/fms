# 🔧 Correction Erreur 500 - Page Achats Carburant HT

## 🐛 Problème identifié

**Erreur**: Server Error (500) sur https://fms.undpciv.org/achats-carburant-ht/

**Cause**: Les modèles `Achat_Stock_Carburant_HT` et `Achat_Carburant_TTC` n'ont pas les méthodes nécessaires que les templates essaient d'utiliser :
- `get_absolute_url()` - Pour le lien "Voir"
- `get_update_url()` - Pour le lien "Modifier"  
- `get_delete_url()` - Pour le lien "Supprimer"

---

## ✅ Solution appliquée

### Modifications dans `core/models.py`

#### 1. Modèle `Achat_Stock_Carburant_HT` (lignes 357-370)

Ajout de 3 méthodes après `format_solde_theorique()` :

```python
def get_absolute_url(self):
    """Retourne l'URL de la page de détail de l'achat carburant HT"""
    from django.urls import reverse
    return reverse('achat_carburant_ht_detail', args=[str(self.id_achat_stock_carburant_ht)])

def get_update_url(self):
    """Retourne l'URL de la page de modification de l'achat carburant HT"""
    from django.urls import reverse
    return reverse('achat_carburant_ht_update', args=[str(self.id_achat_stock_carburant_ht)])

def get_delete_url(self):
    """Retourne l'URL de la page de suppression de l'achat carburant HT"""
    from django.urls import reverse
    return reverse('achat_carburant_ht_delete', args=[str(self.id_achat_stock_carburant_ht)])
```

#### 2. Modèle `Achat_Carburant_TTC` (lignes 449-462)

Ajout des mêmes 3 méthodes après `format_solde_theorique()` :

```python
def get_absolute_url(self):
    """Retourne l'URL de la page de détail de l'achat carburant TTC"""
    from django.urls import reverse
    return reverse('achat_carburant_ttc_detail', args=[str(self.id_achat_carburant_ttc)])

def get_update_url(self):
    """Retourne l'URL de la page de modification de l'achat carburant TTC"""
    from django.urls import reverse
    return reverse('achat_carburant_ttc_update', args=[str(self.id_achat_carburant_ttc)])

def get_delete_url(self):
    """Retourne l'URL de la page de suppression de l'achat carburant TTC"""
    from django.urls import reverse
    return reverse('achat_carburant_ttc_delete', args=[str(self.id_achat_carburant_ttc)])
```

---

## 🚀 Déploiement sur le serveur

### Étape 1: Connexion au serveur
```bash
ssh c2501100c@web57.undpciv.org
```

### Étape 2: Activation de l'environnement virtuel
```bash
source /home/c2501100c/virtualenv/fms/3.11/bin/activate && cd /home/c2501100c/fms
```

### Étape 3: Sauvegarde du fichier actuel
```bash
cp core/models.py core/models.py.backup.$(date +%Y%m%d_%H%M%S)
```

### Étape 4: Transfert du fichier corrigé

**Depuis votre machine locale** (dans un nouveau terminal) :
```bash
scp d:\fms\core\models.py c2501100c@web57.undpciv.org:/home/c2501100c/fms/core/models.py
```

**OU** éditer manuellement sur le serveur :
```bash
nano core/models.py
```

Puis ajoutez les méthodes comme indiqué ci-dessus.

### Étape 5: Redémarrage de l'application
```bash
mkdir -p tmp && touch tmp/restart.txt
```

### Étape 6: Vérification
```bash
# Attendre 5 secondes
sleep 5

# Vérifier les logs
tail -30 debug.log
```

---

## 🧪 Test

1. Videz le cache du navigateur (Ctrl + Shift + Delete)
2. Accédez à : https://fms.undpciv.org/achats-carburant-ht/
3. La page devrait maintenant s'afficher correctement
4. Testez aussi : https://fms.undpciv.org/achats-carburant-ttc/

---

## 📋 Pages concernées par cette correction

- ✅ `/achats-carburant-ht/` - Liste des achats HT
- ✅ `/achats-carburant-ht/<id>/` - Détail d'un achat HT
- ✅ `/achats-carburant-ht/<id>/modifier/` - Modification d'un achat HT
- ✅ `/achats-carburant-ht/<id>/supprimer/` - Suppression d'un achat HT
- ✅ `/achats-carburant-ttc/` - Liste des achats TTC
- ✅ `/achats-carburant-ttc/<id>/` - Détail d'un achat TTC
- ✅ `/achats-carburant-ttc/<id>/modifier/` - Modification d'un achat TTC
- ✅ `/achats-carburant-ttc/<id>/supprimer/` - Suppression d'un achat TTC

---

## 🔍 Vérification des logs

Si le problème persiste, consultez les logs :

```bash
# Logs Django
tail -50 debug.log

# Rechercher les erreurs spécifiques
grep "ERROR" debug.log | tail -20
grep "achats" debug.log | tail -20
```

---

## 📝 Notes techniques

### Pourquoi cette erreur ?

Les templates Django utilisent ces méthodes pour générer dynamiquement les URLs :
- `{{ object.get_absolute_url }}` → Lien vers la page de détail
- `{{ object.get_update_url }}` → Lien vers la page de modification
- `{{ object.get_delete_url }}` → Lien vers la page de suppression

Sans ces méthodes, Django lève une exception `AttributeError` qui génère une erreur 500.

### Modèles similaires déjà corrigés

Les modèles suivants ont déjà ces méthodes :
- ✅ `Carte_Carburant`
- ✅ `Vehicule`
- ✅ `Fournisseur`

### Autres modèles à vérifier

Si vous rencontrez des erreurs 500 similaires sur d'autres pages, vérifiez ces modèles :
- `TypeMaintenance`
- `Maintenance`
- `Planification`
- `DemandeCourse`
- `PlanificationCourse`

---

## ✨ Après la correction

Une fois la correction déployée, testez :

1. **Liste des achats** : Affichage correct de tous les achats
2. **Boutons d'action** : Tous les boutons (Voir, Modifier, Supprimer) fonctionnent
3. **Navigation** : Passage d'une page à l'autre sans erreur
4. **Rechargements** : Bouton "Gérer les rechargements" fonctionne

---

## 🆘 Support

Si le problème persiste :
1. Vérifiez que le fichier a bien été transféré
2. Vérifiez que l'application a redémarré
3. Consultez les logs d'erreur
4. Partagez le message d'erreur complet
