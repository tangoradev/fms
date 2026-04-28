# Guide Utilisateur — Module Gestion Maintenance

## 1) Objectif du module

Le module **Gestion Maintenance** permet de :

- structurer les types de maintenance (vidange, révision, freinage, etc.) ;
- enregistrer les opérations de maintenance réalisées ;
- planifier les prochaines échéances (km / date) ;
- suivre les alertes, retards et historiques par véhicule ;
- produire des rapports et exporter les données (PDF/Excel).

Ce guide s’adresse aux utilisateurs métiers, gestionnaires et administrateurs qui pilotent l’entretien de la flotte.

---

## 2) Profils autorisés

L’accès au module est contrôlé par rôle.

Utilisateurs autorisés :

- **Gestionnaire Maintenance**
- **Gestionnaire Carburant**
- **Driver Principal**
- **Administrateur / Staff**

Si vous n’avez pas accès à certaines pages, contactez l’administrateur pour vérifier votre affectation de rôle.

---

## 3) Menu et écrans principaux

Le module est organisé autour de 3 blocs :

1. **Type Maintenance**
   - Créer et maintenir le référentiel des types d’entretien.

2. **Maintenance**
   - Enregistrer les interventions effectuées sur les véhicules.
   - Consulter, modifier, supprimer les interventions.

3. **Planification**
   - Génération et suivi des prochaines échéances.
   - Visualisation des statuts : planifiée / alerte / retard.

4. **Rapports Maintenance**
   - Filtrage des données.
   - Export en **PDF** et **Excel**.

---

## 4) Processus recommandé (de bout en bout)

### Étape 1 — Paramétrer les types de maintenance

Avant toute saisie, vérifiez que les types de maintenance existent :

- libellé clair (ex. Vidange moteur) ;
- description facultative mais utile.

### Étape 2 — Enregistrer une maintenance réalisée

Créer une maintenance en renseignant :

- service ;
- véhicule ;
- type de maintenance ;
- fournisseur (de type maintenance) ;
- date d’intervention ;
- kilométrage véhicule au moment de l’intervention ;
- montant ;
- détail / observation ;
- périodicités (km/mois) et alertes (km/mois), si applicables.

### Étape 3 — Vérifier la planification générée / mise à jour

Après enregistrement, le système met à jour automatiquement la planification associée selon les règles métier.

### Étape 4 — Exploiter les rapports

Appliquez des filtres (dates, véhicule, type, service, statut…) puis exportez les résultats selon le besoin (PDF pour diffusion, Excel pour analyse).

---

## 5) Détail des fonctionnalités

## 5.1 Type Maintenance

### Créer

1. Ouvrir **Type Maintenance > Ajouter**.
2. Saisir le libellé.
3. Enregistrer.

### Modifier / Supprimer

- Depuis la liste, utiliser les actions de ligne (modifier/supprimer).
- La suppression est à utiliser avec prudence si des maintenances existantes y sont rattachées.

---

## 5.2 Maintenance

### Créer une maintenance

1. Ouvrir **Maintenance > Nouvelle maintenance**.
2. Renseigner les champs obligatoires.
3. Valider.

### Modifier une maintenance

1. Depuis la liste maintenance, ouvrir la ligne concernée.
2. Cliquer sur **Modifier**.
3. Ajuster les informations.
4. Enregistrer.

### Supprimer une maintenance

1. Ouvrir la fiche maintenance.
2. Cliquer sur **Supprimer**.
3. Confirmer la suppression.

### Consulter le détail

La page détail permet de visualiser l’ensemble des données : véhicule, type, date, coûts, périodicité et indicateurs utiles.

---

## 5.3 Planification

### Liste des planifications

La liste présente les planifications avec leurs informations clés :

- véhicule,
- type de maintenance,
- échéances,
- statut dynamique (planifiée / alerte / retard).

### Détail planification

Le détail planification inclut :

- informations générales ;
- progression kilométrique ;
- échéances de date ;
- historique des maintenances liées au véhicule.

### Modifier / Supprimer planification

- Utiliser les boutons d’action depuis la fiche détail ou la liste.
- Toute modification doit respecter la cohérence des données métier.

---

## 5.4 Rapports Maintenance

### Filtrage

Utilisez les filtres pour cibler le périmètre :

- période (date début / date fin),
- service,
- véhicule,
- type de maintenance,
- statut de planification.

### Export PDF

- Format adapté à la diffusion et à l’archivage.
- Mise en page orientée lecture managériale.

### Export Excel

- Format adapté aux analyses (tri, pivot, consolidation).
- Vérifiez l’intégrité des filtres avant export.

---

## 6) Règles métier et validations importantes

Le système applique des contrôles stricts. Les plus importants :

1. **Cohérence service/véhicule**
   - Le véhicule doit appartenir au service sélectionné.

2. **Type fournisseur**
   - Le fournisseur doit être de type **Maintenance**.

3. **Kilométrage positif**
   - Le kilométrage doit être strictement supérieur à zéro.

4. **Montant positif**
   - Le montant doit être strictement supérieur à zéro.

5. **Alertes vs périodicités**
   - `alerte_km` doit être strictement inférieure à `periodicite_km`.
   - `alerte_mois` doit être strictement inférieure à `periodicite_mois`.

6. **Mise à jour kilométrage véhicule**
   - Lorsqu’une maintenance est enregistrée avec un km supérieur au km actuel du véhicule, le kilométrage véhicule est mis à jour automatiquement.

---

## 7) Messages d’erreur fréquents et solutions

### « Le véhicule sélectionné n'appartient pas au service »

- Vérifier que le service du formulaire correspond au service du véhicule.

### « Le fournisseur doit être de type maintenance »

- Choisir un fournisseur catégorisé Maintenance.

### « Le kilométrage doit être supérieur à zéro »

- Saisir une valeur numérique positive.

### « L’alerte doit être inférieure à la périodicité »

- Réduire la valeur d’alerte ou augmenter la périodicité.

---

## 8) Bonnes pratiques d’utilisation

- Saisir les maintenances au fil de l’eau (éviter les retards de saisie).
- Contrôler systématiquement le kilométrage lors de l’enregistrement.
- Harmoniser les libellés des types de maintenance.
- Utiliser les exports périodiques (hebdo/mensuel) pour pilotage.
- Vérifier les planifications en statut **En alerte** et **En retard** en priorité.

---

## 9) Check-list opérationnelle

### Quotidien

- [ ] Enregistrer les nouvelles maintenances réalisées.
- [ ] Vérifier les alertes/retards sur planification.

### Hebdomadaire

- [ ] Analyser les coûts par véhicule/type maintenance.
- [ ] Exporter un rapport de suivi.

### Mensuel

- [ ] Revoir la qualité des données (doublons, erreurs de saisie).
- [ ] Contrôler la conformité du référentiel type maintenance.

---

## 10) FAQ

### Q1. Pourquoi je ne vois pas le module ?

Votre compte ne dispose probablement pas du rôle requis. Demandez à l’administrateur de vous affecter à un groupe autorisé.

### Q2. Une planification ne se met pas à jour après saisie maintenance, que faire ?

Vérifier que la maintenance est bien enregistrée avec un type valide et des périodicités exploitables. Recharger ensuite la page planification.

### Q3. Quel format choisir entre PDF et Excel ?

- **PDF** : partage/validation formelle.
- **Excel** : analyse détaillée et retraitement.

### Q4. Peut-on modifier une maintenance déjà saisie ?

Oui, si vos droits le permettent. Toute modification peut impacter la planification et les indicateurs.

---

## 11) Support et gouvernance

En cas d’anomalie :

1. Capturer l’écran et le message d’erreur.
2. Noter l’action effectuée et l’heure.
3. Transmettre au support applicatif / administrateur FMS.

Pour les changements de règles métier (nouveaux types, fréquence, logique d’alerte), passer par le référent métier maintenance avant implémentation.

---

## 12) Version du document

- **Document** : GUIDE_UTILISATEUR_MAINTENANCE.md
- **Module** : Gestion Maintenance
- **Statut** : Version complète structurée
- **Langue** : Français
