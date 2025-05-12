#!/usr/bin/env python
# coding: utf-8

# In[35]:

import sys
import cv2
import numpy as np
import time
import pylab as pl

inputfile = sys.argv[1]
smoothness = 3

if len(sys.argv)>2:
    smoothness = int(sys.argv[2])

img = cv2.imread(inputfile)
pl.imshow(img, cmap="bone")
pl.show()


gray = cv2.cvtColor(img, cv2.COLOR_RGBA2GRAY)

#pl.imshow(gray, cmap="bone")



edges = cv2.adaptiveThreshold(gray, 255, 
                cv2.ADAPTIVE_THRESH_MEAN_C, 
                cv2.THRESH_BINARY, 9, 9)
pl.imshow(edges, cmap="bone")
pl.show()

edges2 = cv2.adaptiveThreshold(gray, 255, 
                               cv2.ADAPTIVE_THRESH_MEAN_C, 
                               cv2.THRESH_BINARY, smoothness, smoothness)
pl.imshow(edges2, cmap="bone")
pl.show()


    # 2) Color
color = cv2.bilateralFilter(gray, 15, 50, 50)

#gamma = 0.3
def adjust_gamma(image, gamma=1.0):
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255
        for i in np.arange(0, 256)]).astype("uint8")
    return cv2.LUT(image, table)
adjusted = adjust_gamma(color, gamma=1)

#pl.imshow(adjusted, cmap="bone")



# 3) Cartoon
cartoon = cv2.bitwise_and(adjusted, adjusted, mask=edges2)
pl.imshow(cartoon, cmap="gray")
pl.show()

cartoon = cv2.bitwise_and(cartoon, cartoon, mask=edges)
pl.imshow(cartoon, cmap="gray")
pl.show()

cartoon = cv2.bitwise_and(cartoon, adjusted, mask=edges2)
pl.imshow(cartoon, cmap="gray")
pl.show()


pl.imshow(cartoon, cmap="gray")



#pl.imshow(cartoon, cmap="bone")


outname = sys.argv[1].replace("images/",
                              "../subgroups/images/").replace('.png',
                                            '_avatar.png').replace('.jpg',
                                            '_avatar.png').replace('.jpeg',
                                            '_avatar.png')
cv2.imwrite(outname, cartoon) 
print(outname)
