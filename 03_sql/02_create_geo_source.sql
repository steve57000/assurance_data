-- ============================================
-- Projet pédagogique SQL - Assurance habitation
-- Script 02 : création de la table tampon GEO_SOURCE
-- Cette table sert à importer Region+.csv avant répartition
-- dans REGION, DEPARTEMENT et COMMUNE.
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
