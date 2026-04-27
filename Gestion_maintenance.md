Voici un **plan d’implémentation complet** pour le module **4\. Gestion Maintenance**.

**1) Périmètre fonctionnel cible**

1.  **Référentiel maintenance**
    - Types de maintenance (préventive, curative, réglementaire, pneus, vidange, etc.)
    - Gammes/intervalle d’entretien (km, jours, heures)
    - Prestataires/fournisseurs maintenance
    - Pièces et consommables (optionnel mais recommandé)
2.  **Demandes de maintenance**
    - Création par chauffeur / gestionnaire
    - Priorité, symptôme, véhicule, kilométrage, pièces jointes
    - Workflow: En attente → Validée / Rejetée → Planifiée → En cours → Terminée / Close
3.  **Planification**
    - Calendrier atelier/prestataire
    - Affectation technicien/intervenant
    - Créneaux, immobilisation véhicule, estimation coût/durée
4.  **Ordres de travail (OT)**
    - Génération OT depuis demande validée
    - Suivi exécution des tâches
    - Main d’œuvre, pièces, coûts, observation
5.  **Exécution & clôture**
    - Saisie des actions réalisées
    - Mise à jour kilométrage véhicule
    - Contrôle qualité (validation finale)
    - Clôture avec documents (facture, BL, photo)
6.  **Coûts & reporting**
    - Coût par véhicule / service / période / type
    - MTBF/MTTR (si données suffisantes)
    - Taux de disponibilité flotte
    - Alertes échéances maintenance préventive

**2) Architecture technique recommandée**

1.  **Modèles Django (domain)**
    - TypeMaintenance
    - MaintenanceDemande (ticket)
    - OrdreTravailMaintenance
    - MaintenanceIntervention (actions/temps)
    - MaintenancePiece (lignes pièces)
    - MaintenanceDocument
    - MaintenancePlanning
    - MaintenanceHistoriqueStatut (audit)
    - (optionnel) MaintenanceAlerte
2.  **Services applicatifs**
    - maintenance_service.py
        - create_demande(...)
        - validate_demande(...)
        - plan_maintenance(...)
        - start_intervention(...)
        - close_intervention(...)
    - maintenance_cost_service.py
        - agrégations coûts/kpi
    - maintenance_reporting_service.py
        - tableaux de bord + exports
3.  **Règles métier critiques**
    - Pas de clôture sans données minimales (date fin, coût, action)
    - Contrôle transitions statut strictes
    - Un véhicule immobilisé ne peut pas être planifié sur 2 interventions actives
    - Toutes opérations sensibles sous transaction.atomic()
    - Pièces jointes obligatoires selon type/phase (configurable)
4.  **Permissions RBAC**
    - **Driver**: créer/voir ses demandes
    - **Gestionnaire Maintenance**: valider, planifier, clôturer
    - **Driver Principal / Responsable service**: lecture et suivi service
    - **Admin**: accès complet + correction exceptionnelle

**3) UI/UX à livrer**

1.  **Dashboard Maintenance**
    - demandes en attente
    - interventions en retard
    - véhicules immobilisés
    - coût mensuel
2.  **Écrans principaux**
    - Liste + formulaire demande maintenance
    - Détail demande + timeline statut
    - Planning maintenance (vue calendrier)
    - OT (création, exécution, clôture)
    - Historique véhicule maintenance
    - Rapports + exports PDF/Excel
3.  **Filtres indispensables**
    - période, statut, service, véhicule, type, priorité, prestataire

**4) Roadmap d’implémentation (phases)**

1.  **Phase 1 — Cadrage & modèle (S1)**
    - finaliser entités + statuts + contraintes DB
    - migrations initiales
    - seed des types maintenance
2.  **Phase 2 — Workflow demandes (S2)**
    - CRUD demandes
    - validations + transitions statut
    - notifications de validation/rejet
3.  **Phase 3 — Planification & OT (S3-S4)**
    - planification créneaux
    - génération OT
    - gestion immobilisation véhicule
4.  **Phase 4 — Exécution & clôture (S5)**
    - saisie interventions, pièces, coûts
    - clôture contrôlée
    - documents et preuves
5.  **Phase 5 — Reporting & KPI (S6)**
    - dashboard maintenance
    - rapports analytiques + exports
6.  **Phase 6 — Hardening (S7)**
    - tests complets
    - sécurité/permissions
    - performance + UAT

**5) Plan de tests complet**

1.  **Unitaires**
    - transitions statut
    - règles de blocage (clôture invalide, overlap planning)
    - calculs de coûts
2.  **Intégration**
    - scénario E2E: demande → validation → planif → exécution → clôture
3.  **Permissions**
    - matrice rôle/action
4.  **Régression**
    - anti double immobilisation
    - anti transition illégale
    - anti clôture incomplète
5.  **UAT**
    - jeux de cas réels par profil

**6) Migration & qualité des données**

1.  Normaliser les statuts historiques
2.  Réconcilier interventions ouvertes anciennes
3.  Détecter doublons OT/documents
4.  Scripts correctifs + rapport d’écarts avant go-live

**7) KPI de succès**

- % demandes traitées < 48h
- Délai moyen de résolution
- Taux de maintenance préventive vs curative
- Coût maintenance/km par véhicule
- Disponibilité flotte (%)

**8) Priorités immédiates (pratiques)**

1.  Stabiliser le **workflow statut** + règles métier en backend
2.  Livrer **demandes + OT + clôture** (cœur opérationnel)
3.  Ajouter tests critiques
4.  Finaliser dashboard + exports