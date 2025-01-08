import os
import sys
from dash import Dash, html, dcc, Input, Output, ctx, ALL
from flask_caching import Cache
import dash_leaflet as dl
import dash_leaflet.express as dlx
import json
import requests
# Ajouter les chemins requis
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src', 'pages')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src', 'components')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src', 'utils')))

from map import fetch_data_from_geojson

# Initialiser l'application Dash
app = Dash(__name__, suppress_callback_exceptions=True)

# Configuration du cache
cache = Cache(app.server, config={'CACHE_TYPE': 'simple'})

geojson_file_path = "./data/raw/fr-esr-cartographie_formations_parcoursup.geojson"

# Layout de l'application
app.layout = html.Div([
    html.H1("Visualisation des formations Parcoursup avec Dash Leaflet"),
    html.P("Choisissez une année pour visualiser les données :"),
    dcc.Slider(
        id="annee-slider",
        min=2021,
        max=2025,
        step=1,
        marks={year: str(year) for year in range(2021, 2026)},
        value=2023,  # Année par défaut
    ),
    dl.Map(
        id="map",
        center=[47.0, 2.0],  # Centré sur la France
        zoom=6,
        children=[
            dl.TileLayer(),  # Fond de carte
            dl.GeoJSON(
                id="geojson-layer",
                cluster=True,  # Active le clustering
                zoomToBoundsOnClick=True,
                superClusterOptions={"radius": 100},  # Options de supercluster
            ),
        ],
        style={'width': '100%', 'height': '500px'}
    ),
    html.Div(id="api-result-container"),  # Container pour afficher les résultats de l'API
])


# Callback pour mettre à jour les données GeoJSON en fonction de l'année
@app.callback(
    Output("geojson-layer", "data"),  # Met à jour les données GeoJSON
    Input("annee-slider", "value"),  # Récupère la valeur du slider
)
@cache.memoize(timeout=3600)  # Cache pendant 1 heure
def update_geojson_data(annee_cible):
    features = fetch_data_from_geojson(geojson_file_path, str(annee_cible))

    # Convertir les features en format GeoJSON
    geojson_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [feature["longitude"], feature["latitude"]],
                },
                "properties": {
                    "etab_nom": feature["etab_nom"],
                    "nom_formation": feature["nom_formation"],
                    "etab_uai": feature["etab_uai"],
                },
            }
            for feature in features
        ],
    }
    return geojson_data


# Callback pour gérer les clics sur les clusters ou marqueurs individuels
@app.callback(
    Output("api-result-container", "children"),
    Input("geojson-layer", "clickData"),  # Détecte les clics sur une feature GeoJSON
    prevent_initial_call=True,
)
def fetch_api_data(feature):
    if not feature:
        return "Cliquez sur un marqueur pour voir les informations."
    print(feature)

    properties = feature.get("properties", {})
    cod_uai = properties.get("etab_uai", None)
    print(cod_uai)
    if not cod_uai:
        return "Aucun code UAI trouvé pour ce marqueur."

    api_url = f"https://data.enseignementsup-recherche.gouv.fr/api/explore/v2.1/catalog/datasets/fr-esr-parcoursup/records?where=cod_uai%20LIKE%20%22{cod_uai}%22"
    response = requests.get(api_url)
    data = response.json()
    print("results")
    print("----------------")
    if "results" in data and len(data["results"]) > 0:
        info = data["results"][0] # A CHANGER CAR PEUT AVOIR PLUSIEURS FORMATION POUR UN MEME ETABLISSEMENT (EX IUT MARNE LA VALLEE)
        print(info)
        return html.Div([
            html.H3(f"Détails de l'établissement {info['lib_for_voe_ins']}"),
            html.P(f"Région: {info['region_etab_aff']}"),
            html.P(f"Ville: {info['ville_etab']}"),
            html.P(f"Formation Sélective: {info['select_form']}"),
            html.A("Voir la fiche", href=info["detail_forma"], target="_blank"),
        ])
    else:
        return html.P("Aucune information disponible pour cet établissement.")

if __name__ == "__main__":
    app.run_server(debug=True)
