
CREATE TABLE REGION (
                reg_code VARCHAR(10) NOT NULL,
                reg_nom VARCHAR(100) NOT NULL,
                aca_nom VARCHAR(100),
                PRIMARY KEY (reg_code)
);


CREATE TABLE DEPARTEMENT (
                dep_code VARCHAR(10) NOT NULL,
                reg_code VARCHAR(10) NOT NULL,
                dep_nom VARCHAR(100) NOT NULL,
                dep_nom_num VARCHAR(100),
                PRIMARY KEY (dep_code)
);


CREATE TABLE COMMUNE (
                Code_dep_code_commune VARCHAR(10) NOT NULL,
                dep_code VARCHAR(10) NOT NULL,
                com_nom_maj_court VARCHAR(100) NOT NULL,
                PRIMARY KEY (Code_dep_code_commune)
);


CREATE TABLE CONTRAT (
                Contrat_ID INT NOT NULL,
                Code_dep_code_commune VARCHAR(10) NOT NULL,
                No_voie VARCHAR(10),
                B_T_Q VARCHAR(5),
                Type_contrat VARCHAR(100),
                Voie VARCHAR(100),
                Type_de_voie VARCHAR(50),
                Type_local VARCHAR(50),
                Valeur_declaree_biens VARCHAR(50),
                Prix_cotisation_mensuel INT NOT NULL,
                Occupation VARCHAR(50),
                Formule VARCHAR(50),
                Code_postal VARCHAR(10),
                Surface INT NOT NULL,
                PRIMARY KEY (Contrat_ID)
);


ALTER TABLE DEPARTEMENT ADD CONSTRAINT region_departement_fk
FOREIGN KEY (reg_code)
REFERENCES REGION (reg_code)
ON DELETE NO ACTION
ON UPDATE NO ACTION;

ALTER TABLE COMMUNE ADD CONSTRAINT departement_commune_fk
FOREIGN KEY (dep_code)
REFERENCES DEPARTEMENT (dep_code)
ON DELETE NO ACTION
ON UPDATE NO ACTION;

ALTER TABLE CONTRAT ADD CONSTRAINT commune_contrat_fk
FOREIGN KEY (Code_dep_code_commune)
REFERENCES COMMUNE (Code_dep_code_commune)
ON DELETE NO ACTION
ON UPDATE NO ACTION;
