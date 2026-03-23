# Script oral complet

Bonjour, je vais vous présenter notre projet SQL consacré à l'analyse de contrats d'assurance habitation.

Dans un premier temps, nous avons étudié les deux fichiers sources. Le fichier `Contrat+.csv` contient 30335 contrats avec des informations d'adresse, de surface, de formule et de cotisation. Le fichier `Region+.csv` joue le rôle de référentiel géographique et nous a permis de relier chaque contrat à une commune, un département et une région.

Ensuite, nous avons construit le dictionnaire des données. Cette étape nous a permis de qualifier chaque colonne, de distinguer les types numériques des variables catégorielles et de repérer les contraintes utiles. Par exemple, `Surface` devient un entier, les codes géographiques restent en texte pour conserver les zéros éventuels, et `Valeur_declaree_biens` est gardée comme une catégorie exploitable en regroupement.

Après cette phase, nous avons modifié le schéma relationnel. Au lieu de conserver toutes les informations dans une seule table, nous avons retenu un modèle normalisé autour de quatre tables principales : `REGION`, `DEPARTEMENT`, `COMMUNE` et `CONTRAT`. Nous avons aussi utilisé `GEO_SOURCE` et `CONTRAT_SOURCE` comme tables tampon d'import. Cette organisation réduit les redondances et rend les jointures plus claires.

Pour le chargement, nous avons créé les tables puis injecté les données du référentiel géographique. Un point important est apparu pendant les contrôles : trois codes de communes du fichier contrat étaient absents du référentiel, à savoir 97434, 97460 et 97470. Pour ne pas bloquer la clé étrangère, nous avons créé des communes techniques rattachées à leur département. Cela permet d'importer l'ensemble des 30335 contrats sans perdre de données.

Nous avons ensuite réalisé les analyses SQL demandées. Les cinq plus grandes surfaces montent jusqu'à 815 m2. La cotisation mensuelle moyenne ressort à 19.33 euros. La plupart des contrats appartiennent à la tranche de valeur déclarée `0-25000`, ce qui montre un portefeuille plutôt orienté vers des biens de valeur modérée.

Sur le plan géographique, nous avons compté 589 contrats en formule Integral dans la région Pays de la Loire. La surface moyenne des contrats situés à Paris atteint 51.77 m2. Le département où la cotisation moyenne est la plus élevée est Paris, avec 36.4 euros. Enfin, la région Ile-de-France concentre 14177 contrats, ce qui en fait de loin la zone la plus représentée dans le jeu de données.

En conclusion, ce projet nous a permis de dérouler une démarche complète : comprendre les données, modéliser la base, charger les fichiers, contrôler la qualité et produire des analyses métier. Les livrables fournis comprennent le document technique, la présentation synthétique et ce script oral, avec les zones clairement identifiées pour insérer les captures d'écran demandées.
