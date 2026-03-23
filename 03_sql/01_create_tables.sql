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

CREATE INDEX idx_contrat_formule
    ON CONTRAT(Formule);

CREATE INDEX idx_contrat_type_local
    ON CONTRAT(Type_local);
