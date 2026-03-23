# Projet SQL - document technique

## 1. Contexte et objectif
Ce document synthétise le projet SQL d'analyse de contrats d'assurance habitation à partir de deux sources CSV : un fichier contrat et un référentiel géographique. L'objectif est de construire une base normalisée, charger les données et répondre à des questions métier simples.

## 2. Exploration des données
- Source 1 : `Contrat+.csv` avec 30335 lignes chargées dans `CONTRAT_SOURCE`.
- Source 2 : `Region+.csv` transformée en 19 régions, 109 départements et 38919 communes.
- Points d'attention : codes INSEE texte, valeurs catégorielles, 3 codes de communes absents du référentiel (`97434`, `97460`, `97470`).

### Zone capture 1
> Insérer ici une capture du dictionnaire des données Excel complété.

## 3. Schéma relationnel modifié
Le modèle final suit la chaîne `REGION -> DEPARTEMENT -> COMMUNE -> CONTRAT` et s'appuie sur une table tampon `GEO_SOURCE` ainsi qu'une table technique `CONTRAT_SOURCE` pour sécuriser l'import.

### Zone capture 2
> Insérer ici la capture du schéma relationnel modifié dans SQL Power Architect.

## 4. Code SQL générant les tables
Le script principal est `03_sql/01_create_tables.sql`. Les tables tampon et les scripts d'alimentation complètent la création.

```sql
-- ============================================
-- Projet pédagogique SQL - Assurance habitation
-- Script 01 : création des tables normalisées
-- Compatible MySQL 8.0
-- ============================================

-- Suppression dans l'ordre inverse des dépendances
DROP TABLE IF EXISTS CONTRAT;
DROP TABLE IF EXISTS GEO_SOURCE;
DROP TABLE IF EXISTS COMMUNE;
DROP TABLE IF EXISTS DEPARTEMENT;
DROP TABLE IF EXISTS REGION;

CREATE TABLE REGION (
    reg_code VARCHAR(10) PRIMARY KEY,
    reg_nom VARCHAR(100) NOT NULL,
    aca_nom VARCHAR(100)
);

CREATE TABLE DEPARTEMENT (
    dep_code VARCHAR(10) PRIMARY KEY,
    dep_nom VARCHAR(100) NOT NULL,
    dep_nom_num VARCHAR(100),
    reg_code VARCHAR(10) NOT NULL,
    CONSTRAINT fk_departement_region
        FOREIGN KEY (reg_code) REFERENCES REGION(reg_code)
);

CREATE TABLE COMMUNE (
    Code_dep_code_commune VARCHAR(10) PRIMARY KEY,
    com_nom_maj_court VARCHAR(100) NOT NULL,
    dep_code VARCHAR(10) NOT NULL,
    CONSTRAINT fk_commune_departement
        FOREIGN KEY (dep_code) REFERENCES DEPARTEMENT(dep_code)
);

CREATE TABLE CONTRAT (
    Contrat_ID INT PRIMARY KEY,
    No_voie VARCHAR(10),
    B_T_Q VARCHAR(5),
    Type_de_voie VARCHAR(50),
    Voie VARCHAR(100),
    Code_dep_code_commune VARCHAR(10) NOT NULL,
    Code_postal VARCHAR(10),
    Surface INT NOT NULL,
    Type_local VARCHAR(50),
    Occupation VARCHAR(50),
    Type_contrat VARCHAR(100),
    Formule VARCHAR(50),
    Valeur_declaree_biens VARCHAR(50),
    Prix_cotisation_mensuel INT,
    CONSTRAINT fk_contrat_commune
        FOREIGN KEY (Code_dep_code_commune) REFERENCES COMMUNE(Code_dep_code_commune)
);

-- Index utiles pour les jointures et analyses demandées
CREATE INDEX idx_departement_reg_code
    ON DEPARTEMENT(reg_code);

CREATE INDEX idx_commune_dep_code
    ON COMMUNE(dep_code);

CREATE INDEX idx_contrat_code_commune
    ON CONTRAT(Code_dep_code_commune);

CREATE INDEX idx_contrat_code_postal
    ON CONTRAT(Code_postal);

CREATE INDEX idx_contrat_surface
    ON CONTRAT(Surface);
```

## 5. Base chargée
Les volumes chargés sont les suivants.

| Table | Volume |
|---|---:|
| REGION | 19 |
| DEPARTEMENT | 109 |
| COMMUNE | 38919 |
| CONTRAT | 30335 |
| CONTRAT_SOURCE | 30335 |

### Zone capture 3
> Insérer ici une capture de la base de données chargée (vue tables + extrait de données).

## 6. Liste complète des analyses et résultats associés

### Requête 1 - Top 5 des plus grandes surfaces
| Contrat_ID | Surface |
|---|---:|
| 104211 | 815 |
| 105463 | 742 |
| 130878 | 595 |
| 100822 | 570 |
| 109872 | 559 |

### Requête 2 - Prix moyen de la cotisation mensuelle
Résultat : **19.33 EUR/mois**.

### Requête 3 - Contrats par valeur déclarée des biens
- 0-25000 : 22720
- 25000-50000 : 6815
- 50000-100000 : 696
- 100000+ : 104

### Requête 4 - Nombre de formules Integral en Pays de la Loire
Résultat : **589 contrats**.

### Requête 5 - Maisons du département 71
| Contrat_ID | Type_contrat | Formule |
|---|---|---|
| 114768 | Residence principale | Integral |
| 114779 | Residence principale | Classique |
| 114782 | Residence principale | Classique |
| 114812 | Residence principale | Integral |

### Requête 6 - Surface moyenne à Paris
Résultat : **51.77 m2**.

### Requête 7 - Top 10 des départements au prix moyen le plus élevé
| Dep | Nom | Prix moyen |
|---|---|---:|
| 75 | Paris | 36.4 |
| 92 | Hauts-de-Seine | 26.27 |
| 94 | Val-de-Marne | 19.82 |
| 78 | Yvelines | 18.89 |
| 69 | Rhône | 18.49 |
| 1 | Ain | 18.24 |
| 6 | Alpes-Maritimes | 18.14 |
| 17 | Charente-Maritime | 17.32 |
| 74 | Haute-Savoie | 17.15 |
| 2A | Corse-du-Sud | 17.07 |

### Requête 8 - Communes avec au moins 150 contrats
| Code commune | Commune | Contrats |
|---|---|---:|
| 75118 | PARIS 18 | 515 |
| 75117 | PARIS 17 | 468 |
| 75115 | PARIS 15 | 407 |
| 75116 | PARIS 16 | 394 |
| 6088 | NICE | 387 |
| 75111 | PARIS 11 | 381 |
| 33063 | BORDEAUX | 302 |
| 75120 | PARIS 20 | 302 |
| 44109 | NANTES | 291 |
| 75119 | PARIS 19 | 266 |

### Requête 9 - Nombre de contrats par région
| Reg | Région | Contrats |
|---|---|---:|
| 11 | Ile-de-France | 14177 |
| 93 | Provence-Alpes-Côte d'Azur | 3279 |
| 84 | Auvergne-Rhône-Alpes | 3042 |
| 75 | Nouvelle-Aquitaine | 2038 |
| 76 | Occitanie | 1609 |
| 52 | Pays de la Loire | 1196 |
| 32 | Hauts-de-France | 1189 |
| 53 | Bretagne | 947 |

## 7. Méthodologie suivie
1. Lecture des fichiers CSV et exploration des colonnes.
2. Construction du dictionnaire des données.
3. Normalisation en 4 tables métier + tables tampon d'import.
4. Création des scripts SQL, import et contrôle qualité.
5. Exécution des requêtes d'analyse et interprétation des résultats.

## 8. Conclusion
Le projet aboutit à une base relationnelle propre, exploitable et cohérente avec les besoins d'analyse métier. La concentration des contrats en Ile-de-France et la surreprésentation des appartements ressortent nettement.
