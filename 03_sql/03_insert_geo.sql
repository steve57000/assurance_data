-- ============================================
-- Projet pédagogique SQL - Assurance habitation
-- Script 03 : alimentation des tables géographiques normalisées
-- Pré-requis : Region+.csv déjà importé dans GEO_SOURCE
-- via l'outil d'import IntelliJ ou une autre méthode compatible.
-- ============================================

INSERT INTO REGION (reg_code, reg_nom, aca_nom)
SELECT DISTINCT reg_code, reg_nom, aca_nom
FROM GEO_SOURCE
WHERE reg_code IS NOT NULL
  AND reg_code <> '';

INSERT INTO DEPARTEMENT (dep_code, dep_nom, dep_nom_num, reg_code)
SELECT DISTINCT dep_code, dep_nom, dep_nom_num, reg_code
FROM GEO_SOURCE
WHERE dep_code IS NOT NULL
  AND dep_code <> ''
  AND reg_code IS NOT NULL
  AND reg_code <> '';

INSERT INTO COMMUNE (Code_dep_code_commune, com_nom_maj_court, dep_code)
SELECT DISTINCT Code_dep_code_commune, com_nom_maj_court, dep_code
FROM GEO_SOURCE
WHERE Code_dep_code_commune IS NOT NULL
  AND Code_dep_code_commune <> ''
  AND dep_code IS NOT NULL
  AND dep_code <> '';
