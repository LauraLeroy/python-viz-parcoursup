import os
import sys
from dash import Dash, html, dcc, Input, Output, ctx, ALL
from flask_caching import Cache
import dash_leaflet as dl
import dash_leaflet.express as dlx
import json
import requests
import plotly.express as px
import plotly.graph_objects as go

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src', 'pages')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src', 'components')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src', 'utils')))

from src.components.map import fetch_data_from_geojson

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
                    "formations": feature["formations"],
                    "etab_uai": feature["etab_uai"],
                },
            }
            for feature in features
        ],
    }
    return geojson_data



def process_api_response(response):

    if(response["total_count"] == 0):
        return []
    
    data = {
        'total_count': response["results"][0],
        'etab_uai': response["results"][0].get('cod_uai', ''),
        'dep': response["results"][0].get('dep', ''),
        'dep_lib': response["results"][0].get('dep_lib', ''),
        'nom_etab': response["results"][0].get('g_ea_lib_vx', ''),
        'academie': response["results"][0].get('acad_mies', ''),
        'session': response["results"][0].get('session', ''),
        'region': response["results"][0].get('region_etab_aff', ''),
        'ville': response["results"][0].get('ville_etab', ''),
    }
    # Extraire la clé 'results' qui contient les formations
    if 'results' in response:
        results = []
        for formation in response['results']:
            # Création d'un dictionnaire pour chaque formation avec ses informations spécifiques
            print(formation)
            formation_data = {
                'intitule_formation': formation.get('lib_for_voe_ins', ''),
                'selectivite': formation.get('select_form', ''),
                'capacite': formation.get('capa_fin', ''),
                'effectif_total_candidat': formation.get('voe_tot', ''),
                'effectif_total_candidat_femme': formation.get('voe_tot_f', ''),
                'effectif_total_candidat_bg_pp': formation.get('nb_voe_pp_bg', ''),#bac général  PHASE PRINCIPALE
                'effectif_total_candidat_bt_pp': formation.get('nb_voe_pp_bt', ''),#bac technologique
                'effectif_total_candidat_bp_pp': formation.get('nb_voe_pp_bp', ''),#bac pro
                'effectif_total_candidat_autre_pp': formation.get('nb_voe_pp_at', ''), #autre formation
                'proposition_admission_total_BG': formation.get('prop_tot_bg', ''),#PROPOSITION D'ADMISSION
                'proposition_admission_total_BT': formation.get('prop_tot_bt', ''),
                'proposition_admission_total_BP': formation.get('prop_tot_bp', ''),
                'proposition_admission_total_autre': formation.get('prop_tot_at', ''),
                'acceptation_total': formation.get('acc_tot', ''), #effectif des candidat ayant accepté la proposition d'admission
                'acceptation_total_f': formation.get('acc_tot_f', ''),#dont femme
                'effectif_admis_BG': formation.get('acc_bg', ''), #effectif admis bag général ectc...
                'effectif_admis_BT': formation.get('acc_bt', ''),
                'effectif_admis_BP': formation.get('acc_bp', ''),
                'effectif_admis_at': formation.get('acc_at', ''),
                'effectif_admis_mention_inconnue': formation.get('acc_mention_nonrenseignee', ''),
                'effectif_admis_mention_aucune': formation.get('acc_sansmention', ''),
                'effectif_admis_mention_AB': formation.get('acc_ab', ''),
                'effectif_admis_mention_B': formation.get('acc_b', ''),
                'effectif_admis_mention_TB': formation.get('acc_tb', ''),
                'effectif_admis_mention_TBF': formation.get('acc_tbf', ''),
                'rang_dernier_admis': formation.get('ran_grp1', ''),
                'lien_form_psup': formation.get('lien_form_psup', ''),
            }
            results.append(formation_data)

        # Ajouter la liste des formations dans le dictionnaire des données
        data['results'] = results
    
    return data

def generate_pie_chart(result):
    labels = ['Sans Mention', 'Mention AB', 'Mention B', 'Mention TB', 'Mention TBF']
    values = [
        result['effectif_admis_mention_aucune'],
        result['effectif_admis_mention_AB'],
        result['effectif_admis_mention_B'],
        result['effectif_admis_mention_TB'],
        result['effectif_admis_mention_TBF'],
    ]
    fig = px.pie(
        names=labels,
        values=values,
        title=f"Répartition des mentions au bac des admis pour la formation {result['intitule_formation']}"
    )
    return fig

def create_nested_pie_chart(data):
    # Extraction des données de base
    candidats = [
        data['effectif_total_candidat_bg_pp'],
        data['effectif_total_candidat_bt_pp'],
        data['effectif_total_candidat_bp_pp'],
        data['effectif_total_candidat_autre_pp'],
    ]
    propositions = [
        data['proposition_admission_total_BG'],
        data['proposition_admission_total_BT'],
        data['proposition_admission_total_BP'],
        data['proposition_admission_total_autre'],
    ]
    admis = [
        data['effectif_admis_BG'],
        data['effectif_admis_BT'],
        data['effectif_admis_BP'],
        data['effectif_admis_at'],
    ]

    # Calcul des catégories opposées proposition vs refusés, admis vs voeux non accepté
    refuses = [max(c - p, 0) for c, p in zip(candidats, propositions)]  # Refusé
    voeux_non_acceptes = [max(p - a, 0) for p, a in zip(propositions, admis)]  # Vœux non acceptés

    labels = [
        "Candidats BG", "Propositions BG", "Admis BG", "Vœux non acceptés BG", "Refusé BG",
        "Candidats BT", "Propositions BT", "Admis BT", "Vœux non acceptés BT", "Refusé BT",
        "Candidats BP", "Propositions BP", "Admis BP", "Vœux non acceptés BP", "Refusé BP",
        "Candidats Autres", "Propositions Autres", "Admis Autres", "Vœux non acceptés Autres", "Refusé Autres",
    ]

    # Définition des parents pour la hiérarchie
    parents = [
        "", "Candidats BG", "Propositions BG", "Propositions BG", "Candidats BG",  # BG
        "", "Candidats BT", "Propositions BT", "Propositions BT", "Candidats BT",  # BT
        "", "Candidats BP", "Propositions BP", "Propositions BP", "Candidats BP",  # BP
        "", "Candidats Autres", "Propositions Autres", "Propositions Autres", "Candidats Autres",  # Autres
    ]

    values = [
        candidats[0], propositions[0], admis[0], voeux_non_acceptes[0], refuses[0],  # BG
        candidats[1], propositions[1], admis[1], voeux_non_acceptes[1], refuses[1],  # BT
        candidats[2], propositions[2], admis[2], voeux_non_acceptes[2], refuses[2],  # BP
        candidats[3], propositions[3], admis[3], voeux_non_acceptes[3], refuses[3],  # Autres
    ]

    colors = [
        "#1B4965", "#0081A7", "#00AFB9", "#62B6CB", "#BEE9E8",  # BG  --> Candidats, Propositions, Admis, Vœux non acceptés, Refusé, 
        "#FF7B00", "#FF9500", "#FFA200", "#FFB700", "#FF8800",  # BT
        "#55753C", "#96BE8C", "#ACECA1", "#C9F2C7", "#629460",  # BP
        "#6E0D0D", "#F73E3E", "#A81111", "#FF7777", "#DE1021",  # Autres
    ]

    fig = go.Figure(go.Sunburst(
        labels=labels,
        parents=parents,
        values=values,
        branchvalues="total",  # Les parents incluent les enfants
        marker=dict(colors=colors)
    ))

    # Mise en forme de la figure
    fig.update_layout(
        title="Répartition des candidats, propositions et admis par type de bac",
        margin=dict(t=40, l=0, r=0, b=0),
    )

    return fig


# Callback pour gérer les clics sur les clusters ou marqueurs individuels
@app.callback(
    Output("api-result-container", "children"),
    Input("geojson-layer", "clickData"),
    prevent_initial_call=True,
)
def fetch_api_data(feature):
    if not feature:
        return "Cliquez sur un marqueur pour voir les informations."

    properties = feature.get("properties", {})
    cod_uai = properties.get("etab_uai", None)

    if not cod_uai:
        return "Aucun code UAI trouvé pour ce marqueur."

    api_url = f"https://data.enseignementsup-recherche.gouv.fr/api/explore/v2.1/catalog/datasets/fr-esr-parcoursup/records?where=cod_uai%20LIKE%20%22{cod_uai}%22"
    response = requests.get(api_url)
    data = process_api_response(response.json())

    if len(data) == 0:
        return html.P("Aucune information disponible pour cet établissement.")

    divs = [
        html.H3(f"Détails de l'établissement {data['nom_etab']}"),
        html.P(f"Session: {data['session']}"),
        html.P(f"Académie: {data['academie']}"),
        html.P(f"Ville: {data['ville']}"),
        html.P(f"Département: {data['dep_lib'] + '-' + data['dep']}"),
        html.P(f"Région: {data['region']}"),
    ]

    # Ajouter les détails pour chaque formation
    if "results" in data and len(data["results"]) > 0:
        for result in data["results"]:
            divs.append(html.Div([
                html.P(f"Intitulé de la formation: {result['intitule_formation']}"),
                html.P(f"Formation Sélective: {result['selectivite']}"),
                html.A("Voir la fiche", href=result["lien_form_psup"], target="_blank"),
                dcc.Graph(figure=generate_pie_chart(result), style={'display': 'inline-block', 'width': '49%'}),  # graphique des mentions
                dcc.Graph(figure=create_nested_pie_chart(result), style={'display': 'inline-block', 'width': '49%'}) #graphiques avec type de bac
            ]))
        return html.Div(divs)
    else:
        return html.P("Aucune information disponible pour cet établissement.")
if __name__ == "__main__":
    app.run_server(debug=False)
