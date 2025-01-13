# home.py

import json
import folium
from folium.plugins import MarkerCluster

def fetch_data_from_geojson(file_path, year):
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



# def create_interactive_map(features):
#     """ Crée une carte interactive avec des popups contenant les informations détaillées """
#     print("Création de la carte interactive...")
#     m = folium.Map(location=[47.0, 2.0], zoom_start=6, tiles="cartodbpositron")

#     marker_cluster = MarkerCluster().add_to(m)  # Ajoute un cluster de marqueurs à la carte

#     # Ajout de chaque point sur la carte
#     for feature in features:
#         etab_uai = feature['etab_uai']
#         etab_nom = feature['etab_nom']
#         latitude = feature['latitude']
#         longitude = feature['longitude']
#         nom_formation = feature['nom_formation']
#         annee = feature['annee']

#         # Créer le contenu HTML du popup de base
#         html = f"""
#         <h1>{etab_nom}</h1>
#         <p><b>Nom de l'établissement:</b> {etab_nom}</p>
#         <p><b>Nom de la formation:</b> {nom_formation}</p>
#         <p><b>Année:</b> {annee}</p>
#         <p><button id="btn-{etab_uai}">Obtenir plus d'informations</button></p>
#         <div id="api-result-{etab_uai}"></div>
#         <script>
#             document.getElementById("btn-{etab_uai}").onclick = function() {{
#                 window.parent.postMessage({{
#                     action: 'fetchData',
#                     annee: '{annee}',
#                     cod_uai: '{etab_uai}'
#                 }}, '*');
#             }};
#         </script>
#         """

#         iframe = folium.IFrame(html=html, width=300, height=250)
#         popup = folium.Popup(iframe, max_width=2650)

#         folium.Marker(
#             location=[latitude, longitude],
#             popup=popup
#         ).add_to(marker_cluster)

#     # Retourner la carte générée
#     return m
