import pytesseract, cv2, time, sys
from pytesseract import Output
from statistics import mode
from image_similarity_measures.quality_metrics import sam, uiq
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
    # if img_char.shape[1]-n_letter.shape[1]<0-img_char.shape[1]*0.2:
    #     return {"same_rate":0}
    temp = np.zeros((max(img_char.shape[0],n_letter.shape[0]+offset[0]),max(img_char.shape[1],n_letter.shape[1]+offset[1])))
    img_char = (255-img_char)//150
    n_letter = n_letter//150

    # for y in range(img_char.shape[0]):
    #     for x in range(img_char.shape[1]):
    #         if img_char[y,x,0]>0:
    #             temp[y,x]+=1
    temp[:img_char.shape[0],:img_char.shape[1]] = img_char[:,:,0]
    temp[offset[0]:offset[0]+n_letter.shape[0],offset[1]:offset[1]+n_letter.shape[1]] = temp[offset[0]:offset[0]+n_letter.shape[0],offset[1]:offset[1]+n_letter.shape[1]] + n_letter[:,:,0] + n_letter[:,:,0]

    # print(n_letter.shape)
    # for y in range(n_letter.shape[0]):
    #     for x in range(n_letter.shape[1]):
    #         if n_letter[y,x,0]>0:
    #             temp[y+offset[0],x+offset[1]]+=2

    let = np.count_nonzero( temp == 1 )
    im = np.count_nonzero( temp == 2 )
    same = np.count_nonzero( temp == 3 )
    root = np.count_nonzero( img_char==1 )

    # n_letter = n_letter*255
    # cv2.imshow('le', n_letter)
    # img_char = img_char*255
    # cv2.imshow('img', img_char)
    # cv2.imshow('tem', temp-100)
    # print(let, im, same, root)
    # cv2.waitKey(0)
    return {"same_rate":(same-(let+im)*0.5)/(same+im),"letter":let,"image":im,"same":same,"dot":dot,"offset":offset}

def diff_char_relative(img_char,n_letter,dot,offset=(0,0)):
    img_char = (255-img_char)//150
    n_letter = n_letter//150
    img_char_temp = np.zeros( (max(img_char.shape[0],n_letter.shape[0]+offset[0])+10 , max(img_char.shape[1],n_letter.shape[1]+offset[1])+10) )
    n_letter_temp = np.zeros( (max(img_char.shape[0],n_letter.shape[0]+offset[0])+10 , max(img_char.shape[1],n_letter.shape[1]+offset[1])+10) )

    for y in range(img_char.shape[0]):
        for x in range(img_char.shape[1]):
            if img_char[y,x,0]>0:
                img_char_temp[y,x]=255

    for y in range(n_letter.shape[0]):
        for x in range(n_letter.shape[1]):
            if n_letter[y,x,0]>0:
                n_letter_temp[y+offset[0],x+offset[1]]=255
    diff = uiq(img_char_temp, n_letter_temp)

    # cv2.imshow('tem', n_letter_temp)
    # cv2.waitKey(0)

    return {"diff_rate":diff,"dot":dot,"offset":offset}




###############################################################################################################

img = cv2.imread('test.png')

char = pytesseract.image_to_boxes(img, output_type=Output.DICT)
print(char)

# d = pytesseract.image_to_data(img, output_type=Output.DICT)
# print(d)
# v_boxes = len(d['level'])
# for i in range(v_boxes):
#     (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
#     cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
# wq = img.shape[1]
# hq = img.shape[0]
# size = 0.5
# dim = ( int(wq*size), int(hq*size) )
# img = cv2.resize(img, dim,interpolation = cv2.INTER_AREA )
# cv2.imshow('img', img)
# cv2.waitKey(0)


# ##### Remove duplicate boxs.
# print(len(char["right"]))
# i = 1
# while i < len(char["right"]):
#     if (char["right"][i-1] > char["left"][i]) and abs(char["top"][i-1]-char["top"][i])>abs(char["top"][i-1]-char["bottom"][i-1]):
#         char["right"].remove(char["right"][i])
#         char["left"].remove(char["left"][i])
#         char["top"].remove(char["top"][i])
#         char["bottom"].remove(char["bottom"][i])
#     else:
#         i+=1
# print(len(char["right"]))


### Get moderate height of text
char_h=[]
for i in range(len(char["right"])):
    char_h+=[char["top"][i]-char["bottom"][i]]
average=sum(char_h)/len(char_h)
char_h = [t for t in char_h if t<=average]
print("Characters height: ",mode(char_h))
size = mode(char_h)/62

############### BEGIN
print("ocr...")

def OCR(a1,a2,a3,a4,b, rangee = range(len(char["left"])) ):
    global char, img, characters, size, step
    ocr = []
    for i_char in rangee:
        h = img.shape[0]
        (x,y,x1,y1) = (char['left'][i_char], img.shape[0] - char['top'][i_char], char['right'][i_char], img.shape[0] - char['bottom'][i_char])
        detect_char = img[y:y1,x:x1,:]
        res = []
        for letter in characters:
            # if letter["char"]!="T":continue
            n_letter = letter["img"]
            ### Resize img 
            # dim = ( int( letter["width"]*(y1-y)/letter["height"] ), y1-y )
            dim = ( int(letter["width"]*size), int(letter["height"]*size) )
            n_letter = cv2.resize(n_letter, dim,interpolation = cv2.INTER_AREA )
            # if letter["char"] =="T": 
            times_x = ( n_letter.shape[1]-detect_char.shape[1] ) // step +1
            times_y = ( n_letter.shape[0]-detect_char.shape[0] ) // step +1
            for ofs_y in range ( times_y ):
                for ofs_x in range ( times_x ):
                    diff = diff_char(detect_char, n_letter,letter["dot"], offset = (ofs_y*step,ofs_x*step))
                    # print(diff,[letter["char"]])
                    diff["same_rate"] = (a1*diff["same"] + a2*diff["letter"] + a3*diff["image"] + a4*diff["dot"]) /(diff["same"]+diff["letter"]+1)

                    diff["char"] = letter["char"]
                    res+=[ diff ]
                    # print(diff)

                    # if diff["same_rate"]>0.1:
                    #     diff["char"] = letter["char"]
                    #     res+=[ diff ]
        # print(" ...")

        # mode_same_rate = [ a["same_rate"] for a in res ]
        # try:
        #     mode_same_rate = sum(mode_same_rate)/len(mode_same_rate)
        #     pre_res = [r for r in res if r["same_rate"]>=mode_same_rate ]

        #     result = max(res, key = lambda x:0-(x["image"]))
        #     ocr+=[result]
        # except:
        #     result = {"same_rate":0,"char":"?"}
        try:
            # pre_res = [t for t in res if t["same_rate"]>=0]
            # pre_res = [t for t in res if t["letter"]<(t["same"]+t["letter"])*0.5]
            result = max(res, key = lambda x:x["same_rate"])
        except:
            result = {"same_rate":"0", "char":"?"}

        ocr+=[result]

    return ocr

total_result = []
dapan = "TôilàAiGiữacuộcđờiNày"
# for a1 in range(1,10):
#     for a2 in range(-5,0):
#         for a3 in range(-5,0):
#             for a4 in [0]:
#                 for b in [1]:
#                     if b==0:
#                         continue
#                     right = 0
#                     resultt = OCR(a1,a2,a3,a4,b)
#                     for t in range(len(dapan)):
#                         try:
#                             if dapan[t] == resultt[t]["char"]:
#                                 right+=1
#                         except:
#                             pass
#                     stri = [t["char"] for t in resultt]
#                     total_result+=[{"right":right,"number":f"{a1} {a2} {a3} {a4} {b}","string":stri}]
#                     print(f"{a1} {a2} {a3} {a4} {b}", resultt)
#                     print(right)
#                     f=open("res.txt","w",encoding="utf8")
#                     f.write(str(total_result))
#                     f.close()

# print(total_result)


# print(OCR(1, -1, -2, 0, 1, rangee = [3] ))
for t in OCR(1, -1, -2, 0, 1 ):
    print(t)

# print(ord("Ữ"))
