import sys
import numpy as np 
from PIL import Image, ImageDraw 
  
img=Image.open(sys.argv[1]) 
img.show()

h,w = img.size 
  
# creating luminous image 
lum_img = Image.new('L',[h,w] ,0)  
draw = ImageDraw.Draw(lum_img) 
draw.pieslice([(0,0),(h,w)],0,360,fill=255) 
img_arr = np.array(img) 
lum_img_arr = np.array(lum_img) 


final_img_arr = np.dstack((img_arr, lum_img_arr)) 
final = Image.fromarray(final_img_arr)
final.save('.'.join(sys.argv[1].split(".")[:-1]) + "_circularcropped.png","PNG")


