-- ============================================
-- Projet pédagogique SQL - Assurance habitation
-- Script 04 : import de Contrat+.csv dans CONTRAT
-- ============================================
-- Recommandation dans ce projet :
-- 1) créer les tables avec 01_create_tables.sql ;
-- 2) créer GEO_SOURCE avec 02_create_geo_source.sql ;
-- 3) importer manuellement Region+.csv dans GEO_SOURCE depuis IntelliJ ;
-- 4) exécuter 03_insert_geo.sql ;
-- 5) importer manuellement Contrat+.csv dans CONTRAT_SOURCE depuis IntelliJ ;
-- 6) exécuter ce script pour alimenter CONTRAT sans bloquer sur la FK.
--
-- Ce fichier documente l'ordre d'exécution et propose, si LOCAL INFILE
-- est activé dans votre environnement, une commande optionnelle.
-- L'import manuel via IntelliJ reste l'option de référence.
--
-- Pourquoi passer par CONTRAT_SOURCE ?
-- Certaines lignes du fichier Contrat+.csv contiennent un code de commune
-- absent du référentiel Region+.csv (exemple observé : 97434, 97460, 97470).
-- Un import direct dans CONTRAT échoue alors sur fk_contrat_commune.
-- La table tampon permet :
-- - de contrôler ces écarts ;
-- - d'ajouter si besoin une commune technique rattachée au bon département ;
-- - puis d'insérer les contrats dans la table finale.

DROP TABLE IF EXISTS CONTRAT_SOURCE;

CREATE TABLE CONTRAT_SOURCE (
    Contrat_ID INT,
    No_voie VARCHAR(10),
    B_T_Q VARCHAR(5),
    Type_de_voie VARCHAR(50),
    Voie VARCHAR(100),
    Code_dep_code_commune VARCHAR(10),
    Code_postal VARCHAR(10),
    Surface INT,
    Type_local VARCHAR(50),
    Occupation VARCHAR(50),
    Type_contrat VARCHAR(100),
    Formule VARCHAR(50),
    Valeur_declaree_biens VARCHAR(50),
    Prix_cotisation_mensuel INT
);

-- Exemple optionnel si LOCAL INFILE est autorisé :
-- LOAD DATA LOCAL INFILE 'C:/chemin/vers/Contrat+.csv'
-- INTO TABLE CONTRAT_SOURCE
-- CHARACTER SET utf8mb4
-- FIELDS TERMINATED BY ';'
-- OPTIONALLY ENCLOSED BY '"'
-- LINES TERMINATED BY '\n'
-- IGNORE 1 LINES
-- (Contrat_ID, No_voie, B_T_Q, Type_de_voie, Voie,
--  Code_dep_code_commune, Code_postal, Surface, Type_local,
--  Occupation, Type_contrat, Formule, Valeur_declaree_biens,
--  Prix_cotisation_mensuel);

-- Après l'import manuel de Contrat+.csv dans CONTRAT_SOURCE :
-- 1) identifier les codes de commune absents du référentiel ;
SELECT DISTINCT cs.Code_dep_code_commune
FROM CONTRAT_SOURCE cs
LEFT JOIN COMMUNE c
    ON c.Code_dep_code_commune = TRIM(cs.Code_dep_code_commune)
WHERE cs.Code_dep_code_commune IS NOT NULL
  AND TRIM(cs.Code_dep_code_commune) <> ''
  AND c.Code_dep_code_commune IS NULL
ORDER BY cs.Code_dep_code_commune;

-- 2) créer automatiquement une commune technique pour les codes absents.
-- La logique de rattachement du département est la plus simple possible :
-- - codes métropole/corse : 2 premiers caractères ;
-- - codes outre-mer commençant par 97 ou 98 : 3 premiers caractères.
-- Cette correction permet de conserver la FK et de charger les contrats.
INSERT INTO COMMUNE (Code_dep_code_commune, com_nom_maj_court, dep_code)
SELECT src.Code_dep_code_commune,
       CONCAT('COMMUNE A COMPLETER - ', src.Code_dep_code_commune) AS com_nom_maj_court,
       src.dep_code_calcule
FROM (
    SELECT DISTINCT TRIM(cs.Code_dep_code_commune) AS Code_dep_code_commune,
           CASE
               WHEN TRIM(cs.Code_dep_code_commune) REGEXP '^(97|98)' THEN LEFT(TRIM(cs.Code_dep_code_commune), 3)
               ELSE LEFT(TRIM(cs.Code_dep_code_commune), 2)
           END AS dep_code_calcule
    FROM CONTRAT_SOURCE cs
    WHERE cs.Code_dep_code_commune IS NOT NULL
      AND TRIM(cs.Code_dep_code_commune) <> ''
) AS src
INNER JOIN DEPARTEMENT d
    ON d.dep_code = src.dep_code_calcule
LEFT JOIN COMMUNE c
    ON c.Code_dep_code_commune = src.Code_dep_code_commune
WHERE c.Code_dep_code_commune IS NULL;

-- 3) insérer les contrats dans la table finale, sans doublon si le script
-- est relancé après correction ou réimport.
INSERT INTO CONTRAT (
    Contrat_ID, No_voie, B_T_Q, Type_de_voie, Voie,
    Code_dep_code_commune, Code_postal, Surface, Type_local,
    Occupation, Type_contrat, Formule, Valeur_declaree_biens,
    Prix_cotisation_mensuel
)
SELECT cs.Contrat_ID, cs.No_voie, cs.B_T_Q, cs.Type_de_voie, cs.Voie,
       TRIM(cs.Code_dep_code_commune), cs.Code_postal, cs.Surface, cs.Type_local,
       cs.Occupation, cs.Type_contrat, cs.Formule, cs.Valeur_declaree_biens,
       cs.Prix_cotisation_mensuel
FROM CONTRAT_SOURCE cs
INNER JOIN COMMUNE c
    ON c.Code_dep_code_commune = TRIM(cs.Code_dep_code_commune)
LEFT JOIN CONTRAT ct
    ON ct.Contrat_ID = cs.Contrat_ID
WHERE ct.Contrat_ID IS NULL;

SELECT 'Importer manuellement Contrat+.csv dans CONTRAT_SOURCE via IntelliJ, puis exécuter tout le script 04_import_contrat.sql.' AS instruction_import;
