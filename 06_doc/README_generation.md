# Génération des livrables du projet SQL

Les livrables demandés sont maintenus sous forme **texte extractible** dans ce dépôt afin d'éviter les blocages de revue liés aux fichiers binaires.

## Fichiers sources à relire / modifier
- `projet_sql_source.md` : document technique.
- `presentation_projet_sql_source.md` : support de présentation.
- `script_oral_complet_source.md` : script oral complet.
- `annexes_chiffrees.txt` : résultats calculés à partir des données.

## Génération locale des PDF
Depuis la racine du dépôt :

```bash
python 06_doc/generate_project_docs.py
```

La commande génère localement :
- `06_doc/projet_sql.pdf`
- `06_doc/presentation_projet_sql.pdf`
- `06_doc/script oral complet.pdf`
- `06_doc/analysis_snapshot.sqlite`

Ces artefacts sont **volontairement exclus du versionnement Git** pour éviter le problème de "fichier binaire" pendant les demandes d'extraction ou de revue.

## Conseil de remise
Pour la remise finale à l'école / au correcteur, utilisez les PDF générés localement, puis ajoutez vos captures d'écran dans les zones prévues.
