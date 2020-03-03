import json

def load_categories():
    with open('categories.json') as json_data:
        json_obj = json.load(json_data)
        categories = json_obj["categories"]
        default_category = json_obj["default"]
        
        print(str(len(categories)) + " categories loaded: " + str(categories))
        if default_category:
            print("Default category: " + str(default_category))
        return categories, default_category
