import os
import json
import tkinter
import argparse
from tkinter import *
import random

from util import imageops, load_categories, imageloader
from view.imageview import ImageWindow
from view import textdraw
from PIL import ImageTk

class MainApp:
    def __init__(self, master, starting_image, labels, eli):
        self.root = master
        frame = Frame(master)
        frame.pack(expand=1, fill=BOTH)
        
        self.top_label = Label(frame, text="")
        self.top_label.pack(side=TOP)
        
        self.photo_image = ImageTk.PhotoImage(starting_image)
        self.image = Label(frame, image=self.photo_image)
        self.image.pack(side=RIGHT, expand=1, fill=BOTH)
        
        self.controls_frame = Frame(frame)
        self.controls_frame.pack(side=LEFT)
        
        # Dictionary: label -> bool (whether the option is exclusive)
        self.exclusive_label_inds = eli
        
        self.buttons = {}
        
        # Number of buttons per row
        row_len = 2
        index = 0
        for label in labels:
            Label(self.controls_frame, text=label).grid(row=(index // row_len), sticky=W, columnspan=2)
            index += row_len
            self.buttons[label] = []
            for button_label in labels[label]:
                button = Button(self.controls_frame, text=button_label, command=lambda x=len(self.buttons[label]), label=label: self.change_button_colors(label, x))
                self.buttons[label].append(button)
                button.grid(row=(index // row_len), column=(index % row_len), sticky=W+E)
                
                index += 1
            index += row_len - index % row_len
        
        # Set button colors
        self.update_button_colors()
    
    def set_image(self, image):
        self.photo_image = ImageTk.PhotoImage(image)
        self.image.configure(image=self.photo_image)
        
        # Update buttons
        self.update_button_colors()
    
    def update_image_info(self, file_list):
        global cur_file
        self.top_label.configure(text="Image " + str(cur_file + 1) + " of "
            + str(len(file_list)) + ": " + file_list[cur_file])
    
    def get_image_dims(self):
        self.root.update()
        return (self.image.winfo_width(), self.image.winfo_height())
    
    def update_button_colors(self):
        global seen_list, cur_file, default_selections
        for label in self.buttons:
            for i, button in enumerate(self.buttons[label]):
                color = "#888888"
                if cur_file in seen_list:
                    # Just in case the JSON format changes
                    if not label in seen_list[cur_file]:
                        print("SETTING DEFAULTS")
                        seen_list[cur_file][label] = default_selections[label].copy()
                    while i >= len(seen_list[cur_file][label]):
                        seen_list[cur_file][label].append(0)
                    if seen_list[cur_file][label][i] == 1:
                        color = "#ee00ee"
                elif cur_file in seen_auto_list:
                    # TODO: FIX UP
                    # Just in case the JSON format changes
                    if not label in seen_auto_list[cur_file]:
                        print("SETTING DEFAULTS")
                        seen_auto_list[cur_file][label] = default_selections[label].copy()
                    while i >= len(seen_auto_list[cur_file][label]):
                        seen_auto_list[cur_file][label].append(0)
                    if seen_auto_list[cur_file][label][i] == 1:
                        color = "#aaaaff"
                button.configure(background=color)
    
    def change_button_colors(self, label, num, set_true=False):
        """ Changes all other colors to something else
            Exclusive: only one can be selected at a time."""
        global seen_list, cur_file, default_selections
        exclusive = self.exclusive_label_inds[label]
        
        if cur_file in seen_list:
            print("Found in seen_list:")
            print(seen_list[cur_file])
        else:
            print("NOT in seen list")
        
        # Has automatic version; use that
        if cur_file not in seen_list and cur_file in seen_auto_list:
            seen_list[cur_file] = seen_auto_list[cur_file]
        elif not cur_file in seen_list and not set_true:
            # Set this one
            result = {}
            result[label] = [0] * len(self.buttons[label])
            result[label][num] = 1
            seen_list[cur_file] = result
            print("Setting default of {} to {}".format(label, seen_list[cur_file][label]))
            
            # Set all others
            for ilabel in self.buttons:
                if ilabel != label:
                    self.change_button_colors(ilabel, 0, True)
            self.update_button_colors()
            return
        elif set_true:
            seen_list[cur_file][label] = default_selections[label].copy()
            print("(2) Setting default of {} to {}".format(label, seen_list[cur_file][label]))
            return
        
        if exclusive:
            for i, button in enumerate(self.buttons[label]):
                prev_selected = seen_list[cur_file][label][i] == 1
                seen_list[cur_file][label][i] = 1 if i == num and not prev_selected else 0
                print("For {}, setting {} to {}".format(label, i, seen_list[cur_file][label][i]))
        else:
            seen_list[cur_file][label][num] = 1 if seen_list[cur_file][label][num] == 0 else 0
            print("(2) For {}, setting {} to {}".format(label, num, seen_list[cur_file][label][num]))
        self.update_button_colors()
        
        print(seen_list[cur_file])
        print(seen_list[cur_file][label])

cur_file = 0
org_img = None
org_img_file = -1
seen_list = {}
# Files "seen" by automatic classification
seen_auto_list = {}
default_selections = {}
file_list = []

# Cache step rate. A cache_step_rate of 50 will load every 50th image in
# the cache range.
cache_step_rate = 1

def main(args):
    global seen_list, file_list
    folder = args.folder
    
    # Normalize folder path
    if not folder.endswith("/"):
        folder += "/"
    
    det_save_file = "det_save.json"
    det_auto_file = "det_save_auto.json"
    for root, dirs, files in os.walk(folder):
        for name in files:
            if (name[-4:].lower() == ".jpg" or name[-5:].lower() == ".jpeg"
                or name.endswith(".png")):
                file_list.append(root + "/" + name)

    file_list = sorted(file_list)
    global cur_file, org_img, org_img_file, cache_step_rate, default_selections
    cur_file = 0
    
    categories, default_selections, exclusives = load_categories.load_categories()

    if len(file_list) == 0:
        print("No images found!")
        return
    
    # Files automatically matched
    file_auto_list = []
    # Load automatically sorted images
    try:
        json_file = open(det_auto_file, "r")
        file_auto_list = json.load(json_file)
        print("Loaded {} auto files".format(len(file_auto_list)))
        json_file.close()
    except FileNotFoundError:
        pass

    file_seen_list = []
    try:
        json_file = open(det_save_file, "r")
        file_seen_list = json.load(json_file)
        json_file.close()
        
        didsee_list = []
        didsee_auto_list = []
        didnotsee_list_org = []
        didnotsee_list = []
        
        # Find all the files already seen
        for f in file_list:
            if f[len(folder):] in file_seen_list:
                didsee_list.append(f)
            else:
                didnotsee_list_org.append(f)
        
        # Find files automatically seen
        if len(file_auto_list) > 0:
            for f in didnotsee_list_org:
                if f[len(folder):] in file_auto_list:
                    didsee_auto_list.append(f)
                else:
                    didnotsee_list.append(f)
        else:
            didnotsee_list = didnotsee_list_org
                    
        
        # Put the ones you already saw at the beginning
        random.shuffle(didsee_auto_list)
        random.shuffle(didnotsee_list)
        file_list = didsee_list + didsee_auto_list + didnotsee_list
        
        for f in file_seen_list:
            f = folder + f
            if f in file_list:
                seen_list[file_list.index(f)] = file_seen_list[f[len(folder):]]
        
        for f in file_auto_list:
            f = folder + f
            if f in file_list:
                seen_auto_list[file_list.index(f)] = file_auto_list[f[len(folder):]]
    except FileNotFoundError:
        random.shuffle(file_list)
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
    
    # Set cache range parameters
    IMAGE_CACHE_MAX_BACK = 3
    IMAGE_CACHE_MAX_AHEAD = 40
    IMAGE_CACHE_SIZE = IMAGE_CACHE_MAX_BACK + IMAGE_CACHE_MAX_AHEAD
    IMAGE_CACHE_MAX_SIZE = max(IMAGE_CACHE_SIZE, 60)
    
    KEY_WAIT = 20
    
    # Create the main GUI
    view_dims = (1920 * 8 // 10, 1080 * 9 // 10)
    image_loader = imageloader.ImageLoader(view_dims, IMAGE_CACHE_MAX_SIZE)
    org_img = image_loader.get_image(file_list[cur_file], cur_file)
    
    root = Tk()
    app = MainApp(root, org_img, categories, exclusives)
    view_dims = app.get_image_dims()
    image_loader.set_view_dims(view_dims)
    app.set_image(image_loader.get_image(file_list[cur_file], cur_file))
    
    def mymainloop(event):
        global cur_file, org_img_file, cache_step_rate
        if cur_file != org_img_file:
            org_img = image_loader.get_image(file_list[cur_file], cur_file)
            org_img_file = cur_file
            print("Setting image")
            app.update_image_info(file_list)
            app.set_image(org_img)
        image_loader.update_cache(get_target_cache_fnames(cache_step_rate))
        
        #TODO: key = cv2.waitKey(KEY_WAIT)
        key = event.keysym
        print("Keysym: {}".format(key))
        #TODO if not window.is_visible():
        #    break
        
        # Scroll forward with right arrow key or ] or D
        if key == "Right" or key == "bracketright" or key == "d":
            cur_file += 1
            cache_step_rate = 1
        
        # Go back with left arrow key or [ or A
        if key == "Left" or key == "bracketleft" or key == "a":
            cur_file -= 1
            cache_step_rate = 1
        
        # Scroll fast forward - }
        if key == "braceright":
            cur_file += 50
            cache_step_rate = 50
        # Scroll fast backward - {
        if key == "braceleft":
            cur_file -= 50
            cache_step_rate = 50
        
        cur_file = get_cur_offset(cur_file, 0)
        
        # Change category using the numbers 0-9
        """if key >= 48 and key <= 57:
            category_num = key - 48
            category_id_str = str(category_num)
            if category_id_str in categories:
                seen_list[cur_file] = category_id_str"""
        
        # M key - find next unseen image
        if key == "m" and len(seen_list) < len(file_list):
            while (cur_file in seen_list):
                cur_file = get_cur_offset(cur_file, 1)
        
        # F key - use automatic if one exists
        if key == "f" and cur_file in seen_auto_list and cur_file not in seen_list:
            seen_list[cur_file] = seen_auto_list[cur_file]
            app.update_button_colors()
        
        # Q key - quit
        if key == "q":
            root.destroy()
            return
    
    def cacheloop():
        global cur_file, org_img, org_img_file, cache_step_rate
        if cur_file != org_img_file:
            org_img = image_loader.get_image(file_list[cur_file], cur_file)
            org_img_file = cur_file
            
            app.update_image_info(file_list)
            app.set_image(org_img)
        image_loader.update_cache(get_target_cache_fnames(cache_step_rate))
        root.after(KEY_WAIT, cacheloop)
    
    # Do the main loop
    root.bind_all("<Key>", mymainloop)
    root.after(KEY_WAIT, cacheloop)
    root.mainloop()
    
    named_seen_list = {}
    for seen_id in seen_list:
        # Store without the root folder
        named_seen_list[file_list[seen_id][len(folder):]] = seen_list[seen_id]

    print(str(len(seen_list)) + " photo decisions saved.")
    out_file = open(det_save_file, "w")
    json.dump(named_seen_list, out_file, indent=2)
    out_file.close()
    
    # Close window before cleaning up
    # TODO window.destroy()
    image_loader.clean_up()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder", help="Image folder to search", default="imgfolder")
    main(parser.parse_args())
