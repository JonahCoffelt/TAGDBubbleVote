# This QR Code Generator is brought to you by Ethan Edgington.
# Check out www.gameswithstyle.com for more of my work!
# Import modules
import qrcode
import math
from PIL import Image

logosDirectory = "" # Quickly type what file to seach for center images in (Ex: "Logos/")
codesDirectory = "" # Quickly type what file to generate QR codes in (Ex: "QR Codes/")
fileType = "png"    # Allows you to adjust what file type images are saved as (Ex: png, jpg)

def generate_qr_code(url, name, bx_sz, brdr, light_color, dark_color, img, img_size, correctionInput):

    # Gets the image
    if (img != "" and img_size > 0 and correctionInput > 0):
        logo = Image.open(logosDirectory + img)   # Be sure to navigate to whatever directory your image is in
    
        # Adding an image requires using correction
        match correctionInput:
            case 1:
                correction = qrcode.ERROR_CORRECT_L
            case 2:
                correction = qrcode.ERROR_CORRECT_M
            case 3:
                correction = qrcode.ERROR_CORRECT_Q
            case 4:
                correction = qrcode.ERROR_CORRECT_H

        if (correctionInput == 1):
            correction = qrcode.ERROR_CORRECT_L

        # img_size must be odd
        realImgSize = (2*img_size - 1) * bx_sz

        # Adjust image size
        wpercent = (realImgSize/float(logo.size[0]))
        hsize = int((float(logo.size[1])*float(wpercent)))

        # For some reason, box sizes of 15 * 2^n makes the image one pixel too short
        # I would guess this has to do with antialiasing?
        if (math.log2(bx_sz / 15).is_integer()):
            hsize += 1
        hsize += 1

        logo = logo.resize((realImgSize, hsize))
    else:
        correction = 0

    QRcode = qrcode.QRCode(
        version = None,                 # From 1-40 or "None" if fit=True
        error_correction = correction,  # Correction constants - L: 7%, M: 15%, Q: 25%, H: 30%
        box_size = bx_sz,               # How many pixels each box gets
        border = brdr                   # How many boxes thick the outside border gets
    )

    QRcode.add_data(url)    # Adding URL or text to QRcode
    QRcode.make(fit=True)   # Generating QR code

    # Adding color to QR code
    QRimg = QRcode.make_image(fill_color = smartRGB(dark_color), back_color = smartRGB(light_color)).convert('RGB')

    # Set size of image if you have one
    if (img != "" and img_size > 0 and correctionInput > 0):
        pos = ((QRimg.size[0] - logo.size[0]) // 2,
            (QRimg.size[1] - logo.size[1]) // 2)
        QRimg.paste(logo, pos)

    # Save the QR code
    QRimg.save(codesDirectory + name + '.' + fileType)
    print('QR code generated!')             # Let the user know it generated correctly



# Converts hex to rgp tuple
def hex_to_rgb(hex):
    h = hex.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))



# Ensures the input returns RGP, regardless of inputting rgb or hex
def smartRGB(value):
    rgbTuple = (0, 0, 0)

    # Try to set the tuple equal to the value
    try:
        rgbTuple = value

    # If that didn't work, it's not a tuple
    except:

        # So hopefully it's a hex code
        try:
            rgbTuple = hex_to_rgb(value)

        # If not, the user is beyond help. Return black
        except:
            pass

    return rgbTuple
