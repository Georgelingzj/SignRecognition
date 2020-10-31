import numpy as np
import cv2
import os
import datetime
import matplotlib.pyplot as plt
from templateMatch import Matcher

#show the whole numpy array in the terminal
np.set_printoptions(threshold=np.inf)

folderPath = "./imageProcessed/"

def Solution(image):
    """
    input: same size (256*256) rgb image

    output: the label of the image
        "l" -> left
        "m" -> middle
        "r" -> right
        "o" -> other(NO target)

        if no target detected, return "o", which is the initial value
    """
    #initial two point for locatate the target area
    topLeft = [0,0]
    bottomRight = [0,0]
    pred_label = "o" #initial the recognition label

    #make image to gray 
    thresh = 200
    image = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    image = cv2.threshold(image, thresh, 255, cv2.THRESH_BINARY)[1]

    #find contours in grey image
    C,h= cv2.findContours(image, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    if len(C) > 0:
        for i in range(len(C)):
            c = C[i]
            area = cv2.contourArea(c)
            rect = cv2.minAreaRect(c)
            box = cv2.boxPoints(rect)
            # convert all coordinates floating point values to int
            box = np.int0(box)

            #limit the area we interested
            if area>500:
                topLeft = [box[1][0],box[1][1]]
                bottomRight = [box[3][0],box[3][1]]
                #cut the traffic sign with slight remnants around
                cut = image[topLeft[1]:bottomRight[1],topLeft[0]:bottomRight[0]]
                Ishape = cut.shape
                #limit the area we interested again
                if Ishape[0] <30 or Ishape[1] < 40:
                    continue
                else:
                    #use two different template to match
                    #each return two position with is the topleft and the bottomright of the processed image
                    #t1.jpg is the x-like character
                    topleft_1,bottomright_1 = Matcher(cut,"./template/t2.jpg")
                    topleft_2,bottomright_2= Matcher(cut,"./template/t1.jpg")
                    #if not none
                    if topleft_1 and topleft_2 and bottomright_1 and bottomright_2:
                        pred_label = helper(topleft_1,bottomright_1,topleft_2,bottomright_2,Ishape=Ishape)

    return pred_label


def slideWindow(image,width,height,window_width,window_height,step):

    """
    Reason for this method:
        1. if I use certain methods on the whole image, the lantency is much high
        2. Through observation, it is found that street signs appear on the horizontal axis of the image(No uphill)
        I imitated Yolo and designed a sliding window to cut pictures along the middle row
        
    input: [image, image width, image height
            ,window width,window height, per step move length]

    
    the original setting is:
    [image,1920,1080,256,256,100]
    if the input image size changed, plz adjust the window shape and step length to get better performance

    output: image for network
    """
    #the middle row of the input image
    middleRow = int(height/2)
    #starting x and y coordinate, 600 -> to find the target as fast as possible
    startPoint = [600,middleRow]
    pred = "o"
    while startPoint[0] + window_width <= width:
        h1 = int(middleRow-(window_height/2))
        h2 = int(middleRow+(window_height/2))
        w1 = int(startPoint[0])
        w2 = int(startPoint[0]+window_width)
        cut = image[h1:h2,w1:w2]

        startPoint[0] += step
        pred = Solution(cut)
        #as soon as finding label, break.
        if pred != "o":
            break
    return pred


def helper(target_topL,target_bottR,xlike_topL,xlike_bottR,Ishape):
    """
        (x,y) / (width, height)

        input: the topleft and bottom right coordinate for special character and x-like character respectively
                the shape of input image

        ! For convenience, we call the specical character -> target

        output:  label
    """
    #calculate the center point of target and xlike character
    target_m = (target_bottR[0]+target_topL[0])/2
    xlike_m = (xlike_topL[0] + xlike_bottR[0])/2
    

    #if the center point of target appear in the right most 1/3 part
    if(target_m>0.67*Ishape[1]):
        #left condition1
        pred_label = "r"
    # xlike is in the right of target,the detected xlike is next to the target, the last one distinguish it with label "m"
    elif (xlike_m<target_m) and (abs(xlike_bottR[0]-target_topL[0])<3) and (target_m > 0.60*Ishape[1] and xlike_m<0.60*Ishape[1]):
        #left condition2
        pred_label = "r"
    # xlike is in the left of the target, the detected xlike is next to the target, target is in the left most 1/3 region.
    elif(xlike_m > target_m) and (abs(xlike_topL[0]-target_bottR[0])<5) and (target_m < 0.33*Ishape[1] and xlike_m>0.33*Ishape[1]):
        pred_label = "l"
    #distinguish it with second condition
    elif (xlike_m<target_m) and (abs(xlike_bottR[0]-target_topL[0])<5):
        #middle condition1: xlike is in the left of target
        pred_label = "m"
    elif (xlike_m>target_m) and (abs(xlike_topL[0]-target_bottR[0])<5):
        #middle condition1: xlike is in the right of target
        pred_label = "m"
    else:
        pred_label = "l"
        
    return pred_label


def Processor(videoPath, is_record = False,output_suffix = ".mp4"):

    assert os.path.exists(videoPath), "No target file in video folder"
    
    s = videoPath.split('/')
    foldername = s[1]
    filename = s[2].split('.')[0]

    outPath = "./" + foldername + '/' + filename + "_processed.mp4"
    capture = cv2.VideoCapture(videoPath)
    fps = int(round(capture.get(cv2.CAP_PROP_FPS)))
    video_width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

    if output_suffix == ".mp4":
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    else:
        # if the suffix of output video is ".avi" use below
        fourcc = cv2.VideoWriter_fourcc(*'XVID')

    if is_record == True:
        myVideoWriter = cv2.VideoWriter(outPath,fourcc,fps,(video_width, video_height))

    pred1_last = "o"
    #last pred label
    predPresent = ""
    starttime_ = datetime.datetime.now()
    while(capture.isOpened()):
        ret,frame = capture.read()
        if(ret == True):
            width,height = frame.shape[1],frame.shape[0]
            pred = slideWindow(image=frame,width=width,height=height,window_width=256,window_height=256,step = 100)

            """
            small trick:
                in the test I found, apart from the prediction of the first frame,
                the prediction of the other following might be incorrect

                when the frame appear the street sign from no target
                set a variabel to remember the 'first frame''s prediction and record the time
                in the time period of 2s from the 'first frame''s prediction, all the other prediction of 
                incoming frame will be ignored

                1.more then 2s from 'first frame''s prediction or 2. the frame of input video has no street sign
                to reset the 'predPresent'

            """
            if pred != "o" and pred1_last == "o":
                predPresent = pred
                pred1_last = pred
                starttime_ = datetime.datetime.now()
            elif pred ==  "o" and pred1_last != "o":
                endtime = datetime.datetime.now()
                if (endtime-starttime_).seconds > 2:
                    pred1_last = pred
                    predPresent = "o"

            if predPresent == "l":
                frame = cv2.putText(frame, 'Left', (int(video_width/2), 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0,255), 2)
            elif predPresent == "m":
                frame = cv2.putText(frame, 'middle', (int(video_width/2), 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0,255), 2)
            elif predPresent == "r":
                frame = cv2.putText(frame, 'right', (int(video_width/2), 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0,255), 2)

            cv2.imshow("Capture", frame)
            if is_record == True:
                myVideoWriter.write(frame)
        if(ret == False):
            break
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    capture.release()
    if is_record == True:
        myVideoWriter.release()
    cv2.destroyAllWindows()
