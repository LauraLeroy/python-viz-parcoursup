# home.py

import json
import folium
from folium.plugins import MarkerCluster

def fetch_data_from_geojson(file_path, year):
    """ Récupère les données du GEOJSON à utiliser pour la carte """
    print(f"Chargement des données depuis le fichier GeoJSON : {file_path}...")

    # Charger le fichier GeoJSON
    with open(file_path, 'r', encoding='utf-8') as file:
        geojson_data = json.load(file)

    features = []
    for feature in geojson_data['features']:
        # Propriété de la data
        properties = feature['properties']
        # Coordonnées
        geometry = feature['geometry']

        # Filtrer par année
        if properties['annee'] == year:
            features.append({
                'etab_nom': properties['etab_nom'],
                'etab_uai': properties['etab_uai'],  # Ajouter le code établissement
                'annee': properties['annee'],
                'nom_formation': properties['nm'],
                'latitude': geometry['coordinates'][1],  # Latitude
                'longitude': geometry['coordinates'][0]  # Longitude
            })

    print(f"{len(features)} établissements trouvés pour l'année {year}.")
    return features


def create_interactive_map(features):
    """ Crée une carte interactive avec des popups contenant les informations détaillées """
    print("Création de la carte interactive...")
    m = folium.Map(location=[47.0, 2.0], zoom_start=6, tiles="cartodbpositron")

    marker_cluster = MarkerCluster().add_to(m)  # Ajoute un cluster de marqueurs à la carte

    # Ajout de chaque point sur la carte
    for feature in features:
        etab_uai = feature['etab_uai']
        etab_nom = feature['etab_nom']
        latitude = feature['latitude']
        longitude = feature['longitude']
        nom_formation = feature['nom_formation']
        annee = feature['annee']

        # Créer le contenu HTML du popup de base
        html = f"""
        <h1>{etab_nom}</h1>
        <p><b>Nom de l'établissement:</b> {etab_nom}</p>
        <p><b>Nom de la formation:</b> {nom_formation}</p>
        <p><b>Année:</b> {annee}</p>
        <p><button id="btn-{etab_uai}">Obtenir plus d'informations</button></p>
        <div id="api-result-{etab_uai}"></div>
        <script>
            document.getElementById("btn-{etab_uai}").onclick = function() {{
                window.parent.postMessage({{
                    action: 'fetchData',
                    annee: '{annee}',
                    cod_uai: '{etab_uai}'
                }}, '*');
            }};
        </script>
        """

        iframe = folium.IFrame(html=html, width=300, height=250)
        popup = folium.Popup(iframe, max_width=2650)

        folium.Marker(
            location=[latitude, longitude],
            popup=popup
        ).add_to(marker_cluster)

    # Retourner la carte générée
    return m
