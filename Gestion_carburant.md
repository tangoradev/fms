**Plan d’implémentation complète — Module 3. Gestion Carburant**

_(cartes, achats, rechargements, demandes, dotations)_

**1) Périmètre fonctionnel cible**

1.  **Gestion des cartes carburant**
    - CRUD carte (numéro, service, véhicule, type carburant, statut, solde)
    - Statuts: Disponible, Attribuée, Non disponible, Bloquée (option)
    - Historique des changements de statut et d’affectation
2.  **Achats carburant**
    - Flux **HT (stock)** et **TTC (direct)** séparés
    - Pièces justificatives (facture, voucher)
    - Contrôles comptables de base (montants, volumes, date achat)
3.  **Rechargements**
    - Rechargement carte depuis achat HT/TTC
    - Gestion du solde restant par dotation/source
    - Anti double-imputation (même montant alloué 2 fois)
4.  **Demandes carburant**
    - Création demande par chauffeur/demandeur
    - Workflow: En attente → Validée/Rejetée → Clôturée
    - Justification obligatoire en rejet
    - Génération fiche ravitaillement
5.  **Dotations**
    - Dotation active unique par carte (HT ou TTC)
    - Suivi consommation par dotation
    - Clôture auto quand solde = 0
6.  **Pilotage & rapports**
    - Conso par service, véhicule, période
    - État des dotations, ravitaillements, soldes
    - Alertes (solde bas, anomalies, demandes non traitées)

**2) Architecture technique**

**2.1 Modèle métier (domain)**

- Carte_Carburant
- Achat_Stock_Carburant_HT
- Achat_Carburant_TTC
- Rechargement_\* (HT/TTC)
- Demande_Carte_Carburant
- (à ajouter/recommander) MouvementCarteCarburant pour journal unique des mouvements

**2.2 Services applicatifs à créer**

1.  carburant_service.py
    - create_rechargement(...)
    - apply_consumption(...)
    - close_dotation_if_needed(...)
2.  demande_service.py
    - validate_demande(...)
    - reject_demande(...)
    - close_demande(...)
3.  reporting_service.py
    - agrégations mensuelles/hebdo, exports

**2.3 Règles métier critiques**

- Solde carte jamais négatif
- Une seule dotation active (HT ou TTC) par carte
- Rechargement impossible si source close/épuisée
- Validation demande obligatoire avant clôture
- Pièces justificatives requises selon type d’opération
- Toutes les opérations sensibles sous transaction.atomic()

**2.4 Permissions (RBAC)**

- **Driver**: créer/consulter ses demandes
- **Gestionnaire Carburant**: traiter demandes, créer achats/rechargements, clôturer
- **Driver Principal / Responsable service**: lecture + suivi service
- **Admin**: full access + corrections exceptionnelles

**3) UI / Écrans à livrer**

1.  **Dashboard Carburant**
    - demandes en attente, solde global, dotations ouvertes, anomalies
2.  **Cartes carburant**
    - liste filtrable (service, statut, type)
    - fiche carte (solde, véhicule, dotation active, historique mouvements)
3.  **Achats**
    - écrans distincts HT/TTC
    - validation formulaire + upload document
4.  **Rechargements**
    - formulaire guidé (source -> carte -> montant/volume)
    - aperçu solde source et solde carte avant validation
5.  **Demandes**
    - création demande
    - traitement (validation/rejet)
    - clôture avec traçabilité
6.  **Dotations & suivi**
    - vue “dotations actives”
    - détail consommation par dotation
7.  **Rapports**
    - état ravitaillements
    - relevé consommation
    - export PDF/Excel

**4) API (si nécessaire)**

- GET/POST /api/cartes-carburant
- GET/POST /api/achats-ht
- GET/POST /api/achats-ttc
- GET/POST /api/rechargements
- GET/POST /api/demandes-carburant
- POST /api/demandes-carburant/{id}/traiter
- POST /api/demandes-carburant/{id}/cloturer
- GET /api/dotations/suivi
- GET /api/reports/consommation

Inclure pagination, filtrage, permissions DRF, audit log.

**5) Plan de réalisation (roadmap 6 phases)**

1.  **Phase 1 — Stabilisation modèle & règles (S1)**
    - contraintes DB, validations formulaires, services métier de base
2.  **Phase 2 — Workflows demandes (S2)**
    - création/traitement/clôture + notifications
3.  **Phase 3 — Achats & rechargements (S3-S4)**
    - flux HT/TTC robustes, cohérence soldes, journal des mouvements
4.  **Phase 4 — Dotations & suivi consommation (S5)**
    - suivi par service/véhicule/carte/dotation
5.  **Phase 5 — Reporting & exports (S6)**
    - tableaux de bord + PDF/Excel
6.  **Phase 6 — Hardening (S7)**
    - tests complets, sécurité, performance, UAT

**6) Plan de tests complet**

1.  **Unitaires**
    - calculs de soldes, validations montants/volumes, transitions de statut
2.  **Intégration**
    - scénario complet: achat -> rechargement -> demande -> consommation -> clôture
3.  **Permissions**
    - matrice rôle/action
4.  **Régression**
    - anti double rechargement, anti solde négatif, dotation active unique
5.  **UAT**
    - cas métiers réels par profil (Driver / Gestionnaire / Admin)

**7) Migration & qualité de données**

1.  Normaliser statuts historiques (casse/valeurs incohérentes)
2.  Réconcilier soldes carte vs rechargements historiques
3.  Détecter doublons vouchers/numéro carte
4.  Scripts correctifs + rapport d’écarts avant go-live

**8) KPI de succès**

- % demandes traitées < 24h
- Écart “solde théorique vs réel” (cible ≈ 0)
- Taux d’opérations rejetées pour erreur de saisie
- Nombre d’anomalies mensuelles
- Taux de clôture correcte des demandes/dotations

**9) Risques & mitigations**

1.  **Incohérences historiques de soldes** → script de réconciliation + audit trail
2.  **Complexité HT/TTC** → service métier unique + tests forts
3.  **Erreurs manuelles** → formulaires guidés + contrôles bloquants
4.  **Surcharge opérationnelle** → dashboard priorisé + alertes ciblées