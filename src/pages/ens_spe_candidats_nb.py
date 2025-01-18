import pandas as pd
import plotly_express as px
from dash import Dash, dcc, html, dash_table, callback, Output, Input

df = pd.read_json("./data/raw/fr-esr-parcoursup-enseignements-de-specialite-bacheliers-generaux-2.json",encoding="utf-8")

df["couple_specialites"] = df["doublette"].apply(lambda x: f"{x[0]}, {x[1]}")
specialites = df["couple_specialites"] #🚨le nom entre " " doit être identique au nom de la colonne du tableau
specialites = specialites.unique()

formations = df['formation'] #🚨le nom entre " " doit être identique au nom de la colonne du tableau
formations = formations.unique()

###suppression la colonne doublette
df = df.drop(columns=["doublette"])
annees = df['annee_du_bac'] #🚨le nom entre " " doit être identique au nom de la colonne du tableau
annees = annees.unique()

### Initialisation de l'app
app = Dash()


### La mise en page du graphique

app.layout= [
            dcc.Dropdown( ## Menu déroulant pour les formations
                 options=[{'label': formation, 'value': formation} for formation in formations],
                 value='DCG',
                 id='formation-dropdown'),
            
             dcc.RadioItems(
                    options=[],##bouton invisible qui permet la selection des deux colonnes
                    value='both',
                    id='xaxis-columns'),
             
             dcc.Graph(
                 figure={},
                 id='controls-and-graph'),
             
             dcc.Slider( ## slider pour les années
                df['annee_du_bac'].min(),
                df['annee_du_bac'].max(),
                step = None,
                id = 'year-slider',
                value = df['annee_du_bac'].min(),
                marks = {str(year): str(year) for year in df['annee_du_bac'].unique()},),
                
             ]
    
###Intéraction 
@callback(
    Output('controls-and-graph','figure'), # Output(component_id , component_property())
    Input('formation-dropdown', 'value'),
    Input('xaxis-columns','value'),
    Input('year-slider','value'),

)

def update_graph(selected_formation,col_chosen,selected_year): #(xaxis_columns_name, year_value)
    
    ### filtre pour les données du graphique
    filtered_df = df[(df['annee_du_bac'] == selected_year) &
        (df['formation'] == selected_formation)]
    
    # Réorganiser les données pour les options 'both'
    if col_chosen == 'both':
        melted_df = filtered_df.melt( # création d'une nouvelle colonne "Légende" avec la conversion des colonnes en lignes
            id_vars=['couple_specialites'], 
            value_vars=['voeux', 'propositions_d_admissions'],
            var_name='Légende', 
            value_name='Valeur'
        )
        
        fig = px.bar(
            melted_df, 
            x='Valeur', 
            y='couple_specialites', 
            color='Légende', 
            barmode ='group', 
            title=f"Comparaison des voeux et propositions pour l'année {selected_year}"
        )
    
    fig.update_layout( ### Noms des axes
        xaxis_title="Nombre de candidats",
        yaxis_title="Duo de spécialités",
    )
    
    return fig


###Affichage

if __name__ == '__main__':
    app.run(debug=True)
