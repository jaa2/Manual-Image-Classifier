import cv2
import numpy as np

# Constants
DEFAULT_WINDOW_WIDTH = 1920
DEFAULT_WINDOW_HEIGHT = 1080
LIGHT_GRAY = 235

""" Class for displaying images using OpenCV """
class ImageWindow:

    """ Name of the window """
    window_name = "Image"
    
    def __init__(self, window_name):
        self.window_name = window_name
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, DEFAULT_WINDOW_WIDTH,
            DEFAULT_WINDOW_HEIGHT)
        
        # Show a temporary image so that viewing rectangle calculations are
        # correct
        im_small = np.zeros((1, 1, 3), np.uint8)
        im_small.fill(LIGHT_GRAY)
        self.show_image(im_small)
        cv2.waitKey(10)
        del im_small
    
    def get_name(self):
        return self.window_name
    
    def is_visible(self):
        return cv2.getWindowProperty(self.window_name, cv2.WND_PROP_VISIBLE) > 0
    
    def show_image(self, image):
        cv2.imshow(self.window_name, image)
    
    """ Sends a destroy signal to the current window. Note that after this call
        ends, the window may not yet be completely destroyed. """
    def destroy(self):
        cv2.destroyWindow(self.window_name)
    
    """ Finds the "viewing dimensions" (width, height) of images shown in this
        window """
    def get_view_dims(self):
        # Find maximum width
        blank_img_width = np.zeros((1, 100, 3), np.uint8)
        blank_img_width.fill(LIGHT_GRAY)
        self.show_image(blank_img_width)
        cv2.waitKey(1)
        max_width = cv2.getWindowImageRect(self.window_name)[2]
        del blank_img_width
        
        # Find maximum height
        blank_img_height = np.zeros((100, 1, 3), np.uint8)
        blank_img_height.fill(LIGHT_GRAY)
        self.show_image(blank_img_height)
        cv2.waitKey(1)
        max_height = cv2.getWindowImageRect(self.window_name)[3]
        del blank_img_height
        
        return (max_width, max_height)
