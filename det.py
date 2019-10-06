import cv2
import os
import json

from util import imageops, load_categories, imageloader
from view.imageview import ImageWindow
from view import textdraw

def main():
    file_list = []
    seen_list = {}
    folder = "imgfolder"
    det_save_file = "det_save.json"
    for root, dirs, files in os.walk(folder):
        for name in files:
            if name[-4:].lower() == ".jpg" or name[-5:].lower() == ".jpeg":
                file_list.append(root + "/" + name)

    file_list = sorted(file_list)
    cur_file = 0
    
    categories = load_categories.load_categories()

    if len(file_list) == 0:
        print("No images found!")
        return

    try:
        json_file = open(det_save_file, "r")
        file_seen_list = json.load(json_file)
        for f in file_seen_list:
            if f in file_list:
                seen_list[file_list.index(f)] = file_seen_list[f]
        json_file.close()
    except FileNotFoundError:
        pass

    def get_cur_offset(cur, off):
        cur += off
        cur = cur % len(file_list)
        return cur
    
    """ Create a list of target cache filenames. This will be list of images
        that are (currently) to remain in the cache. """
    def get_target_cache_fnames(step_rate = 1):
        target_fnames = []
        for i in range(-IMAGE_CACHE_MAX_BACK, IMAGE_CACHE_MAX_AHEAD + 1):
            filename = file_list[get_cur_offset(cur_file, i * step_rate)]
            if filename not in target_fnames:
                target_fnames.append(filename)
        return target_fnames
    
    def redraw_image(org_img, cur_file):
        img = org_img.copy()
        img_text = "Image " + str(cur_file + 1) + " of " + str(len(file_list)) +": " + file_list[cur_file]
        font_size = 1
        
        textdraw.border_text(img, img_text, (10, int(30 * font_size)), font_size)
        if len(seen_list) == len(file_list):
            textdraw.border_text(img, "All seen!", (10, int(3 * 30 * font_size)), font_size)
        if cur_file in seen_list:
            # Put chosen category in the center of the image
            category_text = categories[seen_list[cur_file]]
            font_mult = 5
            textdraw.border_text_centered(img, category_text, font_size * font_mult)
        else:
            # Not chosen; you could set a default here if you want
            pass
            # seen_list[cur_file] = 0
        return img
    
    # Set cache range parameters
    IMAGE_CACHE_MAX_BACK = 3
    IMAGE_CACHE_MAX_AHEAD = 40
    IMAGE_CACHE_SIZE = IMAGE_CACHE_MAX_BACK + IMAGE_CACHE_MAX_AHEAD
    IMAGE_CACHE_MAX_SIZE = max(IMAGE_CACHE_SIZE, 60)
    
    KEY_WAIT = 20
    window = ImageWindow("Image")
    view_dims = window.get_view_dims()
    image_loader = imageloader.ImageLoader(view_dims, IMAGE_CACHE_MAX_SIZE)
    org_img = None
    org_img_file = -1
    
    # Cache step rate. A cache_step_rate of 50 will load every 50th image in
    # the cache range.
    cache_step_rate = 1
    
    img = None
    while True:
        if cur_file != org_img_file:
            org_img = image_loader.get_image(file_list[cur_file], cur_file)
            org_img_file = cur_file
            img = redraw_image(org_img, cur_file)
            window.show_image(img)
        image_loader.update_cache(get_target_cache_fnames(cache_step_rate))
        
        key = cv2.waitKey(KEY_WAIT)
        if not window.is_visible():
            break
        
        # Scroll forward with right arrow key or ] or D
        if key == 93 or key == 83 or key == 100:
            cur_file += 1
            cache_step_rate = 1
        
        # Go back with left arrow key or [ or A
        if key == 91 or key == 81 or key == 97:
            cur_file -= 1
            cache_step_rate = 1
        
        # Scroll fast forward - }
        if key == 125:
            cur_file += 50
            cache_step_rate = 50
        # Scroll fast backward - {
        if key == 123:
            cur_file -= 50
            cache_step_rate = 50
        
        cur_file = get_cur_offset(cur_file, 0)
        
        # Change category using the numbers 0-9
        if key >= 48 and key <= 57:
            category_num = key - 48
            category_id_str = str(category_num)
            if category_id_str in categories:
                seen_list[cur_file] = category_id_str
                img = redraw_image(org_img, cur_file)
                window.show_image(img)
        
        # M key - find next unseen image
        if key == 109 and len(seen_list) < len(file_list):
            while (cur_file in seen_list):
                cur_file = get_cur_offset(cur_file, 1)
        
        # Q key - quit
        if key == 113:
            break

    named_seen_list = {}
    for seen_id in seen_list:
      named_seen_list[file_list[seen_id]] = seen_list[seen_id]

    print(str(len(seen_list)) + " photo decisions saved.")
    out_file = open(det_save_file, "w")
    json.dump(named_seen_list, out_file, indent=2)
    out_file.close()
    
    # Close window before cleaning up
    window.destroy()
    image_loader.clean_up()

if __name__ == "__main__":
    main()
