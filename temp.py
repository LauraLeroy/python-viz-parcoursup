import folium
from folium.plugins import MarkerCluster
import json
import requests

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
                'etab_uai': properties['etab_uai'],
                'annee': properties['annee'],
                'nom_formation': properties['nm'],
                'latitude': geometry['coordinates'][1],  # Latitude
                'longitude': geometry['coordinates'][0]  # Longitude
            })

    print(f"{len(features)} établissements trouvés pour l'année {year}.")
    return features

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

#     script = """
#     <script>
#     window.addEventListener('message', function(event) {
#         if (event.data.action === 'fetchData') {
#             const apiUrl = `https://data.enseignementsup-recherche.gouv.fr/api/explore/v2.1/catalog/datasets/fr-esr-parcoursup/records?where=session%20LIKE%20%22${event.data.annee}%22%20AND%20cod_uai%20LIKE%20%22${event.data.cod_uai}%22`;
            
#             fetch(apiUrl)
#                 .then(response => response.json())
#                 .then(data => {
                
#                 console.log(data.results)
#                 console.log(data.results[0].cod_uai)
#                     const resultDiv = document.getElementById('api-result-' + data.results[0].cod_uai);
#                     console.log(resultDiv)
#                     if (data.total_count > 0) {
#                         const info = data.results;
#                         console.log(data.results)
#                         resultDiv.innerHTML = `
#                             <ul>
#                                 <li><b>Formation:</b> ${info.lib_for_voe_ins || 'Non spécifiée'}</li>
#                                 <li><b>Région:</b> ${info.region_etab_aff || 'Non spécifiée'}</li>
#                                 <li><b>Ville:</b> ${info.ville_etab || 'Non spécifiée'}</li>
#                                 <li><b>Formation Sélective:</b> ${info.select_form || 'Non spécifiée'}</li>
#                                 <li><a href="https://www.parcoursup.fr${info.detail_forma || '#'}" target="_blank">Voir la fiche</a></li>
#                             </ul>
#                         `;
#                     } else {
#                         resultDiv.innerHTML = '<p>Aucune information trouvée pour cet établissement.</p>';
#                     }
#                 })
#                 .catch(error => {
#                     console.error('Erreur lors de la récupération des données API:', error);
#                 });
#         }
#     });
#     </script>
#     """

#     m.get_root().html.add_child(folium.Element(script))

#     # Sauvegarder la carte
#     output_map_path = "map.html"
#     m.save(output_map_path)
#     print(f"Carte créée et sauvegardée sous {output_map_path}.")

# # Fonction principale
# if __name__ == "__main__":
#     geojson_file_path = "./data/raw/fr-esr-cartographie_formations_parcoursup.geojson"
#     annee_cible = "2023"  # L'année doit être choisie de manière interactive
#     features = fetch_data_from_geojson(geojson_file_path, annee_cible)
#     create_interactive_map(features)
