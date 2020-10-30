import cv2
import numpy as np
import os

def MatchFunction(image,templatePath):
    """
    Input: image, template path

    Output: 
    """    
    template = cv2.imread(templatePath,0)
    w, h = template.shape[::-1]
    
    METHODS = ['cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR',
            'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED']

    top_left_pos = ()
    for m in METHODS:
        method = eval(m)
        #Apply
        
        res = cv2.matchTemplate(image=image,templ=template,method=method)
        min_val, max_val,min_loc, max_loc = cv2.minMaxLoc(res)

        # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
        if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
            top_left = min_loc
        else:
            top_left = max_loc

        if(top_left):
            top_left_pos = top_left
            break

    bottom_right_pos = (top_left[0] + w, top_left[1] + h)
    middle_point = top_left[0] + 0.5*w
    left_point = top_left[0]
    right_point = bottom_right_pos[0]

    h_point = top_left[1] + 0.5*h
    
    return top_left_pos, bottom_right_pos,middle_point,left_point,right_point,h_point
        
def Matcher(image,tempPath):
    """
        it can be seen template match is not a good way to do the task, it's a bit slow
    """

    # tempPath = "./template/t2.jpg"
    
    top_left, bottom_right,m,l,r, h = MatchFunction(image, tempPath)
            #print the location of sign in the whole image
            #print(h,int(video_height)*0.3,h>int(video_height)*0.25)
    return top_left,bottom_right

    
    
                


    