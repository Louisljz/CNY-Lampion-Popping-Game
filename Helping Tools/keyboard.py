import cv2
from cvzone.HandTrackingModule import HandDetector
import cvzone
from pynput.keyboard import Controller, Key
 
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)
 
detector = HandDetector(maxHands=1, detectionCon=0.8, minTrackCon=0.8)
keyboard = Controller()

keys = [["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
        ["A", "S", "D", "F", "G", "H", "J", "K", "L"], 
        ["Z", "X", "C", "V", "B", "N", "M"]] 
clicked = False 
finalText = '' 

def checkTextSize(button):
    if button.text == 'Backspace':
        textSize = 3
    else:
        textSize = 4
    return textSize

def drawAll(img, buttonList):
    for button in buttonList:
        x, y = button.pos
        w, h = button.size
        cvzone.cornerRect(img, (button.pos[0], button.pos[1], button.size[0], button.size[1]),
                          20, rt=0)
        cv2.rectangle(img, button.pos, (x + w, y + h), (255, 0, 255), cv2.FILLED)
        cv2.putText(img, button.text, (x + 20, y + 65),
                    cv2.FONT_HERSHEY_PLAIN, checkTextSize(button), (255, 255, 255), 4)

    x, y, w, h = 950, 150, 85, 85
    cvzone.cornerRect(img, (x, y, w, h), 20, rt=0)
    cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 255), cv2.FILLED)

    return img
 
class Button():
    def __init__(self, pos, text, size=(85, 85)):
        self.pos = pos
        self.size = size
        self.text = text
 
buttonList = []
for i in range(len(keys)):
    for j, key in enumerate(keys[i]):
        buttonList.append(Button((100 * j + 50, 100 * i + 50), key))

x, y, w, h = 750, 250, 290, 85
buttonList.append(Button((x,y), 'Backspace', (w,h)))

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    hands, img = detector.findHands(img, flipType=False)

    if hands:
        hand = hands[0]
        lmList = hand['lmList']
        bboxInfo = hand['bbox']
        img = drawAll(img, buttonList)
 
        for button in buttonList:
            x, y = button.pos
            w, h = button.size
 
            if x < lmList[8][0] < x + w and y < lmList[8][1] < y + h:
                cv2.rectangle(img, (x - 5, y - 5), (x + w + 5, y + h + 5), (175, 0, 175), cv2.FILLED)
                cv2.putText(img, button.text, (x + 20, y + 65),
                            cv2.FONT_HERSHEY_PLAIN, checkTextSize(button), (255, 255, 255), 4)
                length, info, img = detector.findDistance(lmList[8][0:2], lmList[12][0:2], img)
                
                if length > 50 and clicked == True:
                    clicked = False

                if length < 50 and clicked == False:
                    clicked = True
                    if button.text == 'Backspace':
                        keyboard.press(Key.backspace)
                        finalText = finalText[:-1]
                    else:
                        keyboard.press(button.text)
                        finalText += button.text
                          
    cv2.rectangle(img, (50, 350), (700, 450), (175, 0, 175), cv2.FILLED)
    cv2.putText(img, finalText, (60, 430),
                cv2.FONT_HERSHEY_PLAIN, 5, (255, 255, 255), 5)
    
    cv2.imshow("Keyboard", img)
        
    if cv2.waitKey(1) & 0xFF == ord(' '):
        break

cap.release()
cv2.destroyAllWindows()
