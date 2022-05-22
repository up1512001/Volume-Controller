import cv2
import mediapipe as mp
import time
import numpy as np
import HandTrackingModule as htm
import math

from ctypes import cast , POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities ,IAudioEndpointVolume



###################
wCam , hCam = 640 , 480
###################

cap = cv2.VideoCapture(0)
cap.set(1,wCam)
cap.set(2,hCam)

detector = htm.HandDectector(detectionCon=0.70)

pTime = 0


devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_,CLSCTX_ALL,None)
volume = cast (interface,POINTER(IAudioEndpointVolume))
# volume.GetMute()
# volume.GetMasterVolumeLevel()
# print(volume.GetVolumeRange())
volRange = volume.GetVolumeRange()

minVolume = volRange[0]
maxVolume = volRange[1]

volBar =400
volPer = 0
while True:
    success , img = cap.read()

    img = detector.findHands(img)
    lmList = detector.findPosition(img,draw=False)
    if len(lmList) != 0:
        # print(lmList[4],lmList[8])

        x1 , y1 = lmList[4][1] , lmList[4][2]
        x2 , y2 = lmList[8][1] , lmList[8][2]
        cx,cy = (x1+x2)//2 , (y1+y2)//2

        cv2.circle(img,(x1,y1),10,(255,0,255),cv2.FILLED)
        cv2.circle(img, (x2, y2), 10, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (cx ,cy), 10, (255, 0, 255), cv2.FILLED)
        cv2.line(img,(x1,y1),(x2,y2),(255,255,255))

        length = math.hypot(x2-x1,y2-y1)
        # print(length)

        # hand rase is 50 to 300
        #  volume range is -65 to 0
        vol = np.interp(length,[50,190],[minVolume,maxVolume])
        volBar = np.interp(length, [50, 190], [400, 150])
        volPer = np.interp(length, [50, 190], [0, 100])
        # print(int(length), vol)

        volume.SetMasterVolumeLevel(vol, None)

        if(length < 50):
            cv2.circle(img, (cx ,cy), 13, (0, 255, 0), cv2.FILLED)

        if (length > 180):
            cv2.circle(img, (cx, cy), 13, (0,0, 250), cv2.FILLED)

    cv2.rectangle(img , (50,150),(85,400),(255,0,0),3)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (255,0,0), cv2.FILLED)
    cv2.putText(img,f'{int(volPer)} %',(40,450),cv2.FONT_HERSHEY_PLAIN,2,(255,0,0),3)


    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime

    cv2.putText(img, f'FPS : {int(fps)} %', (40, 30), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 3)

    cv2.imshow("Image :",img)
    cv2.waitKey(1)