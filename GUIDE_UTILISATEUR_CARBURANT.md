## Guide Utilisateur — Module Gestion Carburant

Version: 1.0  
Application: FMS  
Public: Chauffeurs, Gestionnaires Carburant, Responsables, Administrateurs

---

### 1) Objectif du module

Le module **Gestion Carburant** permet de piloter le cycle complet de carburant:

- gestion des **cartes carburant**,
- gestion des **achats** (HT stock et TTC direct),
- gestion des **rechargements**,
- gestion des **demandes de ravitaillement**,
- suivi des **dotations**,
- production de **rapports**.

L’objectif est de sécuriser les opérations, tracer les consommations et fiabiliser les soldes.

---

### 2) Profils et droits d’accès

#### 2.1 Chauffeur (Driver)

- Créer une demande carburant.
- Consulter ses demandes.
- Clôturer une demande acceptée après ravitaillement.

#### 2.2 Gestionnaire Carburant

- Créer et gérer cartes, achats, rechargements.
- Traiter les demandes (accepter/rejeter).
- Suivre dotations et ravitaillements.
- Consulter dashboard et rapports.

#### 2.3 Administrateur

- Accès complet (pilotage, contrôle, correction exceptionnelle).

> Remarque: les accès sont filtrés selon les services affectés à l’utilisateur.

---

### 3) Vue d’ensemble du workflow

1. **Achat carburant** (HT ou TTC)
2. **Rechargement** d’une ou plusieurs cartes à partir d’une dotation
3. **Demande carburant** créée par le chauffeur
4. **Traitement** de la demande (Acceptée / Rejetée)
5. **Clôture** de la demande après ravitaillement
6. **Mise à jour automatique** des soldes (carte, rechargement, dotation)

---

### 4) Navigation du module

Les principaux écrans du module:

- **Cartes carburant**
- **Achats carburant HT**
- **Achats carburant TTC**
- **Rechargements de cartes**
- **Demandes carte carburant**
- **Dashboard carburant**
- **Suivi des dotations**
- **Rapports**:
  - Relevé consommation
  - État ravitaillements

---

### 5) Gestion des cartes carburant

#### 5.1 Créer une carte

Champs principaux:

- Service
- Numéro de carte
- Véhicule (optionnel)
- Solde (automatique/recalculé)
- Statut (Disponible, Attribué, Non disponible, Bloquée)

#### 5.2 Modifier une carte

- Mettre à jour affectation véhicule.
- Mettre à jour statut selon la situation opérationnelle.

#### 5.3 Bonnes pratiques

- Ne jamais dupliquer un numéro de carte.
- Bloquer une carte compromise plutôt que la supprimer.
- Vérifier la cohérence service carte / service dotation.

---

### 6) Gestion des achats carburant

Deux flux séparés:

- **HT (stock)**: approvisionnement de stock/dotation.
- **TTC (direct)**: dotation directe.

#### 6.1 Créer un achat HT/TTC

Champs typiques:

- Service
- Fournisseur carburant
- Voucher
- Business Unit / Dept ID / Project ID
- Date achat
- Libellé
- Type carburant
- Volume
- Montants (HT et TTC pour HT, TTC pour TTC)
- Document justificatif

#### 6.2 Contrôles automatiques

- Montants > 0
- Volume > 0
- Cohérence montant HT/TTC
- Statut dotation recalculé automatiquement (Ouverte/Close)

---

### 7) Gestion des rechargements

#### 7.1 Principe

Un rechargement lie:

- une carte carburant,
- une dotation source (HT ou TTC),
- un montant et un volume.

#### 7.2 Règles métiers appliquées

- Pas de montant/volume négatif ou nul.
- Même carte + même dotation: **interdit en doublon**.
- Carte et dotation doivent appartenir au **même service**.
- Une carte ne peut pas être active simultanément en HT et TTC.
- Le total rechargé ne peut pas dépasser le montant de la dotation.

#### 7.3 Impact automatique

- Mise à jour de la dotation active sur la carte.
- Recalcul du solde carte.
- Mise à jour du statut de la dotation.

---

### 8) Gestion des demandes carburant

#### 8.1 Création (chauffeur)

Le chauffeur renseigne:

- Service
- Véhicule
- Motif de demande

Statut initial: **En attente**.

#### 8.2 Traitement (gestionnaire)

Actions:

- **Acceptée**: dotation obligatoire.
- **Rejetée**: commentaire obligatoire.

Une fiche de ravitaillement peut être générée selon le workflow.

#### 8.3 Clôture (après ravitaillement)

Champs à renseigner:

- Date ravitaillement
- Kilométrage véhicule
- Prix unitaire TTC
- Volume
- Montant TTC
- Station service
- Document justificatif

Effets:

- statut passe à **Close**,
- consommation appliquée au rechargement,
- soldes mis à jour,
- fiche ravitaillement régénérée.

---

### 9) Suivi des dotations

La vue de suivi permet de contrôler:

- montant total dotation,
- montant utilisé,
- solde restant,
- pourcentage d’utilisation,
- rechargements associés,
- demandes associées.

Utiliser cette vue pour détecter rapidement:

- dotations presque épuisées,
- anomalies de consommation,
- dotations à clôturer.

---

### 10) Rapports

#### 10.1 Relevé de consommation

Sélection:

- type de dotation (HT/TTC),
- dotation,
- mois/année,
- service (optionnel).

Résultat:

- solde d’ouverture,
- consommation du mois,
- solde de clôture,
- totaux globaux.

#### 10.2 État des ravitaillements

Filtres multicritères:

- période,
- service,
- dotation,
- carte,
- véhicule,
- chauffeur.

Exports disponibles: **PDF** et **Excel**.

---

### 11) Notifications et documents

Le module peut envoyer:

- notifications email lors de création/traitement/clôture,
- logs d’envoi,
- génération et téléchargement de fiche ravitaillement PDF.

---

### 12) Cas d’usage complet (exemple)

1. Le gestionnaire crée un achat HT “Dotation Mars Service A”.
2. Il recharge la carte `CARD-001` avec 300 000 FCFA.
3. Le chauffeur crée une demande pour son véhicule.
4. Le gestionnaire accepte la demande et associe la dotation.
5. Après passage en station, le chauffeur clôture avec facture.
6. Le module réduit automatiquement:
   - `solde_restant` du rechargement,
   - `solde` de la carte,
   - et met à jour les indicateurs de dotation.

---

### 13) Contrôles et messages fréquents

- "Le montant TTC doit être supérieur à zéro."
- "Le volume doit être supérieur à zéro."
- "Cette carte a déjà été rechargée avec cette dotation."
- "La dotation est obligatoire pour accepter la demande."
- "Un commentaire est obligatoire en cas de rejet."
- "Seules les demandes acceptées peuvent être clôturées."

Interprétation: ces messages bloquent volontairement les incohérences métier.

---

### 14) Bonnes pratiques opérationnelles

- Créer les achats dès réception des justificatifs.
- Recharger les cartes uniquement depuis une dotation correcte (HT ou TTC).
- Traiter les demandes quotidiennement (SLA < 24h recommandé).
- Exiger les justificatifs de clôture (ticket/facture).
- Vérifier hebdomadairement les dotations proches de zéro.
- Archiver les exports mensuels (PDF/Excel).

---

### 15) FAQ

#### 15.1 Pourquoi une carte n’apparaît pas dans la liste de rechargement?

Vérifier:

- service de la carte,
- statut de la carte,
- dotation active incompatible (HT/TTC),
- règles anti-doublon.

#### 15.2 Pourquoi une demande ne peut pas être clôturée?

Causes courantes:

- statut non "Acceptée",
- montant/volume/km manquant ou invalide,
- station service absente.

#### 15.3 Pourquoi une dotation passe à "Close"?

Quand le solde théorique atteint 0 (dotation entièrement consommée/allouée).

#### 15.4 Peut-on corriger une erreur après clôture?

Oui, uniquement via un profil habilité (gestionnaire/admin), avec traçabilité recommandée.

---

### 16) Glossaire

- **Dotation**: enveloppe carburant issue d’un achat HT/TTC.
- **Rechargement**: allocation d’une partie de dotation à une carte.
- **Solde restant**: montant encore disponible après consommation.
- **Demande Close**: demande finalisée après ravitaillement.

---

### 17) Support

En cas d’incident:

1. Capturer l’écran + message exact.
2. Noter numéro de demande/carte/dotation.
3. Contacter l’équipe support FMS ou l’administrateur module.

---

Fin du guide.
