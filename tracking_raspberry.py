"""
Project Name:
    BALLTRACKER

Function of the Program:
    - (this file) recognize a ball, track the 3D position of it nad send the position over the network to a PC
	- receive the data from the client and display the ball position with Open3D 

Author:
    Jan Schuessler, FHGR

Latest Version:
    1.0 - 2021.05.26 - submitted

Version History:
    0.1 - 2020.05.06 (started with coding)
"""

from picamera import PiCamera
from picamera.array import PiRGBArray
from time import sleep, time
import cv2 as cv
import numpy as np
import socket
import pickle
import pandas as pd

with_windows = True
BlobMethod = True

# these settings has to match with the ones in the server file for the visualization
img_width = 608
img_height = 400
FOV = np.pi*33/180
RADIUS = 0.02

# Commands to start vncserver:
'''
vncserver
--> Invokes Xvnc on the next available display and with suitable defaults.
vncserver :1
--> Invokes Xvnc on display :1.
vncserver -geometry 800x600 -depth 16 :1
--> Invokes Xvnc on display :1 with desktop size of 800x600 pixels and color depth of 16 bits per pixel.
vncserver -kill :1
--> Shuts down Xvnc server on display :1.
'''
# start vnc server (on Display :1) with 800x600px: --> vncserver
# start vnc server with Full-HD display: --> vncserver :1 -geometry 1920x1080 -depth 24

# on PC, connect with tightvncserver to: raspberry-IP:display#, i.e: 192.168.43.59:1 
# Password: 123456 (change password with command: vncpasswd)

def nothing(x):
    pass

def getBlobPosition(binaryImg):
    # calculate moments of binary image
    M = cv.moments(binaryImg)

    # calculate x,y coordinate of center
    try:
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"]) 
        return(cX,cY)
    except:
        return(np.nan,np.nan)

def getPosition3D(x, y, r):
    x = -(x - img_width/2)
    y = -(y - img_height/2)                

    P = np.sqrt(x**2 + y**2)
    ball_angle = np.arctan((P + r)/f) - np.arctan((P - r)/f)
    distance = RADIUS/np.tan(ball_angle/2)
    e = [x,y,f]/np.linalg.norm([x,y,f])

    return distance*e

# Network Client Config
server_name = '192.168.43.103'
server_port = 10000

# Create a UDP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

f = img_width/(2*np.tan(FOV)) # focal length in pixels

cam = PiCamera()
res = (img_width, img_height)
cam.resolution = res
cam.framerate = 24
rawCapture = PiRGBArray(cam, size=res)
sleep(0.1)
windowColorSelect = 'Select Color'
if with_windows:
    cv.namedWindow(windowColorSelect)

kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE,(5,5)) # kernel for filtering

settings = pd.read_csv('settings.csv', sep=';')
Hue_low =   int(settings['Hue_low'][0])
Hue_high =  int(settings['Hue_high'][0])
Sat_low =   int(settings['Sat_low'][0])
Sat_high =  int(settings['Sat_high'][0])
Val_low =   int(settings['Val_low'][0])
Val_high =  int(settings['Val_high'][0])

if with_windows:
    cv.createTrackbar("Hue low", windowColorSelect, Hue_low, 179, nothing)
    cv.createTrackbar("Hue high", windowColorSelect, Hue_high, 179, nothing)
    cv.createTrackbar("Sat low", windowColorSelect, Sat_low, 255, nothing)
    cv.createTrackbar("Sat high", windowColorSelect, Sat_high, 255, nothing)
    cv.createTrackbar("Val low", windowColorSelect, Val_low, 255, nothing)
    cv.createTrackbar("Val high", windowColorSelect, Val_high, 255, nothing)


#t0 = 0
stdPos = [0,0,-0.1]
Position = stdPos
try:
    for cap in cam.capture_continuous(rawCapture, format='bgr', use_video_port=True): 
        img = cap.array
        cap.truncate(0)

        frame_hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
        if with_windows:
            filtered = cv.inRange(frame_hsv,
                (
                cv.getTrackbarPos('Hue low', windowColorSelect),
                cv.getTrackbarPos('Sat low', windowColorSelect),
                cv.getTrackbarPos('Val low', windowColorSelect)),                                    
                (
                cv.getTrackbarPos('Hue high', windowColorSelect),
                cv.getTrackbarPos('Sat high', windowColorSelect),
                cv.getTrackbarPos('Val high', windowColorSelect)))
        else:
            filtered = cv.inRange(frame_hsv,(Hue_low, Sat_low, Val_low), (Hue_high, Sat_high, Val_high))

        if with_windows:
            cv.imshow("filtered", filtered)    
        filtered = cv.erode(filtered, kernel, iterations=1)  
        filtered = cv.dilate(filtered, kernel, iterations=1)  

        if BlobMethod:
            x,y = getBlobPosition(filtered)
            area = cv.countNonZero(filtered)
            radius = np.sqrt(area/np.pi)
            if not np.isnan(x) and not np.isnan(y):
                # draw circle and center
                cv.circle(img, (int(x), int(y)), int(radius), (255, 0, 255), 2)
                cv.circle(img, (int(x), int(y)), 5, (0, 0, 255), -1)
                Position = getPosition3D(x,y,radius)
            else:
                Position = stdPos
        else:
            cnts, _ = cv.findContours(filtered, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
            if len(cnts) > 0:
                # find largest contour and circle
                c = max(cnts, key=cv.contourArea)
                ((x, y), radius) = cv.minEnclosingCircle(c)
                if radius > 3:
                    # draw circle and center
                    cv.circle(img, (int(x), int(y)), int(radius), (255, 0, 255), 2)
                    cv.circle(img, (int(x), int(y)), 5, (0, 0, 255), -1)

                    # claculate 3D position
                    Position = getPosition3D(x,y,radius)                    
                else:
                    Position = stdPos
            else:
                Position = stdPos

        # send to server
        data = pickle.dumps(Position)
        sock.sendto(data, (server_name, server_port))

        if with_windows:
            cv.imshow("orig", img)
        key = cv.waitKey(1)
        if (key == 'q' or key == 27):
            break
except KeyboardInterrupt:
    pass
finally:
    print('Closing socket')
    sock.close()
    if with_windows:
        settings['Hue_low'][0] = cv.getTrackbarPos('Hue low', windowColorSelect)
        settings['Hue_high'][0] = cv.getTrackbarPos('Hue high', windowColorSelect)
        settings['Sat_low'][0] = cv.getTrackbarPos('Sat low', windowColorSelect)
        settings['Sat_high'][0] = cv.getTrackbarPos('Sat high', windowColorSelect)
        settings['Val_low'][0] = cv.getTrackbarPos('Val low', windowColorSelect)
        settings['Val_high'][0] = cv.getTrackbarPos('Val high', windowColorSelect)

        settings.to_csv('settings.csv', index=False, sep=';')
    cv.destroyAllWindows()