-- ============================================
-- Projet pédagogique SQL - Assurance habitation
-- Script 05 : contrôles après import
-- ============================================

-- Volumes par table
SELECT COUNT(*) AS nb_regions FROM REGION;
SELECT COUNT(*) AS nb_departements FROM DEPARTEMENT;
SELECT COUNT(*) AS nb_communes FROM COMMUNE;
SELECT COUNT(*) AS nb_contrats FROM CONTRAT;
SELECT COUNT(*) AS nb_contrats_source FROM CONTRAT_SOURCE;

-- Aperçu des données chargées
SELECT * FROM REGION LIMIT 5;
SELECT * FROM DEPARTEMENT LIMIT 5;
SELECT * FROM COMMUNE LIMIT 5;
SELECT * FROM CONTRAT LIMIT 5;

-- Vérification des valeurs utiles pour les requêtes métier
SELECT DISTINCT Type_local FROM CONTRAT ORDER BY Type_local;
SELECT DISTINCT Formule FROM CONTRAT ORDER BY Formule;
SELECT DISTINCT Occupation FROM CONTRAT ORDER BY Occupation;
SELECT DISTINCT Valeur_declaree_biens FROM CONTRAT ORDER BY Valeur_declaree_biens;

-- Vérification des éventuels écarts de référentiel encore présents
SELECT DISTINCT cs.Code_dep_code_commune
FROM CONTRAT_SOURCE cs
LEFT JOIN COMMUNE c
    ON c.Code_dep_code_commune = TRIM(cs.Code_dep_code_commune)
WHERE cs.Code_dep_code_commune IS NOT NULL
  AND TRIM(cs.Code_dep_code_commune) <> ''
  AND c.Code_dep_code_commune IS NULL
ORDER BY cs.Code_dep_code_commune;

-- Vérification des communes techniques ajoutées pour sécuriser la FK
SELECT Code_dep_code_commune, com_nom_maj_court, dep_code
FROM COMMUNE
WHERE com_nom_maj_court LIKE 'COMMUNE A COMPLETER - %'
ORDER BY Code_dep_code_commune;
