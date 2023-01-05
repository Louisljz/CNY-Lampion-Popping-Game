import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector
import time
import autopy
 
##########################
frameR = 100 # Frame Reduction
smoothening = 7
width, height = 1280, 720
#########################
 
pTime = 0
plocX, plocY = 0, 0
clocX, clocY = 0, 0
 
cap = cv2.VideoCapture(0)
cap.set(3, width)
cap.set(4, height)
detector = HandDetector(maxHands=1, detectionCon=0.8, minTrackCon=0.8)
wScr, hScr = autopy.screen.size()
# print(wScr, hScr)
 
while True:
    # 1. Find hand Landmarks
    success, img = cap.read()
    hands, img = detector.findHands(img)
    if hands:
        hand = hands[0]
        lmList = hand['lmList']
        bbox = hand['bbox']
        # 2. Get the tip of the index and middle fingers
        x1, y1 = lmList[8][0:2]
        x2, y2 = lmList[12][0:2]
        # print(x1, y1, x2, y2)
        
        # 3. Check which fingers are up
        fingers = detector.fingersUp(hand)
        # print(fingers)
        cv2.rectangle(img, (frameR, frameR), (width - frameR, height - frameR),
        (255, 0, 255), 2)
        # 4. Only Index Finger : Moving Mode
        if fingers[1] == 1 and fingers[2] == 0:
            # 5. Convert Coordinates
            x3 = np.interp(x1, (frameR, width - frameR), (0, wScr))
            y3 = np.interp(y1, (frameR, height - frameR), (0, hScr))
            # 6. Smoothen Values
            clocX = plocX + (x3 - plocX) / smoothening
            clocY = plocY + (y3 - plocY) / smoothening
        
            # 7. Move Mouse
            autopy.mouse.move(wScr - clocX, clocY)
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            plocX, plocY = clocX, clocY
            
        # 8. Both Index and middle fingers are up : Clicking Mode
        if fingers[1] == 1 and fingers[2] == 1:
            # 9. Find distance between fingers
            length, lineInfo, img  = detector.findDistance(lmList[8][0:2], lmList[12][0:2], img)
            # print(length)
            # 10. Click mouse if distance short
            if length < 50:
                cv2.circle(img, (int(lineInfo[4]), int(lineInfo[5])),
                15, (0, 255, 0), cv2.FILLED)
                autopy.mouse.click()
        
        # 11. Frame Rate
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3,
        (255, 0, 0), 3)
    # 12. Display
    img = cv2.flip(img, 1)
    cv2.imshow("Image", img)
    
    if cv2.waitKey(1) & 0xFF == ord(' '):
        break

cap.release()
cv2.destroyAllWindows()
