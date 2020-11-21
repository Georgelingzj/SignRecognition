# <font size = 6>Image Processing In Street Sign Recognition</font>



---

# <font size = 6>Workflow</font>

- <font size = 6>Part1: main task</font>
  
- <font size = 6>Part2: Ideas for solving the task</font>

- <font size = 6>Part3: Code explanation</font>  



---

# <font size = 6>Part1: Main task</font>

- <font size = 5>There are three kinds of street sign along both sides of the road</font>
- <font size = 5>Catch video/real time frame</font>  
- <font size = 5>Focus on target area</font>  
- <font size = 5>Recognize the street sign using opencv(mainly about template match)</font>

- ![](https://raw.githubusercontent.com/Georgelingzj/SignRecognition/main/presentation/images/sign2.jpg)



---

# <font size = 6>Part2: Ideas for solving the task</font>

- <font size = 5>Using **"sliding window"** to get smaller part of the images -- street signs are all along the middle horizontal line</font>
- <font size = 5>Change **Colour image** to **Binary(gray) image**</font>
- <font size = 5>Using method in opencv to find the **rectangular target area**</font>
- <font size = 5>Using method in opencv to find x-like character and the special character inside the rectangular targer area</font>
- <font size = 5>Based on coordinates of characters to decide the type of Street sign</font>

---

# <font size = 6>Part3: Code explanation</font>
- <font size = 6>How to get a screenshot</font>
- <font size = 6>How to get a smaller target area</font>
- <font size = 6>How to change it to gray image and apply threshold</font>
- <font size = 6>How to find rectangular street sign in the target area</font>
- <font size = 6>How to match character in target area with templates</font>
- <font size = 6>How to decide which street sign it is</font>

---
# <font size = 6>Part3.1: How to get a screenshot</font>

## Traditional way -- usually has 50ms delay

    !python
    from PIL import ImageGrab
    import numpy as np 
    import cv2

    img = ImageGrab.grab(bbox=(x1,y1,x2,y2))
    img_np = np.array(img)
    cv2.imshow('img',img_np)
    if 0xFF & cv2.waitKey(0) == 27:  
        cv2.destroyAllWindows()

## My way (only for windows since the simulator runs on windows)
    !python
    import mss
    from PIL import Image
    import numpy as np

    sct = mss.mss()
    monitor = {'top': 0, 'left': 0, 'width': 1920, 'height': 1080}
    img = sct.grab(monitor)

    frame = Image.frombytes("RGB", img.size, img.bgra, "raw", "BGRX")        
    frame = np.array(frame)
    frame = cv2.cvtColor(frame,cv2.COLOR_RGB2BGR)


---
# <font size = 6>Part3.2: How to get a smaller target area</font>

    !python
    def slideWindow(image, width, height, window_width, window_height, step)

- We can use "sliding window" along the middle horizontal line to get fixed size smaller image


- ![](https://raw.githubusercontent.com/Georgelingzj/SignRecognition/main/presentation/images/32.jpg)

- Parameter "step" means per moving length of the left edge towards right direction

--- 
# <font size = 6>Part3.2: How to get a smaller target area</font>

- ![](https://raw.githubusercontent.com/Georgelingzj/SignRecognition/main/presentation/images/32_2.jpg)
- There are 3 windows plotted in the image above, the successive one move "step length" from the former left edge


---
# <font size = 6>Part3.2: How to get a smaller target area</font>

    !python
    #the middle row of the input image
    middleRow = int(height/2)
    #starting x and y coordinate, 600 -> to find the target faster
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
    

- Get the start point
- Initialize the pred(predicted level) to "o" other
- Using while loop move the "window" from left to right
- - if find label then break the loop 

---
# <font size = 6>Part3.3: How to make it gray image and apply threshold</font>

![](https://raw.githubusercontent.com/Georgelingzj/SignRecognition/main/presentation/images/33_1.jpg)
- cv2.cvtColor(imagename,COLOR_BGR2GRAY)-- we change the channel of the image
![](https://raw.githubusercontent.com/Georgelingzj/SignRecognition/main/presentation/images/33_2.jpg)
- cv2.threshold(imagename, thresh, 255, cv2.THRESH_BINARY)-- we choose thresh = 200 to reduce obvious noise

---
# <font size = 6>Part3.4: How to find rectangular sign in target area</font>

- ![](https://raw.githubusercontent.com/Georgelingzj/SignRecognition/main/presentation/images/33_3.jpg)
- compared to last images we got, we now are more focus on stree sign. There are less black contents around target area
- The size of current image used to be around 70*40

---
# <font size = 6>Part3.4: How to find rectangular sign in target area</font>

    !python
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

- detect the contour of object on the image
- limit the area of contour to find the most likely target area

---
# <font size = 6>Part3.5: Match character in target area with templates</font>

- template1
- ![](https://raw.githubusercontent.com/Georgelingzj/SignRecognition/main/presentation/images/35_1.jpg)
- template2
- ![](https://raw.githubusercontent.com/Georgelingzj/SignRecognition/main/presentation/images/35_2.jpg)


---
# <font size = 6>Part3.5: Match character in target area with templates</font>

    !python
    METHODS = ['cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR',
            'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED']

    top_left_pos = ()
    for m in METHODS:
        method = eval(m)
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

- there are 6 built-in methods in opencv
- when one of them match successfully, we stop the loop and return the coordinates of top-left and bottom-right point of the character in target area

--- 
# <font size=6>Part3.6: How to decide which street sign it is</font>

    !python 
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

- simply use the relationship between the coordinates(match results)

- <font size=6 color=red>you can find better ideas!</font>

----

- Performance:
    - accuracy: more than **92%** in video mode
    - latency: around **400-6000** microseconds in video mode

- Whole code is in [https://github.com/Georgelingzj/SignRecognition](https://github.com/Georgelingzj/SignRecognition)

- If you have further question, feel free to send me an email at [georgeling.0330@gmail.com](georgeling.0330@gmail.com)

---
# Thanks for listening
    

            


