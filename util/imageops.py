import cv2
import numpy as np

""" Resizes an image to fit a maximum width or height.
    @param img  Image to resize
    @param max_width    Maximum acceptable width
    @param max_height   Maximum acceptable height
"""
def image_resize_to_fit(img, max_width, max_height):
    width = img.shape[1]
    height = img.shape[0]

    ratio_width = max_width / width
    ratio_height = max_height / height

    new_width = width
    new_height = height

    if ratio_width < ratio_height:
        new_width = max_width
        new_height = int(height * ratio_width)
    else:
        new_height = max_height
        new_width = int(width * ratio_height)

    new_img = cv2.resize(img, (new_width, new_height))
    del img
    return new_img

""" "Letterboxes" an image to a given width and height. """
def image_letterbox(img, width, height):
    # Create background image
    new_img = np.zeros((height, width, 3), np.uint8)
    # Light gray
    new_img.fill(235)
    
    # Resize the original image
    img_resized = image_resize_to_fit(img, width, height)
    
    # Find where to paste
    paste_x = 0
    paste_y = 0
    
    if img_resized.shape[1] == width:
        # Center the image vertically; it spans the whole width
        paste_y = int((height - img_resized.shape[0]) / 2)
    else:
        # Center the image horizontally; it spans the whole height
        paste_x = int((width - img_resized.shape[1]) / 2)
    
    # Paste letterboxed image
    new_img[paste_y:paste_y + img_resized.shape[0],
        paste_x:paste_x + img_resized.shape[1]] = img_resized
    
    return new_img
