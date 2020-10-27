import cv2
import numpy as np
import matplotlib.pyplot as plt

def slideWindow(image,width,height,window_width,window_height,step):

    """
    input: [image, image width, image height
            ,window width,window height, per step move length]

    output: image for network
    """
    
    i = 0
    Wpath = "./subImage/"
    middleRow = int(height/2)
    #横坐标，总坐标
    startPoint = [0,middleRow]
    while startPoint[0] + window_width <= width:
    #纵向距离，横向距离
        h1 = int(middleRow-(window_height/2))
        h2 = int(middleRow+(window_height/2))
        w1 = int(startPoint[0])
        w2 = int(startPoint[0]+window_width)
        cut = image[h1:h2,w1:w2]
        startPoint[0] += step
        path = Wpath + str(i) + ".jpg"
        i += 1
        cv2.imwrite(path,cut)
    
    
    
    



    