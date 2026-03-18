-- ============================================
-- Ça permet de confirmer :
-- que les lignes sont bien là
-- que les colonnes sont bien remplies
-- qu’il n’y a pas de décalage d’import
-- ============================================

SELECT COUNT(*) AS nb_contrats FROM CONTRAT;
SELECT COUNT(*) AS nb_regions FROM REGION;

SELECT * FROM CONTRAT LIMIT 5;
SELECT * FROM REGION LIMIT 5;


-- ============================================
-- Tester les valeurs distinctes utiles
-- ============================================

SELECT DISTINCT Type_local FROM CONTRAT;
SELECT DISTINCT Formule FROM CONTRAT;
SELECT DISTINCT Occupation FROM CONTRAT;
SELECT DISTINCT Valeur_declaree_biens FROM CONTRAT;