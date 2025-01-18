import pandas as pd
from dash import Dash, html, dcc, Input, Output
from flask_caching import Cache
import dash_leaflet as dl
import dash_bootstrap_components as dbc
import requests

#import modules from src
from src.components.cards import create_institution_card
from src.components.map import fetch_data_from_geojson
from src.components.graphs import generate_pie_chart, create_nested_pie_chart, generate_heatmap, generate_gender_metrics, generate_double_bar_chart
from src.components.header import create_header
from src.components.footer import create_footer
from src.utils.get_data import process_api_response, get_latest_data

# Initialiser l'application Dash
app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])
# Configuration du cache
cache = Cache(app.server, config={'CACHE_TYPE': 'simple'})

geojson_file_path = "./data/raw/fr-esr-cartographie_formations_parcoursup.geojson"
spe_json_file_path = "./data/raw/fr-esr-parcoursup-enseignements-de-specialite-bacheliers-generaux-2.json"
dfJson = pd.read_json(spe_json_file_path, encoding='utf-8')
dfJson["couple_specialites"] = dfJson["doublette"].apply(lambda x: f"{x[0]}, {x[1]}")

specialites = dfJson["couple_specialites"]
specialites = specialites.unique()
formations = dfJson['formation']
formations = formations.unique()
annees = dfJson['annee_du_bac']
annees = annees.unique()

# Layout de l'application
app.layout = html.Div([
    create_header(),
    dbc.Container([  # Main container for content
        dbc.Row([
            dbc.Col([
                html.P("Choisissez une année pour visualiser les données :"),
                dcc.Slider(
                    id="year-slider",
                    min=2021,
                    max=2023,
                    step=1,
                    marks={year: str(year) for year in range(2021, 2024)},
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
def update_graphs(selected_formation: str, selected_year: int) -> tuple:
    """Mettre à jour les graphiques du dataset formation par enseignement de spé en fonction de la formation et de l'année sélectionnées

    Args:
        selected_formation (str): La formation sélectionnée
        selected_year (int): L'année sélectionnée

    Returns:
        tuple: Les figures mises à jour pour le graphique en barres et la heatmap
    """
    # Mettre à jour le graphique en barres
    bar_chart_figure = generate_double_bar_chart(dfJson, selected_formation, selected_year)
    
    # Mettre à jour la heatmap
    heatmap_figure = generate_heatmap(dfJson, selected_formation, selected_year)
    
    return bar_chart_figure, heatmap_figure

# Callback pour mettre à jour les données GeoJSON en fonction de l'année
@app.callback(
    Output("geojson-layer", "data"),  # Met à jour les données GeoJSON
    Input("year-slider", "value"),  # Récupère la valeur du slider
)
@cache.memoize(timeout=3600)  # Cache pendant 1 heure
def update_geojson_data(annee_cible: int) -> dict:
    """Mettre à jour les données GeoJSON en fonction de l'année cible

    Args:
        annee_cible (int):L'année cible choisie avec le slider

    Returns:
        dict: Les données GeoJSON mises à jour
    """
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



# Callback pour gérer les clics sur les clusters ou marqueurs individuels
@app.callback(
    Output("api-result-container", "children"),
    [Input("geojson-layer", "clickData"),
     Input("year-slider", "value")],
    prevent_initial_call=True,
)
def fetch_api_data(feature: dict, selected_year:int) -> html.Div:
    if not feature:
        return "Cliquez sur un marqueur pour voir les informations."

    properties = feature.get("properties", {})
    cod_uai = properties.get("etab_uai", None)

    if not cod_uai:
        return "Aucun code UAI trouvé pour ce marqueur."

    api_url = f"https://data.enseignementsup-recherche.gouv.fr/api/explore/v2.1/catalog/datasets/fr-esr-parcoursup_{selected_year}/records?where=cod_uai%20LIKE%20%22{cod_uai}%22"
    response = requests.get(api_url)
    data = process_api_response(response.json())

    if len(data) == 0:
        return html.P("Aucune information disponible pour cet établissement.")

    # Header information
    header = html.Div(
    [
        dbc.Container(
            [
                dbc.Row(
                    dbc.Col(
                        create_institution_card(data),
                        width={"size": 10, "offset": 1},
                        lg={"size": 8, "offset": 2}
                    )
                )
            ],
            fluid=True,
            className="py-4"
        )
    ])

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
            ], className='mb-4'),
            dbc.Row([
    dbc.Col(
        dcc.Graph(
            figure=generate_gender_metrics(result)[0],  # First figure (Sunburst chart)
        ),
        xs=12, sm=12, md=6, lg=6  # Full width on small screens, 50% width on medium and larger screens
    ),
    dbc.Col(
        dcc.Graph(
            figure=generate_gender_metrics(result)[1],  # Second figure (Bar chart)
        ),
        xs=12, sm=12, md=6, lg=6  # Full width on small screens, 50% width on medium and larger screens
    ),
], className='mb-4')
  
        ]

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

    #----------------------------------------------------------------
    # POUR METTRE A JOUR LES DONNEES SE SITUANT DANS DATA/RAW DECOMMENTER LES LIGNES CI-DESSOUS
    # CES LIGNES DOIVENT ETRE IMPERATIVEMENT RECOMMENTEES AVANT DE LANCER L'APPLICATION CAR
    # LE PROCESSUS DE TELECHARGEMENT DES DONNEES PEUT ETRE LONG
    #----------------------------------------------------------------


    # url = "https://data.enseignementsup-recherche.gouv.fr/api/explore/v2.1/catalog/datasets/fr-esr-parcoursup-enseignements-de-specialite-bacheliers-generaux-2/exports/json?lang=fr&timezone=Europe%2FBerlin"
    # urlGeoJson = "https://data.enseignementsup-recherche.gouv.fr/api/explore/v2.1/catalog/datasets/fr-esr-cartographie_formations_parcoursup/exports/geojson?lang=fr&timezone=Europe%2FBerlin"
    # if get_latest_data(url) or get_latest_data(urlGeoJson):
    #     print("Des données ont été mises à jour.")
    # else:
    #     print("Aucune mise à jour nécessaire.")
    
    app.run_server(debug=False)
