import os
import sys
import pandas as pd
from dash import Dash, html, dcc, Input, Output, ctx, ALL
from flask_caching import Cache
import dash_leaflet as dl
import dash_bootstrap_components as dbc
import json
import requests
import plotly.express as px


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src', 'pages')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src', 'components')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src', 'utils')))

from src.components.map import fetch_data_from_geojson
from src.components.graphs import generate_pie_chart, create_nested_pie_chart, generate_heatmap, generate_gender_metrics, generate_double_bar_chart

from src.components.header import create_header
from src.components.footer import create_footer

# Initialiser l'application Dash
app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])
# Configuration du cache
cache = Cache(app.server, config={'CACHE_TYPE': 'simple'})
geojson_file_path = "./data/raw/fr-esr-cartographie_formations_parcoursup.geojson"
spe_json_file_path = "./data/raw/fr-esr-parcoursup-enseignements-de-specialite-bacheliers-generaux-2.json"
dfJson = pd.read_json(spe_json_file_path, encoding='utf-8')

dfJson["couple_specialites"] = dfJson["doublette"].apply(lambda x: f"{x[0]}, {x[1]}")
specialites = dfJson["couple_specialites"] #🚨le nom entre " " doit être identique au nom de la colonne du tableau
specialites = specialites.unique()

formations = dfJson['formation'] #🚨le nom entre " " doit être identique au nom de la colonne du tableau
formations = formations.unique()

annees = dfJson['annee_du_bac'] #🚨le nom entre " " doit être identique au nom de la colonne du tableau
annees = annees.unique()

# Layout de l'application
app.layout = html.Div([
    create_header(),
    dbc.Container([  # Main container for content
        dbc.Row([
            dbc.Col([
                html.P("Choisissez une année pour visualiser les données :"),
                dcc.Slider(
                    id="annee-slider",
                    min=2021,
                    max=2025,
                    step=1,
                    marks={year: str(year) for year in range(2021, 2026)},
                    value=2023,
                ),
            ], width={"size": 8, "offset": 2}, className="mb-4")  # Centered slider
        ]),
        
        dbc.Row([
            dbc.Col([
                html.Div([  # Wrapper for the map
                    dl.Map(
                        id="map",
                        center=[47.0, 2.0],
                        zoom=6,
                        children=[
                            dl.TileLayer(),
                            dl.GeoJSON(
                                id="geojson-layer",
                                cluster=True,
                                zoomToBoundsOnClick=True,
                                superClusterOptions={"radius": 100},
                            ),
                        ],
                        style={
                            'width': '100%', 
                            'height': '500px',
                            'border': '1px solid #ddd',  # Optional: adds a border
                            'border-radius': '8px',      # Optional: rounded corners
                        }
                    )
                ], className="shadow-sm")  # Optional: adds subtle shadow
            ], width={"size": 10, "offset": 1}, className="mb-4")  # Centered map
        ]),
        
        dbc.Row([
            dbc.Col([
                html.Div(id="api-result-container")
            ], width={"size": 10, "offset": 1})  # Centered results
        ]),
        
        dbc.Row([
            dbc.Col([
                dcc.Dropdown(
                    id='formation-dropdown',
                    options=[{'label': formation, 'value': formation} for formation in formations],
                    value=formations[0],  # Valeur par défaut
                    placeholder="Sélectionnez une formation",
                ),

                # Slider pour sélectionner une année
                dcc.Slider(
                    id='year-slider',
                    min=dfJson['annee_du_bac'].min(),
                    max=dfJson['annee_du_bac'].max(),
                    step=1,
                    marks={str(year): str(year) for year in dfJson['annee_du_bac'].unique()},
                    value=dfJson['annee_du_bac'].min(),  # Valeur par défaut
                ),

                # Graphique
                dcc.Graph(
                    id='bar-chart',
                    figure={},  # Initialement vide
                ),
                dcc.Graph(
                    id='heatmap',
                    figure={},  # Initialement vide
                ),

            ], width={"size": 10, "offset": 1})  # Centered results
        ])
    ], fluid=False),  # Using fixed-width container
    create_footer()
])

@app.callback(
    [
        Output('bar-chart', 'figure'),
        Output('heatmap', 'figure'),
    ],
    [
        Input('formation-dropdown', 'value'),
        Input('year-slider', 'value'),
    ]
)
def update_graphs(selected_formation, selected_year):
    # Mettre à jour le graphique en barres
    bar_chart_figure = generate_double_bar_chart(dfJson, selected_formation, selected_year)
    
    # Mettre à jour la heatmap
    heatmap_figure = generate_heatmap(dfJson, selected_formation, selected_year)
    
    return bar_chart_figure, heatmap_figure

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

    if(not response and response["total_count"] == 0):
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
            formation_data = {
                'intitule_formation': formation.get('lib_for_voe_ins', ''),
                'form_lib_voe_acc': formation.get('form_lib_voe_acc', ''),
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

# Callback pour gérer les clics sur les clusters ou marqueurs individuels
@app.callback(
    Output("api-result-container", "children"),
    [Input("geojson-layer", "clickData"),
     Input("annee-slider", "value")],
    prevent_initial_call=True,
)
def fetch_api_data(feature, selected_year):
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

    # Header information
    header = [
        html.H3(f"Détails de l'établissement {data['nom_etab']}"),
        html.P(f"Session: {data['session']}"),
        html.P(f"Académie: {data['academie']}"),
        html.P(f"Ville: {data['ville']}"),
        html.P(f"Département: {data['dep_lib'] + '-' + data['dep']}"),
        html.P(f"Région: {data['region']}"),
    ]

    if "results" not in data or len(data["results"]) == 0:
        return html.Div(header + [html.P("Aucune information disponible pour cet établissement.")])

    # Create tabs for formations
    formation_tabs = []
    for result in data["results"]:
        tab_content = [
            # Formation info section
            html.H4(result['intitule_formation'], className='mb-3'),
            html.P([
                "Formation Sélective: ",
                html.Span(result['selectivite'], className='font-weight-bold')
            ]),
            html.A(
                "Voir la fiche",
                href=result["lien_form_psup"],
                target="_blank",
                className="btn btn-primary mb-3"
            ),
            
            # Graphs section
            dbc.Row([
                dbc.Col(
                    dcc.Graph(
                        figure=generate_pie_chart(result),
                    ),
                    xs=12, sm=12, md=6, lg=6
                ),
                dbc.Col(
                    dcc.Graph(
                        figure=create_nested_pie_chart(result),
                    ),
                    xs=12, sm=12, md=6, lg=6
                ),
                # dbc.Col(
                #     dcc.Loading(
                #         children=dcc.Graph(
                #             id=f'heatmap-{result["intitule_formation"]}',
                #             figure=generate_heatmap(dfJson, formation=result, annee=selected_year),
                #             style={'height': '700px'}
                #         ) if generate_heatmap(dfJson, formation=result, annee=selected_year)
                #         else html.P("Données non disponibles pour la heatmap", 
                #                 className="text-muted text-center py-4"),
                #         type="default"
                #     ),
                #     width=12
                # )
            ], className='mb-4'),
            dbc.Row([
                dbc.Col(
                    dcc.Loading(
                        children=dcc.Graph(
                            figure=generate_gender_metrics(result),
                            style={'height': '800px'}
                        ),
                        type="default"
                    ),
                    width=12
                )
            ], className='mb-4'),
  
        ]

        # Create tab for this formation
        formation_tabs.append(
            dcc.Tab(
                label=result['intitule_formation'],
                value=f"tab-{result['intitule_formation']}",
                children=html.Div(tab_content, className='p-4'),
            )
        )

    # Combine header and tabs
    layout = html.Div([
        # Header section
        html.Div(header, className='mb-4'),
        
        # Tabs section
        dcc.Tabs(
            id='formation-tabs',
            value=f"tab-{data['results'][0]['intitule_formation']}", # Set first tab as default
            children=formation_tabs,
            className='custom-tabs'
        )
    ])

    return layout

if __name__ == "__main__":

    app.run_server(debug=False)
