'''
# Team ID:          < eYRC#LD#3449 >
# Theme:            < Luminosity Drone (LD) >
# Author List:      < Keyoor Deorukhkar, Raj Parab, Hiral Mehta, Kalpit Prabhu >
# Filename:         < LD_3449_led_detection.py >
# Functions:        < cv.imread(), np.zeros(), cv.cvtColor(), cv.GaussianBlur,() cv.threshold(), cv.dilate(), cv.erode,() cv.bitwise_and(), cv.findContours(), cv.moments(), cv.putText,() cv.drawContours(), cv.contourArea(), cv.imwrite(), file.write(), file.close(), cv.waitKey()>
# Global variables: < cnt, a, cX, cY, area, i >
'''


import cv2 as cv
import numpy as np

led = cv.imread('/home/keyoor/catkin_ws/src/luminosity_drone/luminosity_drone/scripts/led.jpg')
#cv.imshow('question',led)

blank = np.zeros(led.shape, dtype='uint8')

#gray and blur
gray = cv.cvtColor(led, cv.COLOR_BGR2GRAY,)
# cv.imshow('grey',gray)

blur = cv.GaussianBlur(gray,(7,7),cv.BORDER_DEFAULT)
# cv.imshow('blurr',blur)

#thresh
threshold, thresh = cv.threshold(blur,150,255,0)
# cv.imshow('threshold',thresh)

#erro dia

dialted = cv.dilate(thresh,(7,7),iterations=7)
# cv.imshow('dialted',dialted)

erroded = cv.erode(dialted,(7,7),iterations=7)
# cv.imshow('errrode',erroded)

#make mask

maskedimg = cv.bitwise_and(led,led,mask= thresh)
# cv.imshow('maskedimg',maskedimg)


#find conntours

contours , hierachy = cv.findContours(thresh,cv.RETR_TREE,cv.CHAIN_APPROX_SIMPLE)
# print('no of contour' + str(len(contours)))

cnt = contours[0]
a = 1
area = []
cor_x = []
cor_y = []
for c in contours:
   # calculate moments for each contour
   M = cv.moments(c)
 
   # calculate x,y coordinate of center
   cX = float(M["m10"] / M["m00"])
   cY = float(M["m01"] / M["m00"])
#  cv.circle(led, (cX, cY), 5, (0, 0, 255), -1)
   cv.putText(led, '#' + str(a), (int(cX) - 25, int(cY) - 25),cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
   # print('x coordinate' + str(cX) , 'y coordinate '+ str(cY))
   cv.drawContours(led,contours,-1,(0,0,255),thickness=2)
   area = cv.contourArea(cnt)
   # print('Area:', area)

#  cv.imshow('contoursdrawn',blank)
   #display the image
   #cv.imshow("Image",led)
   cor_x.append(cX)
   cor_y.append(cY)
   a = a+1


cv.waitKey(0)
i = 0
a =a-1
cv.imwrite("LD_3449_led_detection_results.png", led)
# print("savedddd!!!")
# print(cor_x)

with open("LD_3449_led_detection_results.txt", "w") as file:
    # Write the number of LEDs detected to the file
    file.write(f"No. of LEDs detected: {a}\n")
    for c in contours:
      centroid = (cor_x[i],cor_y[i])
      file.write(f"Centroid #{i + 1}: {centroid}\nArea #{i + 1}: {area}\n")
      i = i+1
# Close the text file
file.close()
