-- ============================================
-- Projet pédagogique SQL - Assurance habitation
-- Script 05 : contrôles après import
-- ============================================

-- Volumes par table
SELECT COUNT(*) AS nb_regions FROM REGION;
SELECT COUNT(*) AS nb_departements FROM DEPARTEMENT;
SELECT COUNT(*) AS nb_communes FROM COMMUNE;
SELECT COUNT(*) AS nb_contrats FROM CONTRAT;

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
