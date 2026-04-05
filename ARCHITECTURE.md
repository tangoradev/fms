# ARCHITECTURE FMS (Cartographie Système Complète)

Source d'analyse: `.trae/documents/FMS_Documentation_Complete.md` (lecture intégrale)

---

## 1. ARBRE D’ARCHITECTURE GLOBAL

[CORE] Runtime Django FMS
|- [SUB] fms/settings.py -> persiste dans Database Engine Config (SQLite/MySQL)
|  |- Dependencies:
|  |  - dépend de Environnement Python 3.8+
|  |  - dépend de Backend DB (SQLite/MySQL)
|  |  - dépend de SMTP Config
|  |- Dependents:
|  |  - utilisé par Authentification
|  |  - utilisé par Notifications Email
|  |  - utilisé par Logging Core
|  |  - utilisé par Cache Redis
|  |
|- [SUB] fms/urls.py -> expose via HTTP Routing Global
|  |- Dependencies:
|  |  - dépend de core/urls.py
|  |- Dependents:
|  |  - utilisé par toutes les Views
|  |
|- [SUB] manage.py -> déclenche Django Command Runtime
|  |- Dependents:
|  |  - utilisé par migrations, runserver, scripts
|  |
|- [UTILITY] Logging Core -> notifie debug.log
|  |- Dependencies:
|  |  - dépend de settings.LOGGING
|  |- Dependents:
|  |  - utilisé par vues carburant
|  |
|- [UTILITY] Cache Redis -> consomme redis://127.0.0.1:6379/1
|  |- Dependencies:
|  |  - dépend de django.core.cache
|  |- Dependents:
|  |  - utilisé par dashboard_carburant

[CORE] Authentification & Autorisation
|- [SUB] Modèle Utilisateur (AUTH_USER_MODEL) -> persiste dans Database
|  |- Dependencies:
|  |  - dépend de AbstractBaseUser
|  |  - dépend de PermissionsMixin
|  |  - dépend de Groupe
|  |  - dépend de Service
|  |- Dependents:
|  |  - utilisé par Demande_Carte_Carburant
|  |  - utilisé par Notifications Email
|  |  - utilisé par Contrôle d'accès vues
|  |
|- [SUB] Groupe -> persiste dans Database
|  |- Dependents:
|  |  - utilisé par contrôle rôle Driver
|  |  - utilisé par contrôle rôle Gestionnaire Carburant
|  |  - utilisé par contrôle rôle Driver Principal
|  |
|- [SUB] Service -> persiste dans Database
|  |- Dependents:
|  |  - utilisé par Utilisateur
|  |  - utilisé par Vehicule
|  |  - utilisé par Carte_Carburant
|  |
|- [HOOK] login_required -> déclenche contrôle session
|  |- Dependents:
|  |  - utilisé par vues métier protégées
|  |
|- [HOOK] user_passes_test(role check) -> déclenche filtrage par groupe
|  |- Dependents:
|  |  - utilisé par traitement demande carburant

[CORE] Couche Données Relationnelles
|- [SUB] Database Engine (SQLite dev / MySQL prod) -> persiste dans tables métier
|  |- Dependents:
|  |  - utilisé par tous les modèles
|  |
|- [HOOK] Contraintes DB (UniqueConstraint/CheckConstraint) -> déclenche validation d'intégrité
|  |- Dependents:
|  |  - utilisé par Rechargement HT/TTC
|  |  - utilisé par Carte_Carburant (dotation active)
|  |
|- [UTILITY] Indexes ORM -> utilise accélération requêtes
|  |- Dependents:
|  |  - utilisé par demandes et dashboards
|  |
|- [UTILITY] Query Optimization (select_related/prefetch_related) -> consomme ORM QuerySet
|  |- Dependents:
|  |  - utilisé par vues de listing

[FEATURE] Gestion des Utilisateurs
|- [SUB] Profil Utilisateur (nom, email, fonction, statut) -> persiste dans Utilisateur
|  |- Dependencies:
|  |  - dépend de modèle Utilisateur
|  |- Dependents:
|  |  - utilisé par workflows carburant
|  |  - utilisé par workflows courses
|  |
|- [SUB] Gestion rôles & permissions -> utilise Groupe
|  |- Dependents:
|  |  - utilisé par toutes les règles d'accès
|  |
|- [HOOK] Session sécurisée CSRF/Cookies -> déclenche protection requêtes
|  |- Dependents:
|  |  - utilisé par formulaires Django

[FEATURE] Gestion de la Flotte
|- [SUB] Modèle Vehicule -> persiste dans Vehicule
|  |- Dependencies:
|  |  - dépend de Service
|  |- Dependents:
|  |  - utilisé par Carte_Carburant
|  |  - utilisé par Maintenance
|  |  - utilisé par DemandeCourse
|  |  - utilisé par API kilométrage
|  |
|- [SUB] Statut Disponibilité Véhicule -> utilise champ statut
|  |- Dependents:
|  |  - utilisé par planification courses
|  |
|- [SUB] Kilométrage Véhicule -> persiste dans Vehicule.kilometrage
|  |- Dependents:
|  |  - utilisé par alertes maintenance
|  |  - utilisé par exécution course

[FEATURE] Gestion Carburant
|- [SUB] Carte_Carburant -> persiste dans Carte_Carburant
|  |- Dependencies:
|  |  - dépend de Service
|  |  - dépend de Vehicule
|  |  - dépend de dotations HT/TTC
|  |- Dependents:
|  |  - utilisé par Demande_Carte_Carburant
|  |  - utilisé par API get_cartes_by_dotation
|  |  - utilisé par Rechargements
|  |
|- [SUB] Achat_Stock_Carburant_HT -> persiste dans Achat_Stock_HT
|  |- Dependents:
|  |  - utilisé par Rechargement_Carte_Carburant_HT
|  |
|- [SUB] Achat_Carburant_TTC -> persiste dans Achat_Carburant_TTC
|  |- Dependents:
|  |  - utilisé par Rechargement_Carte_Carburant_TTC
|  |
|- [SUB] Rechargement_Carte_Carburant_HT -> persiste dans Rechargement_HT
|  |- Dependencies:
|  |  - dépend de Achat_Stock_Carburant_HT
|  |  - dépend de Carte_Carburant
|  |- Dependents:
|  |  - utilisé par calcul de solde actif
|  |
|- [SUB] Rechargement_Carte_Carburant_TTC -> persiste dans Rechargement_TTC
|  |- Dependencies:
|  |  - dépend de Achat_Carburant_TTC
|  |  - dépend de Carte_Carburant
|  |- Dependents:
|  |  - utilisé par calcul de solde actif
|  |
|- [SUB] Demande_Carte_Carburant -> persiste dans Demande_Carte_Carburant
|  |- Dependencies:
|  |  - dépend de Utilisateur
|  |  - dépend de Vehicule
|  |  - dépend de Carte_Carburant
|  |- Dependents:
|  |  - utilisé par workflow validation carburant
|  |  - utilisé par générateur PDF
|  |  - utilisé par notifications emails
|  |
|- [SUB] DemandeCarteCarburantCreateForm.clean_volume_demande -> déclenche validation positive volume
|  |- Dependents:
|  |  - utilisé par création de demande carburant
|  |
|- [HOOK] notify_fuel_managers_new_request -> notifie Gestionnaires Carburant
|  |- Dependencies:
|  |  - dépend de Utilisateur(groupe)
|  |  - dépend de send_mail
|  |  - dépend de templates/emails
|  |- Dependents:
|  |  - déclenché par création Demande_Carte_Carburant
|  |
|- [HOOK] Validation Demande Carburant (Accepté/Rejeté) -> déclenche transitions de statut
|  |- Dependents:
|  |  - déclenche générateur fiche PDF
|  |  - déclenche notification driver
|  |
|- [UTILITY] generer_fiche_ravitaillement (xhtml2pdf) -> expose via PDF Binary
|  |- Dependencies:
|  |  - dépend de template fiche_ravitaillement
|  |  - dépend de xhtml2pdf
|  |- Dependents:
|  |  - utilisé par workflow carburant (demande acceptée)
|  |
|- [UTILITY] Exports carburant Excel -> expose via xlsxwriter stream
|  |- Dependents:
|  |  - utilisé par reporting carburant

[FEATURE] Gestion Maintenance
|- [SUB] TypeMaintenance -> persiste dans TypeMaintenance
|  |- Dependents:
|  |  - utilisé par Maintenance
|  |
|- [SUB] Maintenance -> persiste dans Maintenance
|  |- Dependencies:
|  |  - dépend de Vehicule
|  |  - dépend de TypeMaintenance
|  |  - dépend de Fournisseur
|  |- Dependents:
|  |  - utilisé par historique interventions
|  |  - utilisé par export maintenance Excel
|  |  - utilisé par script update_planifications
|  |
|- [SUB] Planification -> persiste dans Planification
|  |- Dependencies:
|  |  - dépend de Vehicule
|  |- Dependents:
|  |  - utilisé par workflow maintenance préventive
|  |  - utilisé par script update_planifications
|  |
|- [HOOK] Calcul échéances km/date -> déclenche statut "En alerte"
|  |- Dependencies:
|  |  - dépend de kilometrage véhicule
|  |  - dépend de date courante
|  |- Dependents:
|  |  - utilisé par alertes maintenance
|  |
|- [HOOK] Notification Driver Principal maintenance -> notifie rôle Driver Principal
|  |- Dependents:
|  |  - déclenché par seuil alerte atteint
|  |
|- [UTILITY] export_maintenance_excel -> expose via fichier XLSX
|  |- Dependencies:
|  |  - dépend de xlsxwriter
|  |- Dependents:
|  |  - utilisé par reporting maintenance
|  |
|- [HOOK] management command update_planifications.py -> déclenche recalcul échéances
|  |- Dependencies:
|  |  - dépend de Planification
|  |  - dépend de Maintenance
|  |- Dependents:
|  |  - utilisé par exploitation/automation ops

[FEATURE] Gestion des Courses
|- [SUB] DemandeCourse -> persiste dans DemandeCourse
|  |- Dependencies:
|  |  - dépend de Utilisateur demandeur
|  |  - dépend de Vehicule (contexte)
|  |- Dependents:
|  |  - utilisé par workflow de validation courses
|  |  - utilisé par planification course
|  |
|- [SUB] PlanificationCourse -> persiste dans PlanificationCourse
|  |- Dependencies:
|  |  - dépend de DemandeCourse acceptée
|  |  - dépend de Vehicule
|  |  - dépend de Chauffeur
|  |- Dependents:
|  |  - utilisé par ExecutionCourse
|  |
|- [SUB] ExecutionCourse -> persiste dans ExecutionCourse
|  |- Dependencies:
|  |  - dépend de PlanificationCourse
|  |  - dépend de kilométrage réel
|  |- Dependents:
|  |  - utilisé par clôture course
|  |
|- [HOOK] Validation responsable (accept/reject) -> déclenche changement statut demande
|  |- Dependents:
|  |  - déclenche planification ressources
|  |  - déclenche notification rejet
|  |
|- [HOOK] Attribution véhicule/chauffeur -> déclenche exécution course
|  |- Dependents:
|  |  - utilisé par workflow course
|  |
|- [HOOK] Clôture course -> déclenche statut "terminée"
|  |- Dependents:
|  |  - utilisé par reporting opérationnel

[CORE] Couche APIs Internes
|- [SUB] API get_cartes_by_dotation -> expose via HTTP JSON
|  |- Dependencies:
|  |  - dépend de Carte_Carburant
|  |  - dépend de dotation_type/dotation_id
|  |- Dependents:
|  |  - utilisé par formulaires dynamiques rechargement
|  |
|- [SUB] API get_vehicule_kilometrage -> expose via HTTP JSON
|  |- Dependencies:
|  |  - dépend de Vehicule
|  |- Dependents:
|  |  - utilisé par formulaires course/maintenance

[UTILITY] Services Transverses
|- [SUB] Notification Email Service -> consomme SMTP Backend
|  |- Dependencies:
|  |  - dépend de EMAIL_HOST config
|  |  - dépend de templates email
|  |- Dependents:
|  |  - utilisé par carburant
|  |  - utilisé par courses (rejets)
|  |  - utilisé par maintenance (alertes)
|  |
|- [SUB] PDF Service -> consomme xhtml2pdf
|  |- Dependents:
|  |  - utilisé par fiches ravitaillement
|  |
|- [SUB] Excel Service -> consomme xlsxwriter
|  |- Dependents:
|  |  - utilisé par reporting maintenance/carburant
|  |
|- [SUB] Image Service -> consomme Pillow
|  |- Dependents:
|  |  - utilisé par gestion documents/photos véhicule

---

## 2. TABLE DES RELATIONS

| FROM | TYPE | TO |
|---|---|---|
| Runtime Django FMS | utilise | fms/settings.py |
| Runtime Django FMS | utilise | fms/urls.py |
| Runtime Django FMS | dépend de | manage.py |
| fms/settings.py | dépend de | Database Engine |
| fms/settings.py | dépend de | SMTP Config |
| fms/settings.py | dépend de | Cache Redis |
| fms/urls.py | dépend de | core/urls.py |
| Utilisateur | persiste dans | Database |
| Groupe | persiste dans | Database |
| Service | persiste dans | Database |
| Contrôle d'accès vues | dépend de | login_required |
| Contrôle d'accès vues | dépend de | user_passes_test |
| user_passes_test | utilise | Groupe |
| Vehicule | persiste dans | Database |
| Vehicule | dépend de | Service |
| Carte_Carburant | persiste dans | Database |
| Carte_Carburant | dépend de | Service |
| Carte_Carburant | dépend de | Vehicule |
| Carte_Carburant | dépend de | Achat_Stock_Carburant_HT |
| Carte_Carburant | dépend de | Achat_Carburant_TTC |
| Achat_Stock_Carburant_HT | persiste dans | Database |
| Achat_Carburant_TTC | persiste dans | Database |
| Rechargement_Carte_Carburant_HT | persiste dans | Database |
| Rechargement_Carte_Carburant_HT | dépend de | Achat_Stock_Carburant_HT |
| Rechargement_Carte_Carburant_HT | dépend de | Carte_Carburant |
| Rechargement_Carte_Carburant_TTC | persiste dans | Database |
| Rechargement_Carte_Carburant_TTC | dépend de | Achat_Carburant_TTC |
| Rechargement_Carte_Carburant_TTC | dépend de | Carte_Carburant |
| Demande_Carte_Carburant | persiste dans | Database |
| Demande_Carte_Carburant | dépend de | Utilisateur |
| Demande_Carte_Carburant | dépend de | Vehicule |
| Demande_Carte_Carburant | dépend de | Carte_Carburant |
| Demande_Carte_Carburant | déclenche | notify_fuel_managers_new_request |
| Demande_Carte_Carburant | déclenche | Validation Demande Carburant |
| Validation Demande Carburant | déclenche | generer_fiche_ravitaillement |
| Validation Demande Carburant | notifie | Driver |
| notify_fuel_managers_new_request | consomme | Notification Email Service |
| notify_fuel_managers_new_request | notifie | Gestionnaires Carburant |
| DemandeCarteCarburantCreateForm | déclenche | Validation volume positif |
| generer_fiche_ravitaillement | consomme | PDF Service |
| generer_fiche_ravitaillement | expose via | PDF Binary |
| Reporting Carburant | consomme | Excel Service |
| TypeMaintenance | persiste dans | Database |
| Maintenance | persiste dans | Database |
| Maintenance | dépend de | Vehicule |
| Maintenance | dépend de | TypeMaintenance |
| Maintenance | dépend de | Fournisseur |
| Planification | persiste dans | Database |
| Planification | dépend de | Vehicule |
| Planification | déclenche | Calcul échéances km/date |
| Calcul échéances km/date | dépend de | Vehicule.kilometrage |
| Calcul échéances km/date | dépend de | Date courante |
| Calcul échéances km/date | déclenche | Notification Driver Principal maintenance |
| Notification Driver Principal maintenance | notifie | Driver Principal |
| update_planifications.py | consomme | Planification |
| update_planifications.py | consomme | Maintenance |
| update_planifications.py | déclenche | Recalcul échéances |
| export_maintenance_excel | consomme | Excel Service |
| export_maintenance_excel | expose via | Fichier XLSX |
| DemandeCourse | persiste dans | Database |
| DemandeCourse | dépend de | Utilisateur |
| DemandeCourse | dépend de | Vehicule |
| DemandeCourse | déclenche | Validation responsable course |
| Validation responsable course | déclenche | PlanificationCourse |
| Validation responsable course | notifie | Demandeur (si rejet) |
| PlanificationCourse | persiste dans | Database |
| PlanificationCourse | dépend de | DemandeCourse |
| PlanificationCourse | dépend de | Vehicule |
| PlanificationCourse | dépend de | Chauffeur |
| PlanificationCourse | déclenche | ExecutionCourse |
| ExecutionCourse | persiste dans | Database |
| ExecutionCourse | dépend de | PlanificationCourse |
| ExecutionCourse | dépend de | Kilométrage réel |
| ExecutionCourse | déclenche | Clôture course |
| Clôture course | déclenche | Statut terminée |
| API get_cartes_by_dotation | expose via | HTTP JSON |
| API get_cartes_by_dotation | consomme | Carte_Carburant |
| API get_vehicule_kilometrage | expose via | HTTP JSON |
| API get_vehicule_kilometrage | consomme | Vehicule |
| Dashboard carburant | consomme | Cache Redis |
| Vues listing demands | consomme | Query Optimization ORM |
| Query Optimization ORM | dépend de | select_related/prefetch_related |
| Contraintes DB | déclenche | Validation intégrité données |
| Contraintes DB | dépend de | UniqueConstraint |
| Contraintes DB | dépend de | CheckConstraint |
| Notification Email Service | dépend de | SMTP Config |
| Notification Email Service | consomme | Templates Email |
| PDF Service | dépend de | xhtml2pdf |
| Excel Service | dépend de | xlsxwriter |
| Image Service | dépend de | Pillow |

---

## 3. FICHIERS CRITIQUES PAR FONCTIONNALITÉ

[CORE] Configuration & Runtime
- fms/settings.py
- fms/urls.py
- fms/wsgi.py
- manage.py
- requirements.txt

[CORE] Authentification & Autorisation
- core/models.py (Utilisateur, Groupe, Service)
- core/forms.py (auth/forms métier)
- core/views.py (login/logout + guards)
- core/admin.py
- templates/core/login.html

[FEATURE] Gestion Utilisateurs
- core/models.py
- core/forms.py
- core/views_admin.py
- templates/core/users/*.html

[FEATURE] Gestion Flotte
- core/models.py (Vehicule)
- core/forms.py
- core/views.py
- core/views_admin.py
- templates/core/vehicules/*.html

[FEATURE] Gestion Carburant
- core/models.py (Carte_Carburant, Achat/Rechargements, Demande_Carte_Carburant)
- core/forms.py (DemandeCarteCarburantCreateForm)
- core/views.py
- core/utils.py (fiche PDF, helpers)
- core/urls.py
- templates/core/carburant/*.html
- templates/core/fiche_ravitaillement.html
- templates/emails/nouvelle_demande.html

[FEATURE] Gestion Maintenance
- core/models.py (TypeMaintenance, Maintenance, Planification)
- core/forms.py
- core/views.py / core/views_admin.py
- core/utils.py (export_maintenance_excel)
- core/management/commands/update_planifications.py
- templates/core/maintenance/*.html

[FEATURE] Gestion Courses
- core/models.py (DemandeCourse, PlanificationCourse, ExecutionCourse)
- core/forms.py
- core/views.py
- core/views_execution_course.py
- core/views_admin.py
- core/urls.py
- templates/core/courses/*.html
- templates/core/execution_course_form.html

[FEATURE] API Interne & Intégrations
- core/urls.py (routes API)
- core/views.py (get_cartes_by_dotation, get_vehicule_kilometrage)
- core/utils.py

[UTILITY] Reporting & Export
- core/utils.py (PDF, Excel)
- templates/core/*.html (templates de rapports)
- static/ (assets export/branding)

[UTILITY] Monitoring / Logs / Performance
- fms/settings.py (LOGGING, CACHES)
- core/views.py (logs événementiels)
- core/tests.py

---

## 4. ANALYSE SYSTÈME

### 4.1 Points de couplage fort
1. **`core/models.py` monolithique**: concentre toutes les entités métier (auth, carburant, maintenance, courses), ce qui augmente l'impact des changements transverses.
2. **`core/views.py` potentiellement surchargé**: mélange logique UI, workflows métier, APIs JSON et triggers de notification.
3. **Carburant fortement couplé à Véhicule + Carte + Dotations + Notifications + PDF**: une modification de règles carburant propage des effets en chaîne.
4. **Workflows pilotés par statuts en texte** (`soumise`, `acceptée`, etc.): risque de dérive d'états si les transitions ne sont pas centralisées.

### 4.2 Risques architecturaux
1. **Risque d'incohérence transactionnelle** sur les soldes cartes/dotations si validation, PDF et notifications ne sont pas orchestrés en transaction atomique.
2. **Risque de duplication de règles d'accès** si les checks groupe sont dispersés dans les vues.
3. **Risque de dette technique sur automations** (scripts management command + hooks dans vues) sans scheduler central explicite.
4. **Observabilité partielle**: logging fichier local (`debug.log`) sans pipeline central (ELK/Cloud logging).

### 4.3 Bottlenecks potentiels
1. **Exports PDF/Excel synchrones**: blocage de requêtes HTTP sur gros volumes.
2. **Notifications email synchrones** dans les workflows de validation: latence utilisateur et fragilité en cas d'indisponibilité SMTP.
3. **Requêtes multi-relations** (carburant/maintenance) sans systématisation de `select_related/prefetch_related`.
4. **Dashboard stats** dépendant de cache Redis non garanti en environnement minimal.

### 4.4 Opportunités d’APIisation (REST/GraphQL)
1. **Domain API Carburant**: endpoints versionnés (`/api/v1/fuel/*`) pour demandes, validations, soldes, rechargements.
2. **Domain API Maintenance**: endpoints pour échéances, alertes, interventions, fournisseurs.
3. **Domain API Courses**: endpoints workflow-driven avec transitions d'état explicites.
4. **API Auth/Roles**: exposition claire des permissions effectives par utilisateur pour clients web/mobile.
5. **GraphQL Gateway** (option): utile pour dashboards croisant carburant + maintenance + courses avec un seul round-trip.

### 4.5 Composants critiques à isoler (candidats microservices)
1. **Service Notifications** (email/events): extraire vers worker asynchrone (Celery/RQ) + retries.
2. **Service Reporting** (PDF/Excel): génération asynchrone + stockage objet + URL de téléchargement.
3. **Service Workflow Engine** (statuts & transitions): centraliser les règles métier de carburant/courses/maintenance.
4. **Service Fleet Telemetry** (futur): isolation naturelle pour GPS, kilométrage temps réel, prédiction maintenance.

### 4.6 Priorités de refactoring (ordre recommandé)
1. **Centraliser les transitions de statut** dans des services métier dédiés.
2. **Externaliser notifications et exports en asynchrone**.
3. **Découper `core` par domaines** (`core_fuel`, `core_maintenance`, `core_trip`, `core_identity`) en conservant un monolithe modulaire.
4. **Renforcer tests de non-régression workflow** (carburant/courses/maintenance).
5. **Ajouter métriques techniques** (temps de requête, taux d'échec email, durée génération rapports).
