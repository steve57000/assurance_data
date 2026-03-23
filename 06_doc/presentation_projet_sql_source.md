# Présentation projet SQL

## Slide 1 - Contexte
- Analyse de contrats d'assurance habitation.
- Objectif : passer de fichiers CSV à une base relationnelle exploitable.

## Slide 2 - Sources
- Contrats : 30335 lignes.
- Référentiel géographique : 38919 communes après normalisation.
- Un dictionnaire de données a été préparé pour typer les colonnes.

## Slide 3 - Modèle de données
- REGION
- DEPARTEMENT
- COMMUNE
- CONTRAT
- Tables tampon : GEO_SOURCE et CONTRAT_SOURCE

## Slide 4 - Import et qualité
- Normalisation du référentiel.
- Ajout automatique de communes techniques pour 3 codes manquants.
- Contrôle des volumes et des valeurs distinctes.

## Slide 5 - Résultats clés
- Cotisation moyenne : 19.33 EUR.
- Surface moyenne des contrats parisiens : 51.77 m2.
- Formules Integral en Pays de la Loire : 589.

## Slide 6 - Faits marquants
- Ile-de-France : 14177 contrats.
- Paris (75) = département au prix moyen le plus élevé : 36.4 EUR.
- 20 communes dépassent 150 contrats.

## Slide 7 - Conclusion
- Base propre.
- Requêtes métier validées.
- Livrables prêts avec emplacements pour captures d'écran.
