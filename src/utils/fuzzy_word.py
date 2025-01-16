from fuzzywuzzy import process
import pandas as pd

# Listes des catégories de BUT
BUT_PRODUCTION_LIST = [
    "Chimie", "Génie biologique", "Génie chimique, génie des procédés", 
    "Génie civil, construction durable", "Génie électrique et informatique industrielle",
    "Génie industriel et maintenance", "Génie mécanique et productique", 
    "Hygiène Sécurité Environnement", "Informatique", "Mesures physiques", 
    "Métiers de la transition et de l’efficacité énergétique", "Packaging, emballage et conditionnement", 
    "Qualité, logistique industrielle et organisation", "Réseaux et télécommunications", 
    "Science et génie des matériaux"
]

BUT_SERVICE_LIST = [
    "Gestion des Entreprises et des Administrations", 
    "Techniques de Commercialisation", 
    "Gestion Administrative et Commerciale des Organisations", 
    "Info-Com", "Métiers du Multimédia et de l’Internet", 
    "Carrières Juridiques", "Carrière Sociales"
]

DE_SOCIAL = [
    "Educateur spécialisé", "Educateur de jeunes enfants", "Assistant de service social",
]

DE_SANITAIRE = [
    "Orthophoniste", "Orthoptiste", "Infirmier", "Manipulateur en électroradiologie médicale",
    "Psychomotricien","Audioprothésiste", "Technicien de laboratoire médical",
    "Ergothérapeute", "Podologue"
]

CPGE_DICT = {"Classe préparatoire aux études supérieures":"CUPGE",
             "Classe préparatoire scientifique":"CPGE S",
              "Classe préparatoire littéraire":"CPGE L",
              "Classe préparatoire économique et commerciale":"CPGE ECG",
        }

def categorize(query,alt_query, value_index_map):
    """
    Retourne la catégorie du BUT ou la meilleure correspondance fuzzy, avec l'index dans le CSV.

    Args:
        query (str): La chaîne à rechercher.
        value_index_map (dict): Dictionnaire des valeurs avec leur index.

    Returns:
        str: Le type de BUT (Production ou Service) ou la meilleure correspondance fuzzy, et l'index.
    """
    values = list(value_index_map.keys())  # Obtenir les valeurs pour la recherche fuzzy

    if "BTS" in query:
        first_fifteen_letters = query[:15]
        best_match = process.extractOne(first_fifteen_letters, values)
        return best_match[0]
    if "BUT" in query:
        best_match_production = process.extractOne(query, BUT_PRODUCTION_LIST)
        best_match_service = process.extractOne(query, BUT_SERVICE_LIST)
        if best_match_production and best_match_service:
            if best_match_production[1] >= best_match_service[1]:
                return "BUT Production"
            else:
                return "BUT Service"
        elif best_match_production:
            return "BUT Production"
        elif best_match_service:
            return "BUT Service"
        else:
            return ""
    if "D.E" in query:
        best_match_social = process.extractOne(query, DE_SOCIAL)
        best_match_sanitaire = process.extractOne(query, DE_SANITAIRE)
        if best_match_social and best_match_sanitaire:
            if best_match_social[1] >= best_match_sanitaire[1]:
                return "D.E social"
            else:
                return "D.E sanitaire"
        elif best_match_social:
            return "D.E social"
        elif best_match_sanitaire:
            return "D.E sanitaire"
        else:
            return ""
    if "Classe préparatoire" in alt_query:
        new_query = CPGE_DICT[alt_query]
        return process.extractOne(new_query, values)[0] 
    # Recherche fuzzy classique si "BUT" n'est pas dans la chaîne
    best_match = process.extractOne(query, values)
    if best_match:
        matched_value = best_match[0]
        score = best_match[1]
        index = value_index_map[matched_value]  # Récupérer l'index à partir du dictionnaire
        return matched_value #f"Meilleure correspondance : {matched_value} (score : {score}), Index : {index}"
    else:
        return ""