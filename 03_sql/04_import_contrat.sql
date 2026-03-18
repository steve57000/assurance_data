-- ============================================
-- Projet pédagogique SQL - Assurance habitation
-- Script 04 : import de Contrat+.csv dans CONTRAT
-- ============================================
-- Recommandation dans ce projet :
-- 1) créer les tables avec 01_create_tables.sql ;
-- 2) créer GEO_SOURCE avec 02_create_geo_source.sql ;
-- 3) importer manuellement Region+.csv dans GEO_SOURCE depuis IntelliJ ;
-- 4) exécuter 03_insert_geo.sql ;
-- 5) importer manuellement Contrat+.csv dans CONTRAT depuis IntelliJ.
--
-- Ce fichier documente l'ordre d'exécution et propose, si LOCAL INFILE
-- est activé dans votre environnement, une commande optionnelle.
-- L'import manuel via IntelliJ reste l'option de référence.

-- Exemple optionnel si LOCAL INFILE est autorisé :
-- LOAD DATA LOCAL INFILE 'C:/chemin/vers/Contrat+.csv'
-- INTO TABLE CONTRAT
-- CHARACTER SET utf8mb4
-- FIELDS TERMINATED BY ';'
-- OPTIONALLY ENCLOSED BY '"'
-- LINES TERMINATED BY '\n'
-- IGNORE 1 LINES
-- (Contrat_ID, No_voie, B_T_Q, Type_de_voie, Voie,
--  Code_dep_code_commune, Code_postal, Surface, Type_local,
--  Occupation, Type_contrat, Formule, Valeur_declaree_biens,
--  Prix_cotisation_mensuel);

SELECT 'Importer manuellement Contrat+.csv dans la table CONTRAT via IntelliJ si LOCAL INFILE est désactivé.' AS instruction_import;
