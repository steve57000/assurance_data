-- ============================================
-- Projet pédagogique SQL - Assurance habitation
-- Script 03 : alimentation des tables géographiques normalisées
-- Pré-requis : Region+.csv déjà importé dans GEO_SOURCE
-- via l'outil d'import IntelliJ ou une autre méthode compatible.
-- Ce script est idempotent : il peut être relancé sans provoquer
-- d'erreur de doublon sur les clés primaires.
-- ============================================

INSERT INTO REGION (reg_code, reg_nom, aca_nom)
SELECT src.reg_code, src.reg_nom, src.aca_nom
FROM (
    SELECT TRIM(reg_code) AS reg_code,
           MIN(TRIM(reg_nom)) AS reg_nom,
           MIN(NULLIF(TRIM(aca_nom), '')) AS aca_nom
    FROM GEO_SOURCE
    WHERE reg_code IS NOT NULL
      AND TRIM(reg_code) <> ''
      AND reg_nom IS NOT NULL
      AND TRIM(reg_nom) <> ''
    GROUP BY TRIM(reg_code)
) AS src
WHERE NOT EXISTS (
    SELECT 1
    FROM REGION r
    WHERE r.reg_code = src.reg_code
);

INSERT INTO DEPARTEMENT (dep_code, dep_nom, dep_nom_num, reg_code)
SELECT src.dep_code, src.dep_nom, src.dep_nom_num, src.reg_code
FROM (
    SELECT TRIM(dep_code) AS dep_code,
           MIN(TRIM(dep_nom)) AS dep_nom,
           MIN(NULLIF(TRIM(dep_nom_num), '')) AS dep_nom_num,
           MIN(TRIM(reg_code)) AS reg_code
    FROM GEO_SOURCE
    WHERE dep_code IS NOT NULL
      AND TRIM(dep_code) <> ''
      AND dep_nom IS NOT NULL
      AND TRIM(dep_nom) <> ''
      AND reg_code IS NOT NULL
      AND TRIM(reg_code) <> ''
    GROUP BY TRIM(dep_code)
) AS src
WHERE NOT EXISTS (
    SELECT 1
    FROM DEPARTEMENT d
    WHERE d.dep_code = src.dep_code
);

INSERT INTO COMMUNE (Code_dep_code_commune, com_nom_maj_court, dep_code)
SELECT src.Code_dep_code_commune, src.com_nom_maj_court, src.dep_code
FROM (
    SELECT TRIM(Code_dep_code_commune) AS Code_dep_code_commune,
           MIN(TRIM(com_nom_maj_court)) AS com_nom_maj_court,
           MIN(TRIM(dep_code)) AS dep_code
    FROM GEO_SOURCE
    WHERE Code_dep_code_commune IS NOT NULL
      AND TRIM(Code_dep_code_commune) <> ''
      AND com_nom_maj_court IS NOT NULL
      AND TRIM(com_nom_maj_court) <> ''
      AND dep_code IS NOT NULL
      AND TRIM(dep_code) <> ''
    GROUP BY TRIM(Code_dep_code_commune)
) AS src
WHERE NOT EXISTS (
    SELECT 1
    FROM COMMUNE c
    WHERE c.Code_dep_code_commune = src.Code_dep_code_commune
);
