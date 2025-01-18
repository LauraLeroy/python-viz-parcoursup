from typing import Dict, Any
from dash import html

def process_api_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Traite la réponse de l'API pour extraire les données pertinentes.
    
    Args:
        response (Dict[str, Any]): La réponse JSON de l'API.
        
    Returns:
        Dict[str, Any]: Les données extraites et transformées.
    """
    if(not response or response["total_count"] == 0 or response["results"] == []):
        return html.P("Aucune donnée trouvée pour cette recherche.")

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


import os
import requests
from pathlib import Path
import hashlib
from urllib.parse import urlparse
import re

def get_filename_from_url(url: str, response_headers: dict = None) -> str:
    """
    Extrait le nom du fichier de l'URL ou des headers de réponse.
    """
    # Essayer d'abord d'obtenir le nom depuis Content-Disposition
    if response_headers and "Content-Disposition" in response_headers:
        cd = response_headers["Content-Disposition"]
        if "filename=" in cd:
            return re.findall("filename=(.+)", cd)[0].strip('"')
    
    # Sinon, construire un nom basé sur le dataset et le format
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.split('/')
    
    # Trouver le nom du dataset et le format
    dataset_name = next((part for part in path_parts if "fr-esr" in part), "dataset")
    format_type = "geojson" if "geojson" in url else "json"
    
    return f"{dataset_name}.{format_type}"

def get_latest_data(url: str, target_dir: str = "./data/raw") -> bool:
    """
    Télécharge le fichier depuis l'URL si nouveau ou inexistant.
    
    Args:
        url (str): URL de téléchargement direct du fichier
        target_dir (str): Chemin du dossier cible pour sauvegarder le fichier
        
    Returns:
        bool: True si un nouveau fichier a été téléchargé, False sinon
    """
    target_path = Path(target_dir).resolve()
    
    # Faire une première requête pour obtenir les headers
    response = requests.head(url)
    filename = get_filename_from_url(url, response.headers)
    
    file_path = target_path / filename
    temp_file = target_path / f"temp_{filename}"

    # Télécharger le fichier dans un fichier temporaire pour pouvoir le comparer plus tard
    response = requests.get(url, stream=True)
    response.raise_for_status()

    # Écrire le contenu dans un fichier temporaire
    with open(temp_file, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    
    # Si le fichier original n'existe pas, renommer le fichier temporaire pour avoir le bon nom
    if not file_path.exists():
        os.rename(temp_file, file_path)
        return True
        
    # Comparer les fichiers (D'après chatPGT)
    def get_file_hash(file_path):
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    if get_file_hash(temp_file) != get_file_hash(file_path):
        # Si les fichiers sont différents, remplacer l'ancien fichier
        os.replace(temp_file, file_path)
        return True
    else:
        #les fichiers sont identiques, on supprime le fichier temporaire
        os.remove(temp_file)
        return False