import pytesseract
from pytesseract import Output
import cv2, time
import statistics
from statistics import mode
from PIL import Image, ImageDraw, ImageFont
import numpy as np
### Import characters list
f = open("chars.map",'r', encoding = "utf8")
char_list = f.read().split("\n")
f.close()

def text_phantom(text, size = 0, font ='arial'):
    fontsize = 10
    text_height=0
    text = (text+ " ")*10+ "aawe "
    while text_height < size:
        fontsize= fontsize + (size-text_height)//2 + 1
        pil_font = ImageFont.truetype(font + ".ttf", size=fontsize,
                                      encoding="unic")
        text_width, text_height = pil_font.getsize(text)
        print( str(fontsize)+str(text_width," ",text_height) )
        canvas = Image.new('RGB', [text_width+100, text_height+100], (0, 0, 0))
        draw = ImageDraw.Draw(canvas)
        offset = (50,50)
        draw.text(offset, text, font=pil_font, fill="#ffffff")
        box = pytesseract.image_to_boxes(np.asarray(canvas), output_type=Output.DICT )
        # print(box)
        try:
            text_height = mode(box["top"])-mode(box["bottom"])
        except:
            break
    print(f"letter: {text[0]}, fontsize: {fontsize}")

    text_width, text_height = pil_font.getsize(text[0])
    canvas = Image.new('RGB', [text_width, text_height], (0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    offset = (0,0)
    draw.text(offset, text[0], font=pil_font, fill="#ffffff")
    n_letter = np.asarray(canvas)
    n_letter = n_letter[text_height- mode(box["top"])+50 : text_height - mode(box["bottom"])+50,:,:]

    # Convert the canvas into an array with values in [0, 1]
    return n_letter / 255.0 , fontsize

# make text numpy array
def text_numpy(text, size , font ='arial'):
        pil_font = ImageFont.truetype(font + ".ttf", size=size,
                                      encoding="unic")
        text_width, text_height = pil_font.getsize(text)
        canvas = Image.new('RGB', [text_width, text_height], (0, 0, 0))
        # draw the text onto the canvas
        draw = ImageDraw.Draw(canvas)
        offset = (0,0)
        black = "#ffffff"
        draw.text(offset, text, font=pil_font, fill=black)
        # Convert the canvas into an array with values in [0, 1]
        result = np.asarray(canvas) / 255.0 
        # Crop image
        top = int( char_size_list[text][1]/120*size)
        bottom = int( char_size_list[text][2]/120*size)
        return result[text_height-top:text_height-bottom,:,:]



# Get list char_size_list for font 120
font = "ttf\\OpenSans-Regular"

for text in char_list:
    pil_font = ImageFont.truetype(font+".ttf", size=120,
                                  encoding="unic")
    text_width, text_height = pil_font.getsize(text)
    canvas = Image.new('RGB', [text_width, text_height], (0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    offset = (0,0)
    draw.text(offset, text, font=pil_font, fill="#ffffff")
    img = np.asarray(canvas)
    # char_size_list[text[0]] = [text_height, mode(box["top"])-50,mode(box["bottom"])-50]
    for i in range(text_height):
        if np.sum(img[:i,:,:])>200:
            top = i
            break
    for i in reversed(range(text_height)):
        if np.sum(img[i:,:,:])>200:
            bottom = i
            break
    for i in range(text_width):
        if np.sum(img[:,:i,:])>200:
            left = i
            break
    for i in reversed(range(text_width)):
        if np.sum(img[:,i:,:])>200:
            right = i
            break

    # print(top)

    img = img[top:bottom,left:right,:]
    print(f"{text[0]} {img.shape}  {top} {bottom} {left} {right} ")

    # Save result
    text_height = img.shape[0]
    text_width = img.shape[1]
    dot = np.count_nonzero(img)
    im = Image.fromarray(img, 'RGB')
    fontt = font.split("\\")[-1]
    im.save(f'font\\{fontt}\\{ord(text[0])}_{text_height}_{text_width}_{dot}.jpg')















# ### Resize img 
# scale_percent=40
# width = int(img.shape[1] * scale_percent / 100)
# height = int(img.shape[0] * scale_percent / 100)
# dim = (width, height)
# img = cv2.resize(img, dim,interpolation = cv2.INTER_AREA )