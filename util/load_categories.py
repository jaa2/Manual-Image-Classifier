import json

def load_categories():
    with open('categories.json') as json_data:
        json_obj = json.load(json_data)
        categories_org = json_obj["categories"]
        
        categories_final = {}
        default_selections = {}
        exclusives = {}
        for category in categories_org:
            categories_final[category] = categories_org[category]["items"]
            default_selections[category] = categories_org[category]["defaults"]
            exclusives[category] = categories_org[category]["exclusive"]
            if exclusives[category] and len([x for x in default_selections[category] if x == 1]) != 1:
                raise ValueError("ERROR: Category " + category + " is exclusive, so it must have exactly one default selection.")
            if len(default_selections[category]) != len(categories_org[category]["items"]):
                raise ValueError("ERROR: Category " + category + " does not have the correct number of items in its default list. Expected " + str(len(categories_org[category]["items"])) + " but got " + str(len(default_selections[category])))
        
        print(str(len(categories_final)) + " categories loaded: " + str(categories_final))
        return categories_final, default_selections, exclusives
