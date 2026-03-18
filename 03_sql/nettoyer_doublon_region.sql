-- ============================================
-- 1. TABLE TAMPON POUR LE FICHIER GEOGRAPHIQUE
-- ============================================
DROP TABLE IF EXISTS GEO_SOURCE;

CREATE TABLE GEO_SOURCE (
    Code_dep_code_commune VARCHAR(10),
    reg_code VARCHAR(10),
    reg_nom VARCHAR(100),
    aca_nom VARCHAR(100),
    dep_nom VARCHAR(100),
    com_nom_maj_court VARCHAR(100),
    dep_code VARCHAR(10),
    dep_nom_num VARCHAR(100)
);

-- ============================================
-- 2. INSERTIONS DANS LES TABLES NORMALISEES
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
  AND dep_code <> '';

INSERT INTO COMMUNE (Code_dep_code_commune, com_nom_maj_court, dep_code)
SELECT DISTINCT Code_dep_code_commune, com_nom_maj_court, dep_code
FROM GEO_SOURCE
WHERE Code_dep_code_commune IS NOT NULL
  AND Code_dep_code_commune <> '';

-- ============================================
-- 3. VERIFICATIONS
-- ============================================
SELECT COUNT(*) AS nb_regions FROM REGION;
SELECT COUNT(*) AS nb_departements FROM DEPARTEMENT;
SELECT COUNT(*) AS nb_communes FROM COMMUNE;
SELECT COUNT(*) AS nb_contrats FROM CONTRAT;
