-- ============================================
-- Les 5 contrats avec les surfaces les plus élevées
-- ============================================
SELECT Contrat_ID, Surface
FROM CONTRAT
ORDER BY Surface DESC
LIMIT 5;


-- ============================================
-- Prix moyen de la cotisation mensuelle
-- ============================================
SELECT AVG(Prix_cotisation_mensuel) AS prix_moyen_cotisation
FROM CONTRAT;


-- ============================================
-- Nombre de contrats pour chaque catégorie de prix de la valeur déclarée des biens
-- ============================================
SELECT Valeur_declaree_biens, COUNT(*) AS nombre_contrats
FROM CONTRAT
GROUP BY Valeur_declaree_biens
ORDER BY nombre_contrats DESC;


-- ============================================
-- numéros de contrats avec type de contrat et formule pour les maisons du département 71
-- ============================================
SELECT Contrat_ID, Type_contrat, Formule
FROM CONTRAT
WHERE Type_local = 'Maison'
  AND CAST(Code_postal AS CHAR) LIKE '71%';