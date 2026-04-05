# Guide d'Utilisateurs FMS
## Fleet Management System - Manuel d'Utilisation

---

## Table des Matières

1. [Introduction et Présentation](#1-introduction-et-présentation)
2. [Connexion et Navigation](#2-connexion-et-navigation)
3. [Guide par Rôle Utilisateur](#3-guide-par-rôle-utilisateur)
4. [Fonctionnalités Principales](#4-fonctionnalités-principales)
5. [Rapports et Exports](#5-rapports-et-exports)
6. [FAQ et Résolution de Problèmes](#6-faq-et-résolution-de-problèmes)
7. [Bonnes Pratiques](#7-bonnes-pratiques)

---

## 1. Introduction et Présentation

### 1.1 Qu'est-ce que FMS ?

FMS (Fleet Management System) est un système de gestion de flotte automobile développé pour le PNUD Côte d'Ivoire. Il permet de gérer efficacement :

- **Les véhicules** de la flotte
- **Le carburant** et les cartes de carburant
- **La maintenance** préventive et curative
- **Les courses** et déplacements
- **Les rapports** et statistiques

### 1.2 Interface Utilisateur

L'interface FMS est moderne et responsive, accessible sur :
- **Ordinateurs** (Windows, Mac, Linux)
- **Tablettes** (iPad, Android)
- **Smartphones** (iOS, Android)

### 1.3 Navigateurs Supportés

✅ **Recommandés :**
- Google Chrome (version récente)
- Mozilla Firefox (version récente)
- Microsoft Edge (version récente)
- Safari (version récente)

---

## 2. Connexion et Navigation

### 2.1 Première Connexion

1. **Accéder au système**
   - Ouvrez votre navigateur web
   - Tapez l'adresse : `http://localhost:8000/` ou l'adresse fournie par votre administrateur

2. **Page de connexion**
   - Saisissez votre **adresse email**
   - Saisissez votre **mot de passe**
   - Cochez "Se souvenir de moi" si souhaité
   - Cliquez sur **"Se connecter"**

3. **Première utilisation**
   - Votre administrateur vous fournira vos identifiants
   - Changez votre mot de passe lors de la première connexion

### 2.2 Navigation Principale

#### Barre de Navigation
- **🏠 Accueil** : Tableau de bord principal
- **📋 Demandes** : Gestion des demandes (carburant, courses)
- **⛽ Carburant** : Gestion du carburant et des cartes
- **🔧 Maintenance** : Suivi des maintenances
- **👥 Administration** : Gestion des utilisateurs (admin uniquement)

#### Menu Utilisateur (coin supérieur droit)
- **👤 Profil** : Informations personnelles
- **📱 Version Mobile** : Interface mobile
- **🚪 Déconnexion** : Sortir du système

### 2.3 Tableau de Bord

Le tableau de bord affiche :
- **Statistiques générales** (véhicules, cartes, utilisateurs)
- **Dernières activités** du système
- **Raccourcis** vers les fonctions principales

---

## 3. Guide par Rôle Utilisateur

### 3.1 Rôle : Driver (Chauffeur)

#### Fonctions Principales
- ✅ Faire des demandes de carburant
- ✅ Consulter l'historique de ses demandes
- ✅ Télécharger les fiches de ravitaillement
- ✅ Faire des demandes de course

#### Interface Driver
Après connexion, vous accédez directement à la liste de vos demandes de carburant.

#### Procédures Spécifiques
1. **Demande de Carburant** (voir section 4.1)
2. **Demande de Course** (voir section 4.4)
3. **Consultation Historique** (voir section 4.6)

### 3.2 Rôle : Gestionnaire Carburant

#### Fonctions Principales
- ✅ Valider/rejeter les demandes de carburant
- ✅ Gérer les dotations de carburant
- ✅ Recharger les cartes carburant
- ✅ Générer les rapports de consommation
- ✅ Gérer les fournisseurs de carburant

#### Interface Gestionnaire
Accès au tableau de bord complet avec statistiques carburant.

#### Procédures Spécifiques
1. **Traitement des Demandes** (voir section 4.2)
2. **Gestion des Dotations** (voir section 4.3)
3. **Rapports Carburant** (voir section 5.1)

### 3.3 Rôle : Driver Principal

#### Fonctions Principales
- ✅ Planifier les courses
- ✅ Affecter les véhicules et chauffeurs
- ✅ Suivre l'exécution des courses
- ✅ Gérer les alertes de maintenance
- ✅ Valider les demandes de course

#### Procédures Spécifiques
1. **Planification des Courses** (voir section 4.5)
2. **Suivi Maintenance** (voir section 4.7)

### 3.4 Rôle : Maintenance

#### Fonctions Principales
- ✅ Enregistrer les interventions de maintenance
- ✅ Planifier la maintenance préventive
- ✅ Gérer les types de maintenance
- ✅ Suivre les coûts de maintenance
- ✅ Gérer les fournisseurs de maintenance

#### Procédures Spécifiques
1. **Enregistrement Maintenance** (voir section 4.8)
2. **Planification Préventive** (voir section 4.9)

### 3.5 Rôle : Administrateur

#### Fonctions Principales
- ✅ Gérer tous les utilisateurs
- ✅ Configurer les services et groupes
- ✅ Gérer la flotte de véhicules
- ✅ Accès à toutes les fonctionnalités
- ✅ Consulter les logs système

#### Procédures Spécifiques
1. **Gestion Utilisateurs** (voir section 4.10)
2. **Gestion Véhicules** (voir section 4.11)

---

## 4. Fonctionnalités Principales

### 4.1 Demande de Carburant (Driver)

#### Étapes pour Créer une Demande

1. **Accéder aux demandes**
   - Cliquez sur **"Demandes"** dans le menu
   - Ou utilisez le bouton **"Nouvelle demande"** sur le tableau de bord

2. **Remplir le formulaire**
   ```
   📋 Informations Requises :
   • Service : Sélectionné automatiquement
   • Véhicule : Choisir dans la liste déroulante
   • Volume demandé : En litres (ex: 50)
   • Justification : Motif de la demande
   • Station service : Lieu de ravitaillement souhaité
   ```

3. **Valider la demande**
   - Vérifiez les informations saisies
   - Cliquez sur **"Soumettre la demande"**
   - Un email de confirmation est envoyé

4. **Suivi de la demande**
   - Statut **"Soumise"** : En attente de traitement
   - Statut **"Acceptée"** : Demande validée
   - Statut **"Rejetée"** : Demande refusée (voir justification)
   - Statut **"Clôturée"** : Carburant livré

#### Conseils Pratiques
- 💡 Faites vos demandes **48h à l'avance**
- 💡 Justifiez clairement le besoin
- 💡 Vérifiez le solde de votre carte avant la demande

### 4.2 Traitement des Demandes (Gestionnaire Carburant)

#### Étapes de Validation

1. **Consulter les demandes en attente**
   - Menu **"Demandes"** → **"Demandes de carburant"**
   - Filtrer par statut **"Soumise"**

2. **Examiner une demande**
   - Cliquer sur une demande pour voir les détails
   - Vérifier :
     - ✅ Justification valide
     - ✅ Volume raisonnable
     - ✅ Solde carte suffisant
     - ✅ Dotation disponible

3. **Prendre une décision**
   
   **Pour ACCEPTER :**
   - Cliquez sur **"Traiter"**
   - Sélectionnez **"Accepter"**
   - Choisissez la dotation à utiliser
   - Saisissez le volume accordé
   - Ajoutez des remarques si nécessaire
   - Cliquez sur **"Valider"**
   
   **Pour REJETER :**
   - Cliquez sur **"Traiter"**
   - Sélectionnez **"Rejeter"**
   - **Obligatoire :** Justifiez le rejet
   - Cliquez sur **"Valider"**

4. **Génération automatique**
   - Fiche de ravitaillement PDF créée
   - Email envoyé au demandeur
   - Mise à jour des soldes

### 4.3 Gestion des Dotations (Gestionnaire Carburant)

#### Types de Dotations

**Dotation HT (Hors Taxes)**
- Achat en gros avec calcul de taxes
- Gestion du volume en litres
- Rechargement multiple des cartes

**Dotation TTC (Toutes Taxes Comprises)**
- Achat direct au prix final
- Montant fixe en FCFA
- Rechargement direct des cartes

#### Créer une Dotation HT

1. **Accéder aux achats**
   - Menu **"Carburant"** → **"Achats carburant HT"**
   - Cliquez sur **"Ajouter"**

2. **Remplir les informations**
   ```
   📋 Champs Obligatoires :
   • Service : Votre service
   • Fournisseur : Station ou grossiste
   • Voucher : Numéro de bon de commande
   • Business Unit : Code comptable
   • Date d'achat : Date de la transaction
   • Type carburant : Essence ou Gasoil
   • Volume : Quantité en litres
   • Montant HT : Prix hors taxes
   • Montant TTC : Prix toutes taxes comprises
   ```

3. **Joindre les documents**
   - Facture du fournisseur (obligatoire)
   - Bon de livraison
   - Autres justificatifs

#### Recharger une Carte

1. **Depuis une dotation**
   - Ouvrir la dotation
   - Cliquer sur **"Rechargements"**
   - Cliquer sur **"Nouveau rechargement"**

2. **Sélectionner la carte**
   - Choisir la carte dans la liste
   - Saisir le volume à recharger
   - Le prix unitaire est calculé automatiquement

3. **Valider le rechargement**
   - Vérifier les calculs
   - Cliquer sur **"Enregistrer"**
   - La carte est automatiquement mise à jour

### 4.4 Demande de Course (Driver/Utilisateur)

#### Créer une Demande de Course

1. **Accéder aux courses**
   - Menu **"Demandes"** → **"Demandes de courses"**
   - Cliquer sur **"Nouvelle demande"**

2. **Remplir le formulaire**
   ```
   📋 Informations Requises :
   • Lieu de départ : Adresse de départ
   • Lieu d'arrivée : Destination
   • Date et heure prévue : Début du déplacement
   • Date et heure de retour : Fin prévue
   • Objet de la mission : Motif détaillé
   • Utilisateur assigné : Qui effectuera la course
   ```

3. **Soumettre la demande**
   - Vérifier toutes les informations
   - Cliquer sur **"Soumettre"**
   - Notification envoyée au responsable

#### Suivi des Demandes de Course

- **Soumise** : En attente de validation
- **Acceptée** : Approuvée, en attente de planification
- **Rejetée** : Refusée avec justification
- **Planifiée** : Véhicule et chauffeur assignés
- **Terminée** : Course effectuée et clôturée

### 4.5 Planification des Courses (Driver Principal)

#### Valider une Demande

1. **Consulter les demandes**
   - Menu **"Demandes"** → **"Demandes de courses"**
   - Filtrer par statut **"Soumise"**

2. **Examiner la demande**
   - Vérifier la pertinence de la mission
   - Contrôler les dates et heures
   - Valider la faisabilité

3. **Prendre une décision**
   - Cliquer sur **"Traiter"**
   - **Accepter** : Passe au statut "Acceptée"
   - **Rejeter** : Justifier obligatoirement

#### Planifier une Course

1. **Accéder à la planification**
   - Menu **"Planification courses"**
   - Voir les courses acceptées

2. **Créer une planification**
   - Cliquer sur **"Planifier"** pour une demande
   - Ou créer une planification manuelle

3. **Assigner les ressources**
   ```
   📋 Assignations :
   • Véhicule : Choisir un véhicule disponible
   • Chauffeur : Assigner un driver
   • Date/Heure : Confirmer ou ajuster
   • Remarques : Instructions spéciales
   ```

4. **Valider la planification**
   - Vérifier la disponibilité des ressources
   - Cliquer sur **"Enregistrer"**
   - Notifications envoyées aux concernés

### 4.6 Consultation de l'Historique

#### Historique des Demandes de Carburant

1. **Accéder à l'historique**
   - Menu **"Demandes"** → **"Demandes de carburant"**
   - Toutes vos demandes sont listées

2. **Filtrer les résultats**
   - Par **statut** : Toutes, Soumises, Acceptées, etc.
   - Par **période** : Dernière semaine, mois, année
   - Par **véhicule** : Filtrer par véhicule spécifique

3. **Consulter les détails**
   - Cliquer sur une demande pour voir :
     - Informations complètes
     - Historique des modifications
     - Fiche de ravitaillement (si acceptée)

#### Télécharger les Fiches

1. **Depuis la liste des demandes**
   - Icône **📄** pour télécharger la fiche PDF

2. **Depuis le détail d'une demande**
   - Bouton **"Télécharger la fiche"**
   - Bouton **"Régénérer la fiche"** (si nécessaire)

### 4.7 Suivi de la Maintenance (Driver Principal)

#### Consulter les Alertes

1. **Tableau de bord maintenance**
   - Menu **"Maintenance"** → **"Planifications"**
   - Voir les alertes par couleur :
     - 🔴 **Rouge** : Maintenance en retard
     - 🟡 **Jaune** : Alerte (proche de l'échéance)
     - 🟢 **Vert** : Planifiée (dans les temps)

2. **Détails d'une planification**
   - Cliquer sur une planification
   - Voir :
     - Prochaine échéance kilométrique
     - Prochaine échéance temporelle
     - Historique des maintenances
     - Progression vers l'échéance

#### Programmer une Maintenance

1. **Depuis une alerte**
   - Cliquer sur **"Programmer maintenance"**
   - Ou créer une nouvelle maintenance

2. **Contacter le service maintenance**
   - Les responsables maintenance reçoivent les alertes
   - Coordination pour planifier l'intervention

### 4.8 Enregistrement Maintenance (Maintenance)

#### Créer une Intervention

1. **Accéder aux maintenances**
   - Menu **"Maintenance"** → **"Maintenances"**
   - Cliquer sur **"Ajouter"**

2. **Remplir le formulaire**
   ```
   📋 Informations Requises :
   • Service : Service du véhicule
   • Véhicule : Sélectionner le véhicule
   • Type de maintenance : Vidange, Révision, etc.
   • Détail : Description de l'intervention
   • Fournisseur : Garage ou mécanicien
   • Date : Date de l'intervention
   • Kilométrage : Km du véhicule après intervention
   • Montant : Coût de l'intervention
   • Facture : Document obligatoire
   ```

3. **Planification future (optionnel)**
   ```
   📋 Périodicité :
   • Périodicité km : Prochaine maintenance dans X km
   • Alerte km : Marge d'alerte en km
   • Périodicité mois : Prochaine maintenance dans X mois
   • Alerte mois : Marge d'alerte en mois
   ```

4. **Enregistrer l'intervention**
   - Joindre obligatoirement la facture
   - Cliquer sur **"Enregistrer"**
   - La planification est automatiquement mise à jour

### 4.9 Planification Préventive (Maintenance)

#### Créer une Planification

1. **Accéder aux planifications**
   - Menu **"Maintenance"** → **"Planifications"**
   - Cliquer sur **"Ajouter"**

2. **Configurer la planification**
   ```
   📋 Configuration :
   • Véhicule : Sélectionner le véhicule
   • Type maintenance : Type d'intervention
   • Utilisateur : Driver principal responsable
   • Échéance km : Kilométrage cible
   • Échéance date : Date limite (optionnel)
   • Alertes : Marges d'alerte
   ```

3. **Système d'alertes automatiques**
   - Calcul automatique des seuils
   - Notifications aux responsables
   - Mise à jour après chaque maintenance

### 4.10 Gestion des Utilisateurs (Administrateur)

#### Créer un Utilisateur

1. **Accéder à la gestion**
   - Menu **"Administration"** → **"Utilisateurs"**
   - Cliquer sur **"Ajouter"**

2. **Informations utilisateur**
   ```
   📋 Champs Obligatoires :
   • Nom complet : Prénom et nom
   • Email : Identifiant de connexion (unique)
   • Mot de passe : Mot de passe initial
   • Fonction : Poste occupé
   • Service(s) : Affectation organisationnelle
   • Groupe(s) : Rôles et permissions
   • Statut : Actif ou Inactif
   ```

3. **Attribution des rôles**
   - **Driver** : Demandes de carburant et courses
   - **Gestionnaire Carburant** : Validation carburant
   - **Driver Principal** : Planification courses
   - **Maintenance** : Gestion maintenance
   - **Admin** : Administration complète

#### Gérer les Services et Groupes

**Services :**
- Représentent les départements/unités
- Organisent les utilisateurs et véhicules
- Menu **"Administration"** → **"Services"**

**Groupes :**
- Définissent les rôles et permissions
- Contrôlent l'accès aux fonctionnalités
- Menu **"Administration"** → **"Groupes"**

### 4.11 Gestion des Véhicules (Administrateur)

#### Ajouter un Véhicule

1. **Accéder à la flotte**
   - Menu **"Administration"** → **"Véhicules"**
   - Cliquer sur **"Ajouter"**

2. **Informations véhicule**
   ```
   📋 Champs Obligatoires :
   • Service : Affectation du véhicule
   • Marque : Constructeur (Toyota, Nissan, etc.)
   • Modèle : Modèle du véhicule
   • Châssis : Numéro de châssis (unique)
   • Immatriculation : Plaque d'immatriculation (unique)
   • Type carburant : Essence ou Gasoil
   • Date mise en service : Date d'acquisition
   • Kilométrage : Kilométrage actuel
   • Statut : Disponible ou Non disponible
   ```

3. **Documents optionnels**
   - Carte grise
   - Photos du véhicule
   - Autres documents

#### Gérer les Cartes Carburant

1. **Créer une carte**
   - Menu **"Carburant"** → **"Cartes carburant"**
   - Cliquer sur **"Ajouter"**

2. **Configuration carte**
   ```
   📋 Informations Carte :
   • Service : Service gestionnaire
   • Numéro carte : Identifiant unique
   • Véhicule : Attribution (optionnel)
   • Solde initial : Montant en FCFA
   • Statut : Disponible, Attribuée, Non disponible
   ```

---

## 5. Rapports et Exports

### 5.1 Rapports de Carburant

#### Rapport Mensuel de Consommation

1. **Accéder aux rapports**
   - Menu **"Carburant"** → **"Rapports"**
   - Cliquer sur **"Rapport mensuel"**

2. **Paramètres du rapport**
   - **Période** : Sélectionner le mois et l'année
   - **Service** : Filtrer par service (optionnel)
   - **Type carburant** : Essence, Gasoil ou Tous

3. **Génération et export**
   - Aperçu à l'écran
   - **Export PDF** : Rapport formaté pour impression
   - **Export Excel** : Données pour analyse

#### Relevé de Consommation

1. **Paramètres avancés**
   - Période personnalisée
   - Filtres multiples (service, véhicule, carte)
   - Groupement par véhicule ou par carte

2. **Contenu du rapport**
   - Consommation par véhicule
   - Évolution mensuelle
   - Comparaisons et tendances
   - Coûts détaillés

#### État des Ravitaillements

1. **Génération automatique**
   - Toutes les demandes acceptées
   - Fiches de ravitaillement consolidées
   - Export PDF groupé

### 5.2 Rapports de Maintenance

#### Rapport Global de Maintenance

1. **Accéder aux rapports**
   - Menu **"Maintenance"** → **"Rapports"**

2. **Filtres disponibles**
   - **Période** : Date de début et fin
   - **Service** : Filtrer par service
   - **Véhicule** : Véhicule spécifique
   - **Type maintenance** : Type d'intervention
   - **Fournisseur** : Prestataire

3. **Exports disponibles**
   - **PDF** : Rapport formaté
   - **Excel** : Données détaillées pour analyse

#### Contenu des Rapports Maintenance

- **Interventions par véhicule**
- **Coûts de maintenance**
- **Fréquence des pannes**
- **Performance des fournisseurs**
- **Planifications à venir**
- **Alertes en cours**

### 5.3 Rapports de Courses

#### Suivi des Courses

1. **Rapport d'activité**
   - Courses planifiées vs réalisées
   - Utilisation des véhicules
   - Kilométrage parcouru

2. **Analyse des coûts**
   - Coût par course
   - Consommation carburant
   - Optimisation des trajets

---

## 6. FAQ et Résolution de Problèmes

### 6.1 Problèmes de Connexion

**❓ Je ne peux pas me connecter**

✅ **Solutions :**
1. Vérifiez votre adresse email (pas de username)
2. Vérifiez votre mot de passe (sensible à la casse)
3. Contactez votre administrateur pour réinitialiser
4. Vérifiez que votre compte est actif

**❓ J'ai oublié mon mot de passe**

✅ **Solutions :**
1. Contactez votre administrateur système
2. Il pourra réinitialiser votre mot de passe
3. Vous recevrez un nouveau mot de passe par email

### 6.2 Problèmes de Demandes

**❓ Ma demande de carburant est rejetée**

✅ **Vérifications :**
1. Lisez la justification du rejet
2. Vérifiez le solde de votre carte
3. Assurez-vous que la justification est claire
4. Respectez les volumes raisonnables
5. Contactez votre gestionnaire carburant

**❓ Je ne reçois pas les notifications email**

✅ **Solutions :**
1. Vérifiez votre dossier spam/courrier indésirable
2. Vérifiez que votre adresse email est correcte
3. Contactez l'administrateur pour vérifier la configuration

### 6.3 Problèmes d'Interface

**❓ L'interface ne s'affiche pas correctement**

✅ **Solutions :**
1. Actualisez la page (F5 ou Ctrl+F5)
2. Videz le cache de votre navigateur
3. Utilisez un navigateur récent et supporté
4. Vérifiez votre connexion internet

**❓ Les fichiers PDF ne s'ouvrent pas**

✅ **Solutions :**
1. Installez un lecteur PDF (Adobe Reader, etc.)
2. Autorisez les pop-ups pour le site FMS
3. Téléchargez le fichier puis ouvrez-le

### 6.4 Problèmes de Données

**❓ Les soldes de cartes ne sont pas à jour**

✅ **Vérifications :**
1. Actualisez la page
2. Vérifiez les dernières transactions
3. Contactez le gestionnaire carburant
4. Vérifiez les rechargements récents

**❓ Mon véhicule n'apparaît pas dans la liste**

✅ **Solutions :**
1. Vérifiez que le véhicule est "Disponible"
2. Vérifiez votre affectation de service
3. Contactez l'administrateur

---

## 7. Bonnes Pratiques

### 7.1 Sécurité

#### Protection du Compte

🔐 **Mot de passe sécurisé :**
- Minimum 8 caractères
- Mélange de lettres, chiffres et symboles
- Changement régulier (tous les 3 mois)
- Ne pas partager ses identifiants

🔐 **Navigation sécurisée :**
- Toujours se déconnecter après utilisation
- Ne pas laisser sa session ouverte
- Utiliser "Se souvenir de moi" uniquement sur son ordinateur personnel

#### Protection des Données

📊 **Confidentialité :**
- Ne pas partager les rapports avec des tiers
- Respecter la confidentialité des données de l'organisation
- Signaler tout problème de sécurité

### 7.2 Utilisation Efficace

#### Planification des Demandes

📅 **Anticipation :**
- Faire les demandes de carburant 48h à l'avance
- Planifier les courses une semaine à l'avance
- Vérifier les soldes régulièrement

📅 **Organisation :**
- Grouper les demandes similaires
- Utiliser des justifications claires et précises
- Tenir compte des contraintes opérationnelles

#### Suivi et Contrôle

📈 **Monitoring :**
- Consulter régulièrement l'historique
- Suivre sa consommation de carburant
- Respecter les planifications de maintenance

📈 **Optimisation :**
- Analyser ses habitudes de consommation
- Proposer des améliorations
- Participer aux formations

### 7.3 Communication

#### Avec les Gestionnaires

💬 **Clarté :**
- Justifications détaillées et précises
- Communication proactive en cas de problème
- Respect des procédures établies

💬 **Réactivité :**
- Répondre rapidement aux demandes d'information
- Signaler les anomalies rapidement
- Proposer des solutions constructives

#### Avec l'Équipe

👥 **Collaboration :**
- Partager les bonnes pratiques
- Aider les nouveaux utilisateurs
- Participer aux réunions de formation

### 7.4 Maintenance du Système

#### Côté Utilisateur

🔧 **Maintenance préventive :**
- Vider régulièrement le cache du navigateur
- Maintenir le navigateur à jour
- Signaler les bugs ou dysfonctionnements

🔧 **Sauvegarde :**
- Télécharger et archiver les documents importants
- Conserver les fiches de ravitaillement
- Faire des captures d'écran en cas de problème

---

## 8. Support et Assistance

### 8.1 Contacts

#### Support Technique
- **Email :** support-fms@undpciv.org
- **Téléphone :** +225 XX XX XX XX
- **Heures :** Lundi-Vendredi 8h-17h

#### Administrateur Système
- **Email :** admin-fms@undpciv.org
- **Urgences :** +225 XX XX XX XX

### 8.2 Formation

#### Sessions de Formation
- Formation initiale pour nouveaux utilisateurs
- Sessions de mise à jour trimestrielles
- Formation spécialisée par rôle

#### Documentation
- Guide technique (pour administrateurs)
- Tutoriels vidéo (en préparation)
- FAQ mise à jour régulièrement

### 8.3 Évolutions

#### Demandes d'Amélioration
- Formulaire de suggestion en ligne
- Réunions trimestrielles utilisateurs
- Roadmap des évolutions

---

## Conclusion

Ce guide d'utilisateurs vous accompagne dans l'utilisation quotidienne du système FMS. Pour toute question non couverte dans ce document, n'hésitez pas à contacter l'équipe support.

**Bonne utilisation du système FMS !** 🚗⛽🔧

---

**© 2025 PNUD Côte d'Ivoire - Tous droits réservés**

*Version 1.0 - Janvier 2025*