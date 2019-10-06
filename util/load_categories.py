import json

def load_categories():
    with open('categories.json') as json_data:
        categories = json.load(json_data)
        print(str(len(categories)) + " categories loaded: " + str(categories))
        return categories
