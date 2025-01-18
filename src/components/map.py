import json
from typing import List, Dict, Any

def fetch_data_from_geojson(file_path: str, year: int) -> List[Dict[str, Any]]:
    """ Récupère les données du GeoJSON pour une année donnée, en regroupant les formations par établissement """
    
    print(f"Chargement des données depuis le fichier GeoJSON : {file_path}...")

    with open(file_path, 'r', encoding='utf-8') as file:
        geojson_data = json.load(file)

    establishments = {}

    for feature in geojson_data['features']:
        properties = feature['properties']
        geometry = feature['geometry']

        if properties['annee'] == year:
            etab_uai = properties['etab_uai']
            formation = properties['nm'][0]  # Assuming that 'nm' is a list and you take the first formation

            if etab_uai not in establishments:
                establishments[etab_uai] = {
                    'etab_nom': properties['etab_nom'],
                    'etab_uai': etab_uai,
                    'annee': properties['annee'],
                    'tc': properties['tc'],
                    'region': properties['region'],
                    'departement': properties['departement'],
                    'commune': properties['commune'],
                    'fiche': properties['fiche'],
                    'etab_url': properties['etab_url'],
                    'latitude': geometry['coordinates'][1],
                    'longitude': geometry['coordinates'][0],
                    'formations': []  # Initialize an empty list for formations
                }
            
            # Ajouter la formation à la liste des formations de l'établissement
            establishments[etab_uai]['formations'].append(formation)

    # Convertir le dictionnaire en une liste de résultats
    results = list(establishments.values())
    print(f"{len(results)} établissements trouvés pour l'année {year}.")
    return results