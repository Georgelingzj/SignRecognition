import cv2

def imagePre(image):
    thresh = 200
    
    image1 = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    img_binary = cv2.threshold(image1, thresh, 255, cv2.THRESH_BINARY)[1]

    return img_binary