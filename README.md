# User Guide

Pour installer les différentes dépendances, aller dans votre environement virtuel (dossier .venv généralement) et activer le avec la commande .\Scripts\activate (Windows) ou  source venv/Scripts/activate (Linux).
Ensuite exécutez la commande pip install -r requirement.txt.
## Data

Les données utilisées provienne de la plateforme DataGouv et plus précisémment de EnseignementSup OpenData géré par le ministère de l'enseignement supérieur et de la recherche.

Voici les différents lien menant aux Dataset utilisé:
- https://data.enseignementsup-recherche.gouv.fr/explore/dataset/fr-esr-parcoursup-enseignements-de-specialite-bacheliers-generaux-2/information/ Parcoursup : propositions d'admission dans l'enseignement supérieur des élèves de terminale diplômés du baccalauréat général selon leurs enseignements de spécialité.
- API : https://data.enseignementsup-recherche.gouv.fr/api/explore/v2.1/catalog/datasets/fr-esr-parcoursup/records - Parcoursup 2024 - vœux de poursuite d'études et de réorientation dans l'enseignement supérieur et réponses des établissements
- https://data.enseignementsup-recherche.gouv.fr/explore/dataset/fr-esr-cartographie_formations_parcoursup/information/?disjunctive.tf&disjunctive.nm&disjunctive.fl&disjunctive.nmc&disjunctive.amg&sort=-annee - Cartographie des formations Parcoursup

Pour une raison inconnue, le GEOJSON de la cartographie des formations paracoursup est incomple car il manque l'année 2024, bien que 2023 et 2025 soit bien présent. De ce fait, nous avons choisis de ne traiter que les données allant de 2021 à 2023.

## Usage

```python
import foobar

# returns 'words'
foobar.pluralize('word')

# returns 'geese'
foobar.pluralize('goose')

# returns 'phenomenon'
foobar.singularize('phenomena')
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)