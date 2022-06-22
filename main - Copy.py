import pytesseract
from pytesseract import Output
import cv2, time
import statistics
from statistics import mode
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from os import listdir
from os.path import isfile, isdir, join

step = 2

### Import characters list
print("importing font...")
characters=[]
for font in listdir("font"):
    if isdir(join("font",font)):
        for ch in listdir( join("font",font) ):
            if isfile( join("font",font,ch) ) and ".jpg" in ch:
                temp = ch[:-4].split("_")
                img = cv2.imread(join("font",font,ch))
                img[img<100]=0
                img[img>100]=1
                characters +=[{ 
                    "char" : chr(int(temp[0])),
                    "height" : int(temp[1]),
                    "width" : int(temp[2]),
                    "dot" : int(temp[3]),
                    "img" : img
                    }]


#### Count different values
def diff_char( img_char, n_letter, dot, offset=(0,0)):

    ### Offset (height, width)
    temp = np.zeros( (n_letter.shape[0]+offset[0],n_letter.shape[1]+offset[1]) )
    temp[offset[0]:,offset[1]:]= n_letter[:,:,0]
    n_letter = temp
    img_char = img_char[:,:,0]

    if img_char.shape[1]-n_letter.shape[1]<0-img_char.shape[1]*0.2:
        return [0]
    img_char[img_char>100]=100
    img_char[img_char<100]=1
    img_char[img_char==100]=0
    root1 = np.count_nonzero(n_letter)
    root2 = np.count_nonzero(img_char)

    temp = np.zeros( (max(img_char.shape[0],n_letter.shape[0]),max(img_char.shape[1],n_letter.shape[1]))  )
    temp[:img_char.shape[0],:img_char.shape[1]]= temp[:img_char.shape[0],:img_char.shape[1]]+img_char
    temp[:n_letter.shape[0],:n_letter.shape[1]] = temp[:n_letter.shape[0],:n_letter.shape[1]]+n_letter

    # Counting
    same = np.count_nonzero(temp)
    dif = np.sum(temp)
    a = int(dif - same)
    dif = same - a
    same = same - dif

    # cv2.imshow('le', n_letter)
    # cv2.imshow('img', img_char)
    # cv2.imshow('tem', temp)
    # cv2.waitKey(0)
    return [same/root2,dif/root2,root1,root2, dot ]





img = cv2.imread('test.jpg')

char = pytesseract.image_to_boxes(img, output_type=Output.DICT)
print(char)
n_boxes = len(char['char'])

# ### Get moderate height of text
# char_h=[]
# for i in range(n_boxes):
#     char_h+=[char["top"][i]-char["bottom"][i]]
# average=sum(char_h)/len(char_h)
# char_h = [t for t in char_h if t<=average]
# print(mode(char_h))

print("ocr...")
### Find size of text:
heights = [char['top'][i] - char['bottom'][i] for i in range(len(char["top"])) ]
heights_avg = sum(heights)/len(heights)
heights = [t for t in heights if t<heights_avg]
size = mode(heights)/62

for i_char in range(len(char["left"])):
    h = img.shape[0]
    (x,y,x1,y1) = (char['left'][i_char], img.shape[0] - char['top'][i_char], char['right'][i_char], img.shape[0] - char['bottom'][i_char])
    temp = img[y:y1,x:x1,:]

    # temp_result = []
    # for text in char_list:
    #     size = int(abs(y-y1)*120/ char_size_list[text][0] )
    #     # n_letter = text_phantom(text, fontsize = size )
    #     n_letter = text_numpy( text, size )
    #     diff = diff_char( img[h-y:h-y1, x:x1 ,:], n_letter )
    #     if diff[0]>0.5:
    #         temp_result+=[diff+[text]]
    # try:
    #     result = max(temp_result, key = lambda x:x[0] )
    # except:
    #     print(f"error {i_char} ")
    # print(result)

    res = []
    for letter in characters:
        # if letter["char"]!="T":continue
        n_letter = letter["img"]
        ### Resize img 
        # dim = ( int( letter["width"]*(y1-y)/letter["height"]) , y1-y )
        dim = ( int(letter["width"]*size), int(letter["height"]*size) )
        n_letter = cv2.resize(n_letter, dim,interpolation = cv2.INTER_AREA )

        for ofs_x in range ( abs(n_letter.shape[1]-(x1-x))//step ):
            for ofs_y in range ( abs(n_letter.shape[0]-(y1-y))//step ):
                diff = diff_char(temp, n_letter,letter["dot"], offset = (ofs_y*step,ofs_x*step))
                # print(diff)
                if diff[0]>0.1:
                    res+=[ diff +[letter["char"]] ]

    
    # print(res)
    res = [r for r in res if r[0]>0.5 and r[1]<0.2 ]
    result = max(res, key = lambda x:x[4])
    print(result)


# cv2.imshow('img', img)
# cv2.waitKey(0)
















# ### Resize img 
# scale_percent=40
# width = int(img.shape[1] * scale_percent / 100)
# height = int(img.shape[0] * scale_percent / 100)
# dim = (width, height)
# img = cv2.resize(img, dim,interpolation = cv2.INTER_AREA )