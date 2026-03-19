-- ============================================
-- Projet pédagogique SQL - Assurance habitation
-- Script 06 : requêtes d'analyse demandées
-- Les jointures suivent le schéma normalisé :
-- CONTRAT -> COMMUNE -> DEPARTEMENT -> REGION
-- ============================================

-- Requête 4
-- Quels sont les 5 contrats qui ont les surfaces les plus élevées ?
SELECT Contrat_ID, Surface
FROM CONTRAT
WHERE Surface IS NOT NULL
ORDER BY Surface DESC
LIMIT 5;

-- Requête 5
-- Quel est le prix moyen de la cotisation mensuelle ?
SELECT AVG(Prix_cotisation_mensuel) AS prix_moyen_cotisation
FROM CONTRAT;

-- Requête 6
-- Quel est le nombre de contrats pour chaque catégorie de prix
-- de la valeur déclarée des biens ?
SELECT Valeur_declaree_biens, COUNT(*) AS nombre_contrats
FROM CONTRAT
GROUP BY Valeur_declaree_biens
ORDER BY nombre_contrats DESC;

-- Requête 7
-- Quel est le nombre de formules Integral sur la région Pays de la Loire ?
SELECT COUNT(*) AS nb_formules_integral_pays_de_la_loire
FROM CONTRAT c
INNER JOIN COMMUNE co
    ON c.Code_dep_code_commune = co.Code_dep_code_commune
INNER JOIN DEPARTEMENT d
    ON co.dep_code = d.dep_code
INNER JOIN REGION r
    ON d.reg_code = r.reg_code
WHERE c.Formule = 'Integral'
  AND r.reg_nom = 'Pays de la Loire';

-- Requête 8
-- Lister les numéros de contrats avec le type de contrat et leur formule
-- pour les maisons du département 71.
SELECT c.Contrat_ID, c.Type_contrat, c.Formule
FROM CONTRAT c
INNER JOIN COMMUNE co
    ON c.Code_dep_code_commune = co.Code_dep_code_commune
INNER JOIN DEPARTEMENT d
    ON co.dep_code = d.dep_code
WHERE c.Type_local = 'Maison'
  AND d.dep_code = '71'
ORDER BY c.Contrat_ID;

-- Requête 9
-- Quelle est la surface moyenne des contrats à Paris ?
-- Remarque : dans Region+.csv, les contrats parisiens sont rattachés aux arrondissements
-- (PARIS  1 à PARIS 20, codes 75101 à 75120), pas à la commune globale PARIS
SELECT AVG(c.Surface) AS surface_moyenne_paris
FROM CONTRAT c
INNER JOIN COMMUNE co
    ON c.Code_dep_code_commune = co.Code_dep_code_commune
WHERE co.dep_code = '75'
  AND co.com_nom_maj_court LIKE 'PARIS%';

-- Requête 10
-- Classement des 10 départements où le prix moyen de la cotisation est le plus élevé.
SELECT d.dep_code,
       d.dep_nom,
       AVG(c.Prix_cotisation_mensuel) AS prix_moyen_cotisation
FROM CONTRAT c
INNER JOIN COMMUNE co
    ON c.Code_dep_code_commune = co.Code_dep_code_commune
INNER JOIN DEPARTEMENT d
    ON co.dep_code = d.dep_code
GROUP BY d.dep_code, d.dep_nom
ORDER BY prix_moyen_cotisation DESC
LIMIT 10;

-- Requête 11
-- Liste des communes ayant eu au moins 150 contrats.
SELECT co.Code_dep_code_commune,
       co.com_nom_maj_court,
       COUNT(*) AS nombre_contrats
FROM CONTRAT c
INNER JOIN COMMUNE co
    ON c.Code_dep_code_commune = co.Code_dep_code_commune
GROUP BY co.Code_dep_code_commune, co.com_nom_maj_court
HAVING COUNT(*) >= 150
ORDER BY nombre_contrats DESC;

-- Requête 12
-- Quel est le nombre de contrats pour chaque région ?
SELECT r.reg_code,
       r.reg_nom,
       COUNT(*) AS nombre_contrats
FROM CONTRAT c
INNER JOIN COMMUNE co
    ON c.Code_dep_code_commune = co.Code_dep_code_commune
INNER JOIN DEPARTEMENT d
    ON co.dep_code = d.dep_code
INNER JOIN REGION r
    ON d.reg_code = r.reg_code
GROUP BY r.reg_code, r.reg_nom
ORDER BY nombre_contrats DESC;
