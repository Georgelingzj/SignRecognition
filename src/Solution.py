import cv2
import os
import matplotlib.pyplot as plt
from window import slideWindow
from preimage import imagePre
import datetime
starttime = datetime.datetime.now()
path = "./images/1.jpg"
img = cv2.imread(path)
img = imagePre(image=img)

width,height = img.shape[1],img.shape[0]

slideWindow(image=img,width=width,height=height,window_width=256,window_height=256,step = 50)

endtime = datetime.datetime.now()
print (endtime - starttime)

plt.imshow(img)
plt.show()
