import os
import requests
import json

#Parcoursup : propositions d'admission dans l'enseignement supérieur des élèves de terminale diplômés du baccalauréat général selon leurs enseignements de spécialité (2021 à 2023)
response_API_admiss = requests.get('https://data.enseignementsup-recherche.gouv.fr/api/explore/v2.1/catalog/datasets/fr-esr-parcoursup-enseignements-de-specialite-bacheliers-generaux-2/records?limit=20')
#Cartographie des formation parcoursup (2021 à 2025 SANS 2024)
response_carto_API = requests.get('https://data.enseignementsup-recherche.gouv.fr/explore/dataset/fr-esr-cartographie_formations_parcoursup/api/?disjunctive.tf&disjunctive.nm&disjunctive.fl&disjunctive.nmc&disjunctive.amg&sort=-annee&location=7,49.04147,9.33289&basemap=e69ab1')
#Parcoursup 2022 - vœux de poursuite d'études et de réorientation dans l'enseignement supérieur et réponses des établissements
response_API_2022 = requests.get('https://data.enseignementsup-recherche.gouv.fr/api/explore/v2.1/catalog/datasets/fr-esr-parcoursup_2022/records?limit=20')#juste l'année a changer !!!sauf 2023 (cest juste fr-esr-parcoursup)

if response_API_2022.status_code == 200:
    data = response_API_2022.text
    parsed_data = json.loads(data)

    output_dir = 'data/raw'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    output_file = os.path.join(output_dir, 'data.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(parsed_data, f, ensure_ascii=False, indent=4)
    
    print(f"Les données ont été enregistrées dans {output_file}")
else:
    print("La requête API a échoué avec le code :", response_API_2022.status_code)
