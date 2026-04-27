# GUIDE UTILISATEUR — MODULE COURSES (FMS)

Version: 1.0  
Date: 2026-04-27  
Application: FMS (Fleet Management System)

---

## 1. Objectif du module Courses

Le module **Courses** permet de gérer de bout en bout les déplacements opérationnels:

1. Saisie d’une demande de course
2. Traitement (acceptation/rejet)
3. Planification (chauffeur + véhicule + créneau)
4. Exécution par le chauffeur affecté
5. Clôture automatique de la course

Ce guide explique **comment utiliser chaque écran** selon votre rôle.

---

## 2. Profils utilisateurs et droits

## 2.1 Demandeur (Utilisateur/Driver)

Peut:
- Créer une demande de course
- Consulter ses demandes
- Modifier une demande uniquement si statut = `soumise`
- Consulter le détail d’une planification liée à ses services/affectations

Ne peut pas:
- Traiter une demande (acceptation/rejet)
- Créer une planification manuelle (sauf droits élevés)

## 2.2 Driver Principal

Peut:
- Voir les demandes de son périmètre service
- Traiter les demandes (`acceptée` / `rejetée`)
- Affecter un chauffeur et un véhicule lors de l’acceptation
- Créer une planification manuelle
- Consulter la grille de planification

## 2.3 Chauffeur affecté

Peut:
- Consulter la planification où il est affecté
- Saisir l’exécution de la course (une seule fois)

Ne peut pas:
- Saisir l’exécution d’une planification assignée à un autre chauffeur

## 2.4 Administrateur / Staff

Peut:
- Accéder à l’ensemble des demandes et planifications
- Superviser les traitements
- Corriger des affectations selon les règles de gouvernance interne

---

## 3. Statuts métier

### 3.1 Statuts de Demande de course

- `soumise` : demande créée, en attente de traitement
- `rejetée` : demande refusée, justification obligatoire
- `planifiée` : demande acceptée et planification créée
- `terminée` : exécution saisie et course clôturée

### 3.2 Statuts de Planification

- `planifiée` : course programmée
- `terminée` : exécution renseignée

---

## 4. Navigation rapide

Menu / URLs principales du module:

- **Liste des demandes**: `/demandes-courses/`
- **Nouvelle demande**: `/demandes-courses/ajouter/`
- **Détail demande**: `/demandes-courses/<id>/`
- **Traitement demande**: `/demandes-courses/<id>/traiter/`
- **Planning courses**: `/planification-courses/`
- **Détail planification**: `/planification-courses/<id>/`
- **Planification manuelle**: `/planification-course/manuelle/`
- **Saisie exécution**: `/execution-course/create/<planification_id>/`

---

## 5. Procédures détaillées

## 5.1 Créer une demande de course

### Étapes
1. Aller sur **Demandes Courses**.
2. Cliquer sur **Nouvelle demande de course**.
3. Renseigner:
   - Service demandeur
   - Lieu de départ
   - Lieu d’arrivée
   - Date/heure prévue
   - Date/heure de retour
   - Objet de la course
4. Cliquer **Créer**.

### Règles importantes
- La date/heure prévue ne doit pas être dans le passé.
- La date/heure de retour doit être postérieure à la date/heure prévue.

### Résultat attendu
- La demande est enregistrée en statut **`soumise`**.
- Une notification peut être envoyée au Driver Principal.

---

## 5.2 Modifier une demande

### Conditions
- Vous êtes l’auteur / demandeur, ou Admin.
- Le statut de la demande est **`soumise`**.

### Étapes
1. Ouvrir la demande (bouton **Voir**).
2. Cliquer **Modifier**.
3. Mettre à jour les champs.
4. Enregistrer.

### Si modification impossible
Si la demande est déjà traitée (`rejetée`, `planifiée`, `terminée`), la modification est bloquée.

---

## 5.3 Traiter une demande (Driver Principal / Admin)

### Étapes
1. Ouvrir la liste des demandes.
2. Cliquer **Traiter** sur une demande `soumise`.
3. Choisir un statut:

#### A. Rejet
- Sélectionner **Rejetée**
- Saisir la justification (obligatoire)
- Valider

#### B. Acceptation / Planification
- Sélectionner **Acceptée**
- Choisir un **chauffeur**
- Choisir un **véhicule**
- Valider

### Contrôles automatiques
- Détection de conflit véhicule (même créneau)
- Détection de conflit chauffeur (même créneau)

### Résultat attendu
- En rejet: demande passe à `rejetée`.
- En acceptation: demande passe à `planifiée` et une planification est créée / mise à jour.

---

## 5.4 Consulter la planification courses

L’écran planning contient:

1. **Calendrier latéral** (sélection de date)
2. **Liste des planifications à venir**
3. **Grille horaire par véhicule**

### Lecture de la grille
- Ligne = heure
- Colonne = véhicule
- Cellule occupée = chauffeur planifié

### Actions
- Cliquer sur une cellule planifiée pour ouvrir le **détail planification**.

---

## 5.5 Créer une planification manuelle (Driver Principal / Admin)

### Quand l’utiliser
- Course urgente sans demande préalable
- Ajustement opérationnel interne

### Étapes
1. Aller sur **Planification courses**.
2. Cliquer **Nouvelle Planification**.
3. Renseigner chauffeur, véhicule, date/heure, lieu.
4. Valider.

### Contrôle automatique
- Si le véhicule est déjà planifié au même créneau, la création est refusée.

---

## 5.6 Saisir l’exécution de la course (chauffeur affecté)

### Conditions
- Vous êtes le chauffeur affecté à la planification.
- Aucune exécution n’a déjà été enregistrée pour cette planification.

### Étapes
1. Ouvrir **Détail planification**.
2. Cliquer **Saisir l’exécution de la course**.
3. Renseigner:
   - Date/heure début
   - Date/heure fin
   - Kilométrage début
   - Kilométrage fin
   - Remarques chauffeur (optionnel)
4. Enregistrer.

### Contrôles automatiques
- Date fin > date début
- Km fin >= km début
- Km début >= kilométrage actuel du véhicule

### Résultat attendu
- Exécution enregistrée
- Kilométrage véhicule mis à jour si progression
- Planification passe à `terminée`
- Demande liée passe à `terminée`

---

## 6. Écrans et actions disponibles

## 6.1 Liste des demandes

Boutons usuels:
- **Voir**
- **Modifier** (si autorisé)
- **Traiter** (Driver Principal/Admin + statut `soumise`)

## 6.2 Détail demande

Affiche toutes les informations de la demande (service, lieux, dates, objet, statut).

## 6.3 Formulaire traitement

Champs dynamiques:
- Si `rejetée` -> justification affichée
- Si `acceptée` -> chauffeur + véhicule affichés

## 6.4 Détail planification

Affiche:
- Chauffeur
- Véhicule
- Date/heure
- Lieu
- Statut
- Détails d’exécution (si existants)

---

## 7. Messages fréquents et résolution

## 7.1 « Vous n'êtes pas autorisé »
Cause probable: rôle ou service non autorisé.

Action:
- Vérifier vos groupes utilisateur
- Vérifier votre rattachement service
- Contacter l’administrateur

## 7.2 « Ce véhicule est déjà planifié sur ce créneau »
Cause: conflit d’affectation.

Action:
- Changer le véhicule
- Changer l’heure

## 7.3 « Ce chauffeur est déjà planifié sur ce créneau »
Cause: conflit de disponibilité chauffeur.

Action:
- Changer le chauffeur
- Changer le créneau

## 7.4 « La date/heure de retour doit être postérieure »
Cause: incohérence saisie horaire.

Action:
- Corriger date/heure de retour

## 7.5 « Le kilométrage de fin ne peut pas être inférieur »
Cause: incohérence de kilométrage.

Action:
- Recontrôler les valeurs saisies

---

## 8. Bonnes pratiques utilisateur

1. Saisir une demande dès que la course est connue.
2. Toujours renseigner un objet de course clair.
3. Éviter les créneaux approximatifs pour limiter les conflits.
4. Pour les Drivers Principaux: traiter rapidement les demandes `soumise`.
5. Pour les chauffeurs: saisir l’exécution juste après la course.
6. Vérifier le kilométrage avant validation finale.

---

## 9. Checklist opérationnelle

## 9.1 Demandeur
- [ ] Demande créée
- [ ] Dates cohérentes
- [ ] Objet précis
- [ ] Suivi du statut effectué

## 9.2 Driver Principal
- [ ] Demande analysée
- [ ] Décision (acceptée/rejetée) enregistrée
- [ ] Affectation chauffeur/véhicule sans conflit

## 9.3 Chauffeur
- [ ] Exécution saisie
- [ ] Horaires cohérents
- [ ] Km début/fin cohérents
- [ ] Remarques ajoutées si incident

---

## 10. FAQ

**Q1. Puis-je modifier une demande déjà planifiée ?**  
Non, seules les demandes `soumise` sont modifiables.

**Q2. Qui peut traiter une demande ?**  
Driver Principal du service concerné ou Administrateur.

**Q3. Qui peut saisir l’exécution ?**  
Uniquement le chauffeur affecté à la planification.

**Q4. Pourquoi je ne vois pas certaines demandes ?**  
Le module applique un filtrage par service et rôle.

**Q5. Une exécution peut-elle être saisie deux fois ?**  
Non, une seule exécution est autorisée par planification.

---

## 11. Support et escalade

En cas de blocage:
1. Capturer l’écran et l’URL.
2. Noter le message exact affiché.
3. Contacter l’équipe support applicatif FMS avec:
   - Votre profil utilisateur
   - L’ID demande ou planification
   - Date/heure de l’incident

---

## 12. Évolutions recommandées (optionnel)

- Historique détaillé des transitions de statut
- Notifications in-app en plus des emails
- Export planning journalier/hebdo
- Vue charge chauffeur (occupation)
- Alertes de chevauchement multi-créneaux avancées

---

Fin du guide.

