import json

data_loc = "../data/synthetic/components"

# load catalog from jsons
CATEGORIES = ['cases', 'coolers', 'cpus', 'fans', 'gpus', 'lighting', 'motherboards', 'psus', 'ram', 'storage']
CATALOG = {}
for category in CATEGORIES:
    with open(f'{data_loc}/{category}.json', 'r') as file:
        cat_data = json.load(file)
    CATALOG[category] = cat_data

# make mobo names from their brands + models
def get_mobo_name(mobo):
    return f"{mobo['brand']} {mobo['model']}"

for mobo in CATALOG['motherboards']: mobo['name'] = get_mobo_name(mobo)