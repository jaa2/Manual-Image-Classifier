import cv2

# Constants
TEXT_BORDER_COLOR = (0, 0, 0)
TEXT_MAIN_COLOR = (255, 255, 255)
TEXT_FONT = cv2.FONT_HERSHEY_DUPLEX

""" Gets the (arbitrary) weight from a given font size """
def font_get_weight(font_size):
    return max(1, int(font_size) * 2)

""" Draws text onto an image at a point"""
def border_text(img, text, point, font_size):
    border = min(5, int(font_size * 2))
    font_weight = font_get_weight(font_size)
    
    for i in range(4):
        xoff = (point[0] + (border if (i == 0) else 0)
            + (-border if (i == 2) else 0))
        yoff = (point[1] + (border if (i == 1 or i == 4 or i == 7) else 0)
            + (-border if (i == 3) else 0))
        cv2.putText(img, text, (xoff, yoff), TEXT_FONT, font_size,
                    TEXT_BORDER_COLOR, font_weight)
    cv2.putText(img, text, point, TEXT_FONT, font_size, TEXT_MAIN_COLOR,
                font_weight)

""" Draws text centered inside the image """
def border_text_centered(img, text, font_size):
    text_dims = get_text_dims(text, font_size)
    
    # Center of image
    text_point = ((img.shape[1] - text_dims[0]) // 2,
        (img.shape[0] + text_dims[1]) // 2)
    
    border_text(img, text, text_point, font_size)
    
""" Gets the dimensions (width, height) of a piece of text """
def get_text_dims(text, font_size):
    return cv2.getTextSize(text, TEXT_FONT,
        font_size, font_get_weight(font_size))[0]
