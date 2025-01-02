import os
from flask import Flask, render_template
import sys

# Ajouter le répertoire src/pages au sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src', 'pages')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src', 'components')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src', 'utils')))

# Importer la page et les fonctions nécessaires
from map import fetch_data_from_geojson, create_interactive_map  # Exemple pour la page home

app = Flask(__name__)

@app.route('/')
def index():
    """Page d'accueil"""
    # Charger les données GeoJSON
    geojson_file_path = "./data/raw/fr-esr-cartographie_formations_parcoursup.geojson"
    annee_cible = "2023"
    features = fetch_data_from_geojson(geojson_file_path, annee_cible)

    # Créer la carte interactive
    carte = create_interactive_map(features)

    # Extraire le HTML de la carte
    carte_html = carte._repr_html_()  # récupère le HTML de la carte

    # Passer la carte et d'autres informations à la page HTML
    return render_template('home.html', carte_html=carte_html, info="Voici des informations supplémentaires")

if __name__ == "__main__":
    app.run(debug=True)