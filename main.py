import cv2
import gtts
from cvzone.HandTrackingModule import HandDetector
from time import sleep
import numpy as np
import cvzone
from pynput.keyboard import Key, Controller
import pygame
from playsound import playsound
from gtts import gTTS
import pyttsx3
import os

cap = cv2.VideoCapture(0)  # vidoecapture object with webcam id=0
cap.set(3, 1280)  # we need to increase size ab keyboard is big and 3-->width
cap.set(4, 720)  # 4-->height

detector = HandDetector(detectionCon=0.8)  # hand detector
keys = [["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "<-"],
        ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
        ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"],
        ["_"]]

finalText = ""
engine = pyttsx3.init()
keyboard = Controller()


# def drawAll(img, buttonList):

#  for button in buttonList:
#    x, y = button.pos
#    w, h = button.size
#   cv2.rectangle(img, button.pos, (x + w, y + h), (9, 254, 40), cv2.FILLED)
#   cv2.putText(img, button.text, (x + 20, y + 65), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
#  return img`

def drawAll(img, buttonList):
    imgNew = np.zeros_like(img, np.uint8)
    for button in buttonList:
        x, y = button.pos
        cvzone.cornerRect(imgNew, (button.pos[0], button.pos[1], button.size[0], button.size[1]), 20, rt=0)
        cv2.rectangle(imgNew, button.pos, (x + button.size[0], y + button.size[1]), (9, 254, 40), cv2.FILLED)
        cv2.putText(imgNew, button.text, (x + 40, y + 60), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 3)

    out = img.copy()
    aplha = 0.5
    mask = imgNew.astype(bool)
    print(mask.shape)
    out[mask] = cv2.addWeighted(img, aplha, imgNew, 1 - aplha, 0)[mask]

    return out


# for replicating all buttons we are making use of class

class Button():
    def __init__(self, pos, text, size=[80, 80]):
        # size will be common and but position will not
        # the self.pos,size and text will run only one time before the loop
        self.pos = pos
        self.size = size
        self.text = text

    # def draw(self, img): #because webcam will have diff images every iteration so we need to draw every iteration

    # return img


buttonList = []
for i in range(len(keys)):
    for j, key in enumerate(keys[i]):
        buttonList.append(Button([100 * j + 50, 100 * i + 50], key))  # making object of Button class

while True:
    success, img = cap.read()  # new image coming from webcam
    img = detector.findHands(img)  # to find hands
    lmList, bboxInfo = detector.findPosition(img)  # find landmarks points from hands
    # we actually need buttons to find locations and to know press and what key is pressed
    # now there are two ways in which
    # 1st we take image and find x and y coordinates of this key and tell code to if finger is around threr or not
    # then consider it as click but drawbackis that if image is changes we need to manually change all the x and yof all keys

    # 2nd we will create rect and put text and create it as button

    img = drawAll(img, buttonList)

    if lmList:  # if there is hand present
        for button in buttonList:
            # we need to check location of each btn and then we need to check is our finger is in that range or not
            x, y = button.pos
            w, h = button.size

            # point no 8 for fore finger itp and 12 for middlefinger tip

            if x < lmList[8][0] < x + w and y < lmList[8][1] < y + h:  # value x and y for our finger tip lmlist[x][y]
                cv2.rectangle(img, button.pos, (x + w, y + h), (178, 38, 254), cv2.FILLED)
                cv2.putText(img, button.text, (x + 20, y + 65), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
                l, _, _ = detector.findDistance(8, 12, img, draw=False)
                print(l)

                ## when clicked
                if l < 30:

                    cv2.rectangle(img, button.pos, (x + w, y + h), (234, 24, 25), cv2.FILLED)
                    cv2.putText(img, button.text, (x + 20, y + 65), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
                    if button.text == "_":
                        keyboard.press(Key.space)
                        finalText += " "
                        text = "space"
                        engine.say(text)
                        engine.runAndWait()
                        sleep(0.15)
                    elif button.text == "<-":
                        keyboard.press(Key.backspace)
                        p = len(finalText)
                        finalText = finalText[:p - 1]
                        text = "backspace"
                        engine.say(text)
                        engine.runAndWait()
                        sleep(0.15)
                    else:
                        keyboard.press(button.text)
                        finalText += button.text
                        text = button.text
                        engine.say(text)
                        engine.runAndWait()
                        sleep(0.15)

                # pygame.mixer.init()
                # crash_sound = pygame.mixer.Sound("clickbait.wav")
                # crash_sound.play()

    cv2.rectangle(img, (50, 450), (1000, 550), (9, 254, 40), cv2.FILLED)
    cv2.putText(img, finalText, (60, 525), cv2.FONT_HERSHEY_PLAIN, 5, (255, 255, 255), 5)

    # for the click part if the distance between forefinger tip and middlefinger tip is very small then consider click
    # if not small enough then don't consider it as a click

    cv2.imshow("Image", img)
    cv2.waitKey(1)
