# User Guide

Pour installer les différentes dépendances, aller dans votre environement virtuel (dossier .venv généralement) et activer le avec la commande .\.venv\Scripts\activate (Windows) ou  source venv/Scripts/activate (Linux).
Ensuite exécutez la commande pip install -r requirement.txt.
## Data

Les données utilisées provienne de la plateforme DataGouv et plus précisémment de EnseignementSup OpenData géré par le ministère de l'enseignement supérieur et de la recherche.

Voici les différents lien menant aux Dataset utilisé:
- https://data.enseignementsup-recherche.gouv.fr/explore/dataset/fr-esr-parcoursup-enseignements-de-specialite-bacheliers-generaux-2/information/ Parcoursup : propositions d'admission dans l'enseignement supérieur des élèves de terminale diplômés du baccalauréat général selon leurs enseignements de spécialité.
- API : https://data.enseignementsup-recherche.gouv.fr/api/explore/v2.1/catalog/datasets/fr-esr-parcoursup/records - Parcoursup 2024 - vœux de poursuite d'études et de réorientation dans l'enseignement supérieur et réponses des établissements
- https://data.enseignementsup-recherche.gouv.fr/explore/dataset/fr-esr-cartographie_formations_parcoursup/information/?disjunctive.tf&disjunctive.nm&disjunctive.fl&disjunctive.nmc&disjunctive.amg&sort=-annee - Cartographie des formations Parcoursup

Pour une raison inconnue, le GEOJSON de la cartographie des formations paracoursup est incomple car il manque l'année 2024, bien que 2023 et 2025 soit bien présent. De ce fait, nous avons choisis de ne traiter que les données allant de 2021 à 2023.

## Developer Guide

Dans le cas, où vous souhaiteriez ajouter une page ou de nouveaux graphiques sur notre site, il y aura plusieurs étapes à respecter impérativement : 

Tout d’abord, il faudra inclure dans le dossier raw soit “data/raw/”,le dataset que vous souhaitez utiliser pour votre graphique puis inclure le code dans le document graphs.py en suivant la logique du document.


## Rapport d’analyse

Ci - dessous voici le détail de l'ensemble des conclusions que l'on peut déduire des différents graphiques.

####La carte du monde####

Cette carte recense l’ensemble des établissements français proposant des formations sur Parcoursup. À l’aide de cette carte, l’utilisateur peut obtenir plusieurs informations sur les établissements et les formations associées. 

Dans un premier temps, en choisissant un point sur la carte, l’utilisateur peut repérer l’environnement dans lequel il se situe. Puis en scrollant sur la page, une brève description de celui-ci, regroupant le nom, l’académie, la région, le département, la ville, et l’année de prélèvement des données, par exemple session 2023. Certains établissements sur la carte n’ont pas de données qui leur sont associées dans le data, ce qui fait que certains graphiques n’affichent rien. Nous n’avons pas trouvé de solutions pour régler ce problème.


####Les diagrammes circulaires####

Ensuite, il y a différents graphiques classés par formations qui apparaissent, le premier étant un diagramme circulaire recensant en pourcentage la répartition des mentions au baccalauréat tous types confondus pour les admis dans la formation. Ce visuel permet aux candidats et futures candidats de se positionner en fonction de leur résultat aux diplômes. 

En outre, l’utilisation du diagramme en secteur permet d’analyser le nombre de candidats admis, refusés, ayant reçu une proposition ou encore n’ayant pas accepté leurs vœux en fonction de leur type de baccalauréat. Autrement dit, on peut observer le nombre de candidats ayant été refusé dans la formation après un baccalauréat professionnel et ainsi de suite.

S'ensuit une analyse du nombre d’hommes et de femmes ayant postulé et ayant été admis dans la formation. Cette information est représentée sous la forme d’un diagramme en cercles emboîtés ou en rayons de soleil indiquant en son centre la répartition des personnes ayant postulé puis sur une second cercle le nombre de personnes admises est lisible. Ainsi on peut approximativement estimer le taux de parité au sein d’une formation selon les années précédentes.


###Diagramme en barres ####

Lorsque l’on cherche une formation post-bac, il est intéressant de s’informer sur la proportion d’hommes et de femmes en son sein. Pour cela, en complément du graphique précédent, un diagramme en barres illustre les mêmes données que le graphique précédent mais sous une autre forme. Ainsi, on peut plus facilement se rendre compte des écarts.


####Le graphique sur les enseignements de spécialité####

D’après ce graphique, l’utilisateur peut déduire le nombre de candidats ayant confirmé au moins un voeux dans la formation qu’il souhaite sur l’année sélectionnée. De plus, il peut également observer sur ce graphique le nombre de candidats ayant reçu une proposition d’admission pour ces mêmes paramètres. Ainsi il peut se faire une idée du taux de candidats susceptible d’entrer dans la formation selon les spécialités tout en ayant une idée des branches choisies par les anciens candidats en fonction des duos de spécialités.


####Heat Map####

Pour finir, le dernier élément de comparaison est une carte thermique en pourcentage sur la répartition des propositions d’admissions en fonction des binômes de spécialités choisis. Elle permet de visualiser les spécialités les couples de spécialités les plus privilégiées pour la formation souhaitée.


## Copyright

Nous déclarons sur l’honneur, Laura Leroy et Lauriane Cotor que le code fourni a été produit par nous même, à l’exception des lignes ci dessous : 

Pour la réalisation du graphique sur les enseignements de spécialités, Lauriane s'est appuyé sur les ressources suivantes qui détaillent comment ajouter des éléments interactifs, https://dash.plotly.com/basic-callbacks et https://pandas.pydata.org/docs/reference/general_functions.html et https://www.geeksforgeeks.org/python-pandas-melt/ dans les éléments suivants ou pour les noms des id:
      > melted_df = filtered_df.melt(...)
      > 'controls-and-graph'; year-slider' et ‘xaxis-columns’


## Developer Guide

[MIT](https://choosealicense.com/licenses/mit/)