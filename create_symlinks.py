import json
import os
import argparse
import random
import shutil

from util.load_categories import load_categories

def main(args):
    det_save_file = "det_save.json"
    file_list = {}
    try:
        json_file = open(det_save_file, "r")
        file_list = json.load(json_file)
        json_file.close()
    except FileNotFoundError:
        print(det_save_file + " not found!")
        return

    categories = load_categories()
    
    for category in categories:
        category_dir = args.output_dir + "/" + categories[category]
        try:
            os.mkdir(category_dir)
        except FileExistsError:
            print("Clearing the category directory " + categories[category] + "...")
            shutil.rmtree(category_dir)
            os.mkdir(category_dir)

    # Equal categories for each folder
    dirs = {}
    dirs_file_lists = {}
    for f in file_list:
        head, tail = os.path.split(f)
        if head not in dirs:
            dirs[head] = {}
            dirs_file_lists[head] = []
            for category in categories:
                dirs[head][category] = 0
        dirs[head][file_list[f]] += 1
        dirs_file_lists[head].append(f)
    
    # Have equal categories for this dir
    i = 0
    for _dir in dirs:
        random.shuffle(dirs_file_lists[_dir])
        categories_used = {}
        for category in categories:
            categories_used[category] = 0
        
        print("")
        print("For dir '" + _dir + "':")
        print("Dir's head values: " + str(dirs[_dir]))
        min_category_count = min(dirs[_dir].values())
        # This is where it decides *how* equal it is
        # In this case, we will allow 2-5 more photos in one category
        # max_pics_per_cat = min(min_category_count + 5, (min_category_count + 1) * 2)
        max_pics_per_cat = 10000000000
        print("Max pics per category: " + str(max_pics_per_cat))
        
        for f in dirs_file_lists[_dir]:
            if categories_used[file_list[f]] < max_pics_per_cat:
                this_dir = args.output_dir + "/" + categories[file_list[f]]
                os.symlink(os.path.relpath(f, this_dir), this_dir + "/" + str(i) + ".jpg")
                categories_used[file_list[f]] += 1
            i += 1
        
        for category in categories:
            print("Created " + str(categories_used[category]) + " symlinks"
                + " in category '" + categories[category] + "'.")
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create symlinks.")
    parser.add_argument("output_dir", help="Output directory for the symlinks.")
    args = parser.parse_args()
    main(args)
