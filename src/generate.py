from pickletools import uint8
import cv2
import numpy as np
import math
#author: Shayan Hemmatiyan
# import keras_ocr

# pipeline =keras_ocr.pipeline.Pipeline()


class Generate:
    def __init__(self, img, image_path, download_f, bb, txt, bg, font_scale):
        # bb [LT, BR]
        self.img = img
        self.image_path=image_path
        self.download_f = download_f
        self.bb = bb
        self.txt = txt
        self.bg = bg
        self.font_scale = font_scale

    def fileType(self, fileName):
        fileName = fileName.replace("\\", "/")
        return (str(fileName.split("/")[-1]).split(".")[-1]).lower()

    def fileName(self, filePath):
        filePath = filePath.replace("\\", "/")
        return str(filePath.split("/")[-1]).split(".")[0]
    
    def midpoint(self, x1,x2,y1,y2):
        return (int((x1+x2)/2), int((y1+y2)/2))

    def gen(self):
        new_img_ = self.img.copy()
        font = cv2.FONT_HERSHEY_DUPLEX
        scale=0.5
        color = (0,0,0)
        start = self.midpoint(self.bb[0][0], self.bb[0][0], self.bb[0][1], self.bb[1][1])
        end = self.midpoint(self.bb[1][0], self.bb[1][0] , self.bb[0][1], self.bb[1][1])
        
        tickness_y = min(max(0,abs(self.bb[1][1]-self.bb[0][1])), int(new_img_.shape[1]))
        tickness_x =  min(max(0,abs(self.bb[1][0]-self.bb[0][0])), int(new_img_.shape[0]))
        start_txt = (self.bb[0][0]+5,start[1]+10)
        if self.bg !="w":
            mask =np.zeros(new_img_.shape[:2], dtype= "uint8")
    
            cv2.line(mask, (int(start[0])+20, int(start[1])), (int(end[0]), int(end[1])),255, int(tickness_y))
        
            img_generated = cv2.inpaint(new_img_, mask,5, cv2.INPAINT_NS)
        else:
            img_generated = new_img_.copy()
            tlx,tly=self.bb[0][0], self.bb[0][1]
            brx,bry=self.bb[1][0], self.bb[1][1]
            mask  =255*np.ones([abs(int(tly)-int(bry)+4),
             abs((int(tlx))- int(brx)+4),3],
             dtype=np.uint8 )
       
            img_generated[ int(tly)+2:int(bry)-2, (int(tlx))+2: int(brx)-2, :]=mask
                     
            # cv2.imshow("fig", img_generated)
            # cv2.waitKey(0)
        if self.font_scale =="scaled":
            
            fontScale = tickness_y/(25/scale)
            img_generated=cv2.putText(img_generated, self.txt,start_txt,\
                font,fontScale ,color, 1, cv2.LINE_AA)

        elif self.font_scale =="l":
            start_txt = (self.bb[0][0]+5, self.bb[0][1]+35)
            img_generated=cv2.putText(img_generated, self.txt,start_txt,\
                font,1 ,color, 1, cv2.LINE_AA)
        elif self.font_scale =="m":
            start_txt = (self.bb[0][0]+5, self.bb[0][1]+30)
            img_generated=cv2.putText(img_generated, self.txt,start_txt,\
                font,0.8 ,color, 1, cv2.LINE_AA)
        elif self.font_scale =="s":
            start_txt = (self.bb[0][0]+5, self.bb[0][1]+25)
            img_generated=cv2.putText(img_generated, self.txt,start_txt,\
                font,0.6 ,color, 1, cv2.LINE_AA)
        print("file", str(self.download_f)+"/gen_"+str(self.fileName(self.image_path) +".png"))
        return img_generated