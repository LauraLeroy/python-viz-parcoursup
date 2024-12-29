import os
import requests
import json

response_API = requests.get('https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-esr-parcoursup/records?limit=1')

if response_API.status_code == 200:
    data = response_API.text
    parsed_data = json.loads(data)

    output_dir = 'data/raw'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    output_file = os.path.join(output_dir, 'data.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(parsed_data, f, ensure_ascii=False, indent=4)
    
    print(f"Les données ont été enregistrées dans {output_file}")
else:
    print("La requête API a échoué avec le code :", response_API.status_code)
