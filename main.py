# Imports
import pygame
import cv2
from cvzone.HandTrackingModule import HandDetector
import time
import random
import os
import sys
import pandas as pd

# Initialize and Create Window
pygame.init()

width, height = 1280, 720
window = pygame.display.set_mode((width,height))
pygame.display.set_caption('CNY Lampion Popping Game')

# Initialize clock for FPS
fps = 30
clock = pygame.time.Clock()

# Set Folder Path according to exe or py file that is being run
if getattr(sys, 'frozen', False):
    folder_path = os.path.dirname(sys.executable)
else:
    folder_path = os.path.dirname(__file__)

# Load Resources
resources_path = os.path.join(folder_path, 'Resources/')
database = os.path.join(resources_path, 'database.csv')

bgmusic_path = os.path.join(resources_path, 'BG Music/')
sfx_path = os.path.join(resources_path, 'SFX/')
fonts_path = os.path.join(resources_path, 'Fonts/')
images_path = os.path.join(resources_path, 'Images/')

# Set App Icon
icon = pygame.image.load(os.path.join(images_path, 'app-icon.png')).convert_alpha()
pygame.display.set_icon(icon)

# Load BG Music
homeMusic = pygame.mixer.Sound(os.path.join(bgmusic_path, 'homeMusic.mp3'))
homeMusic.set_volume(0.1)
gameMusic = pygame.mixer.Sound(os.path.join(bgmusic_path, 'gameMusic.mp3'))
gameMusic.set_volume(0.1)
endMusic = pygame.mixer.Sound(os.path.join(bgmusic_path, 'endMusic.mp3'))
endMusic.set_volume(0.1)

# Load Sound Effects
pop_sfx = pygame.mixer.Sound(os.path.join(sfx_path, 'pop.mp3'))
pop_sfx.set_volume(1)
transition = pygame.mixer.Sound(os.path.join(sfx_path, 'transition.mp3'))
transition.set_volume(1)

# Load Fonts
font1_100 = pygame.font.Font(os.path.join(fonts_path, 'aAsianNinja.ttf'), 100)
font1_70 = pygame.font.Font(os.path.join(fonts_path, 'aAsianNinja.ttf'), 70)
font2_50 = pygame.font.Font(os.path.join(fonts_path, 'go3v2.ttf'), 50)
font2_100 = pygame.font.Font(os.path.join(fonts_path, 'go3v2.ttf'), 100)

# Load Images
home_path = os.path.join(images_path, 'Home/')
game_path = os.path.join(images_path, 'Game/')
end_path = os.path.join(images_path, 'End/')

cursor = pygame.image.load(os.path.join(images_path, 'cursor.png')).convert_alpha()

# Home Screen Images
homeBG = pygame.image.load(os.path.join(home_path, 'homeBG.jpg')).convert()
board = pygame.image.load(os.path.join(home_path, 'bulletin_board.png')).convert_alpha()

playBtn = pygame.image.load(os.path.join(home_path, 'playBtn.png')).convert_alpha()
playBtnRect = playBtn.get_rect()
playBtnRect.x = 150
playBtnRect.y = height/2 - 200

# Game Screen Images
gameBG = pygame.image.load(os.path.join(game_path, 'gameBG.jpg')).convert()
dart = pygame.image.load(os.path.join(game_path, 'dart.png')).convert_alpha()
pop_sprite = pygame.image.load(os.path.join(game_path, 'pop.png')).convert_alpha()

# Lampions
lampion1 = pygame.image.load(os.path.join(game_path, 'lampion1.png')).convert_alpha()
lampion_rect1 = lampion1.get_rect()

lampion2 = pygame.image.load(os.path.join(game_path, 'lampion2.png')).convert_alpha()
lampion_rect2 = lampion2.get_rect()

lampion3 = pygame.image.load(os.path.join(game_path, 'lampion3.png')).convert_alpha()
lampion_rect3 = lampion3.get_rect()

lampion4 = pygame.image.load(os.path.join(game_path, 'lampion4.png')).convert_alpha()
lampion_rect4 = lampion4.get_rect()

special_lampion = pygame.image.load(os.path.join(game_path, 'special lampion.png')).convert_alpha()
special_lampion_rect = special_lampion.get_rect()

lampion_rects = {'lampion_rect1': lampion_rect1,
                'lampion_rect2': lampion_rect2,
                'lampion_rect3': lampion_rect3,
                'lampion_rect4': lampion_rect4,
                'special_lampion_rect': special_lampion_rect}

lampion_images = {'lampion1': lampion1,
                'lampion2': lampion2,
                'lampion3': lampion3,
                'lampion4': lampion4,
                'special_lampion': special_lampion}

# Curtains
curtainsLeft = pygame.image.load(os.path.join(game_path, 'CurtainsLeft.png')).convert_alpha()
curtainsLeftRect = curtainsLeft.get_rect()
curtainsLeftRect.x = 0
curtainsLeftRect.y = 0

curtainsRight = pygame.image.load(os.path.join(game_path, 'CurtainsRight.png')).convert_alpha()
curtainsRightRect = curtainsRight.get_rect()
curtainsRightRect.x = width - 515
curtainsRightRect.y = 0

# End Screen Images
endBG = pygame.image.load(os.path.join(end_path, 'EndBG.png')).convert()
textFrame = pygame.image.load(os.path.join(end_path, 'textFrame.png')).convert_alpha()

textInput = pygame.image.load(os.path.join(end_path, 'textInput.png')).convert_alpha()
textInput_rect = textInput.get_rect()
textInput_rect.x = 350
textInput_rect.y = 70

backbtn = pygame.image.load(os.path.join(end_path, 'back.png')).convert_alpha()
backbtn_rect = backbtn.get_rect()
backbtn_rect.x = 200
backbtn_rect.y = 70

quitbtn = pygame.image.load(os.path.join(end_path, 'quit.png')).convert_alpha()
quitbtn_rect = quitbtn.get_rect()
quitbtn_rect.x = width-350
quitbtn_rect.y = 70


# Webcam
cap = cv2.VideoCapture(0)
cap.set(3, width)
cap.set(4, height)

# Hand Tracking
detector = HandDetector(maxHands=1, detectionCon=0.6)

# Reset Lampions when out of frame or popped.
x_points = [100, 300, 500, 700, 900, 1100] # List of possible respawn points
def reset_lampions(keyRect, y=height):
    rect = lampion_rects[keyRect]

    keys = list(lampion_rects.keys())
    values = list(lampion_rects.values())
    index = keys.index(keyRect)
    values.pop(index)

    rect.y = y
    while True:
        rect.x = random.choice(x_points)
        if rect.collidelist(values) == -1: 
            # Make sure the lampions don't overlap each other
            break

# Reset Initial Position of Lampions
def position_lampions():
    lampion_rect1.x = 200
    lampion_rect1.y = 700

    lampion_rect2.x = 400
    lampion_rect2.y = 700

    lampion_rect3.x = 630
    lampion_rect3.y = 700

    lampion_rect4.x = 880
    lampion_rect4.y = 700

    special_lampion_rect.x = 575
    special_lampion_rect.y = 700

# Keyboard Buttons for Name Scene
keys = [["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
        ["A", "S", "D", "F", "G", "H", "J", "K", "L"], 
        ["Z", "X", "C", "V", "B", "N", "M"]] 

# Generate Button Instances for every key
class Button():
    def __init__(self, pos, text, size=(85, 85)):
        self.pos = pos
        self.size = size
        self.text = text

    def getRect(self):
        return pygame.rect.Rect(self.pos, self.size)

buttonList = []
for i in range(len(keys)): # Rows
    for j, key in enumerate(keys[i]): # Columns
        buttonList.append(Button((100 * j + 50, 100 * i + 50), key))

# Backspace Key (takes 3 cells)
x, y, w, h = 750, 250, 290, 85
buttonList.append(Button((x,y), 'Backspace', (w,h)))

# Enter Key (takes 3 cells)
x, y, w, h = 850, 350, 290, 85
buttonList.append(Button((x,y), 'Enter', (w,h)))

def get_leaderboard():
    db = pd.read_csv(database)
    db = db.sort_values(by='score', ascending=False)
    if len(db) > 10:
        names = db['name'][:10].to_numpy()
        scores = db['score'][:10].to_numpy()
    else:
        names = db['name'].to_numpy()
        scores = db['score'].to_numpy()

    return names, scores

# Scene Manager
class SceneManager:
    def __init__(self, duration = 30, initial_speed = 5, increase_speed=0.35):
        self.duration = duration
        self.initial_speed = initial_speed
        self.increase_speed = increase_speed
        # variable for changing scenes
        self.state = 'home' 
        # At first launch of the App
        # Get top 10 names and scores from database
        self.names, self.scores = get_leaderboard()

    def displayHomeScreen(self):
        # Display UI
        window.blit(homeBG, (0,0))
        window.blit(playBtn, playBtnRect)
        window.blit(board, (50, 575))

        title = font1_100.render('CNY Lampion Popping Game', True, 
                            (153, 52, 65), (255, 184, 177))
        window.blit(title, (100, 20))

        # Display the Database
        length = len(self.names)
        for i in range(length):
            text = font2_50.render(f'{i+1}. {self.names[i]}: {self.scores[i]}',
                                    True, (153, 52, 65), (255, 184, 177))
            window.blit(text, (800, i * 55 + 150))
        
        # Detect Hand from Webcam
        _, img = cap.read()
        img = cv2.flip(img, 1)
        hands = detector.findHands(img, flipType=False, draw=False)
        
        if hands:
            hand = hands[0]
            lmList = hand['lmList']
            fingers = detector.fingersUp(hand) 

            # If teach and middle fingers are raised up..
            if fingers[1] == 1 and fingers[2] == 1:
                # Get X, Y coordinate of the end points of each finger
                teachX, teachY = lmList[8][0:2] 
                middleX, middleY = lmList[12][0:2]
                # Display cursor on both fingers
                window.blit(cursor, (teachX-25, teachY-40))
                window.blit(cursor, (middleX-25, middleY-40))
                # and if the teach finger collides with the button..
                if playBtnRect.collidepoint(teachX, teachY):
                    distance = detector.findDistance((teachX, teachY), 
                                                (middleX, middleY))[0]
                    
                    if distance < 45: # Clicked..
                        # Reset Variables
                        self.start = time.time() 
                        self.score = 0 
                        self.speed = self.initial_speed
                        # Reset Initial Position of Lampions
                        position_lampions()
                        # Reset Curtains' Location
                        curtainsLeftRect.x = 0
                        curtainsRightRect.x = width - 515
                        # Change to Game Scene
                        self.state = 'game' 
                        pygame.mixer.stop()
                        transition.play(0)
                        gameMusic.play(-1)
        
    def displayGameScreen(self):
        timeNow = time.time()
        timeLeft = round(self.duration - (timeNow - self.start))

        if timeLeft == 0:
            # Bcz TextInput Button only appears if Record is Broken, 
            # So to prevent UnboundLocalError, we need to assign the --
            # particular variables a value at the begining.
            self.fingersUp = False 
            self.teachX, self.teachY = 0, 0
            self.middleX, self.middleY = 0, 0

            # Get Previous Best Score from Second Line of Database
            file = open(database, 'r')
            self.prev_best = file.readlines()[1]
            file.close()

            # Display End Screen
            self.state = 'end' 
            pygame.mixer.stop()
            transition.play(0)
            endMusic.play(-1)

        else:
            # Display BG
            window.blit(gameBG, (0,0))
            x, y = None, None
            # Detect Hand from Webcam
            _, img = cap.read()
            img = cv2.flip(img, 1)
            hands = detector.findHands(img, flipType=False, draw=False)                

            if hands:
                hand = hands[0]
                fingers = detector.fingersUp(hand)
                if fingers[1] == 1: # If teach finger is Up..
                    # Display Dart UI on the end of teach finger
                    x, y = hand['lmList'][8][0:2]
                    window.blit(dart, (x-80, y-75))

            # Move and Display Lampions
            for image, keyRect in zip(lampion_images.values(), lampion_rects.keys()):
                rect = lampion_rects[keyRect] # Get Rect Object
                if keyRect == 'special_lampion_rect':
                    if timeLeft <= self.duration - 5:
                        if x and y:
                            if rect.collidepoint(x, y): # Check for collision
                                # Play SFX and animation
                                pop_sfx.play()
                                window.blit(pop_sprite, (x-100, y-75))
                                reset_lampions(keyRect, height*4)
                                self.speed += self.increase_speed
                                self.score += 10
                        
                        if rect.y < 0: # Reset Lampion if it's out of frame
                            reset_lampions(keyRect, height*4)
                    
                        rect.y -= self.speed
                        window.blit(image, rect)
                
                else:
                    if x and y:
                        if rect.collidepoint(x, y): # Check for collision
                            # Play SFX and animation
                            pop_sfx.play()
                            window.blit(pop_sprite, (x-100, y-75))
                            reset_lampions(keyRect)
                            self.speed += self.increase_speed
                            self.score += 5
                    
                    if rect.y < 0: # Reset Lampion if it's out of frame
                        reset_lampions(keyRect)
                
                    rect.y -= self.speed
                    window.blit(image, rect)

            # Display Score, timeLeft and FPS
            FPS = round(clock.get_fps())

            textScore = font2_50.render(f'Score: {self.score}', True, (0,255,0))
            countdown = font2_50.render(f'Time Left: {timeLeft}', True, (0,255,0))
            textFPS = font2_50.render(f'FPS: {FPS}', True, (0,255,0))

            window.blit(textScore, (35, 35))
            window.blit(countdown, (950, 35))
            window.blit(textFPS, (450, 35))

            # Play Curtain Opening Animation Every time Entering Game Screen
            if not curtainsLeftRect.x < -508 or not curtainsRightRect.x > width:
                curtainsLeftRect.x -= 10
                curtainsRightRect.x += 10

                window.blit(curtainsLeft, curtainsLeftRect)
                window.blit(curtainsRight, curtainsRightRect)
        
    def displayEndScreen(self):
        # Display BG and Buttons
        window.blit(endBG, (0,0))
        window.blit(backbtn, backbtn_rect)
        window.blit(quitbtn, quitbtn_rect)

        # Display Text Messages
        finalScore = font2_100.render(f'Final Score: {self.score}', True, (255,255,255))
        message = font2_100.render(r"TIME'S UP!", True, (255,255,255))

        back_message = font2_50.render('BACK', True, (255,255,255))
        quit_message = font2_50.render('QUIT', True, (255,255,255))

        window.blit(textFrame, (20, 225))
        window.blit(finalScore, (300, 350))
        window.blit(message, (350, 275))

        window.blit(back_message, (230, 30))
        window.blit(quit_message, (width-320, 30))

        # Detect Hand from Webcam
        _, img = cap.read()
        img = cv2.flip(img, 1)
        hands = detector.findHands(img, flipType=False, draw=False)

        # If Record broken
        if self.score > int(self.prev_best): 
            file = open(database, 'w')
            # Keep Name Unwritten First, Only Write Score
            file.write('Unknown' + '\n' + str(self.score))
            file.close()

            # Display Messages
            congrats_message = font1_70.render('Congratz! You have broken a new Record!', 
                                            True, (153, 52, 65), (255, 184, 177))
            prevbest_message = font1_70.render(f'Previous Best Score: {self.prev_best}',
                                            True, (153, 52, 65), (255, 184, 177))
            notify_message = font1_70.render('Enter your name by Clicking button on Top!',
                                            True, (153, 52, 65), (255, 184, 177))

            window.blit(congrats_message, (50, 485))
            window.blit(prevbest_message, (320, 560))
            window.blit(notify_message, (10, 635))
            # Display Button to Enter Name Screen
            window.blit(textInput, textInput_rect)

            if self.fingersUp == True:
                # If hand collides with TextInput Button
                if textInput_rect.collidepoint(self.teachX, self.teachY):
                    distance = detector.findDistance((self.teachX, self.teachY), 
                                                (self.middleX, self.middleY))[0]
                    
                    if distance < 45:
                        self.clicked = False # To avoid spam clicks on each key
                        self.finalText = '' # Reset Name
                        # Change to Name Scene
                        self.state = 'name'

        if hands:
            hand = hands[0]
            lmList = hand['lmList']
            fingers = detector.fingersUp(hand) 
            # If teach and middle fingers are raised up..
            if fingers[1] == 1 and fingers[2] == 1:
                self.fingersUp = True
                self.teachX, self.teachY = lmList[8][0:2] 
                self.middleX, self.middleY = lmList[12][0:2]

                # Display cursor on both fingers
                window.blit(cursor, (self.teachX-25, self.teachY-40))
                window.blit(cursor, (self.middleX-25, self.middleY-40))

                # and if the teach finger collides with the back button..
                if backbtn_rect.collidepoint(self.teachX, self.teachY):
                    distance = detector.findDistance((self.teachX, self.teachY), 
                                                (self.middleX, self.middleY))[0]
                    
                    if distance < 45:
                        # Get top 10 names and scores from database
                        self.names, self.scores = get_leaderboard()
                        # Change to Home Scene
                        self.state = 'home' 
                        pygame.mixer.stop()
                        homeMusic.play(-1)
                        return
                
                # or the teach finger collides with the quit button..
                elif quitbtn_rect.collidepoint(self.teachX, self.teachY):
                    distance = detector.findDistance((self.teachX, self.teachY), 
                                                (self.middleX, self.middleY))[0]
                    
                    if distance < 45:
                        # Closes the Game
                        pygame.quit() 
                        sys.exit()
            else:
                self.fingersUp = False

    def displayNameScreen(self):
        # Display BG
        window.blit(endBG, (0,0))
        # Detect Hand from Webcam
        _, img = cap.read()
        img = cv2.flip(img, 1)
        hands = detector.findHands(img, flipType=False, draw=False)

        # Displaying Text Entry
        if len(self.finalText) > 8:
            max = True
            warning = font2_100.render('Maximum Word Number Reached: 8',
                                        True, (255,0,0), (255,255,255))
            window.blit(warning, (100, 500))
        else:
            max = False

        pygame.draw.rect(window, (175, 0, 175), (50, 350, 650, 100))
        nametext = font2_100.render(self.finalText, True, (255, 255, 255))
        window.blit(nametext, (60, 335))
        
        if hands:  
            hand = hands[0]
            fingers = detector.fingersUp(hand) 
            # If teach and middle fingers are raised up..
            if fingers[1] == 1 and fingers[2] == 1:
                lmList = hand['lmList']
                teachX, teachY = lmList[8][0:2]
                middleX, middleY = lmList[12][0:2]

                # Draw all keyboard buttons
                # Special for Unused Key
                x, y, w, h = 950, 150, 85, 85
                pygame.draw.rect(window, (255, 0, 255), (x, y, w, h))
                for button in buttonList:
                    x, y = button.pos
                    w, h = button.size

                    pygame.draw.rect(window, (255, 0, 255), (x, y, w, h))
                    letter = font2_50.render(button.text, True, (255, 255, 255))
                    window.blit(letter, (x + 20, y + 30))

                    # And If button key collides with end of teach finger
                    if button.getRect().collidepoint(teachX, teachY):
                        # Display Hover Animation
                        pygame.draw.rect(window, (175, 0, 175), (x, y, w, h))
                        letter = font2_50.render(button.text, True, (255, 255, 255))
                        window.blit(letter, (x + 20, y + 30))
                        
                        distance = detector.findDistance((teachX, teachY), (middleX, middleY))[0]

                        # To avoid spam clicks, by checking whether the fingers are apart, after every click
                        if distance > 45 and self.clicked == True:
                            self.clicked = False

                        if distance < 45 and self.clicked == False:
                            self.clicked = True
                            # Delete last letter if backspace key is clicked
                            if button.text == 'Backspace':
                                self.finalText = self.finalText[:-1]
                            # Go back to home screen if enter key is clicked
                            elif button.text == 'Enter':
                                if self.finalText != '':
                                    # Only Write Name if Entered By user
                                    file = open(database, 'w')
                                    # Write name and score in file
                                    file.write(self.finalText + '\n' + str(self.score))
                                    file.close()
                                
                                # Get top 10 names and scores from database
                                self.names, self.scores = get_leaderboard()
                                
                                # Change to Home Scene
                                self.state = 'home' 
                                pygame.mixer.stop()
                                homeMusic.play(-1) 
                                return
                            else:
                                if not max:
                                    self.finalText += button.text # Adds Letter

                # Display cursor on both fingers
                window.blit(cursor, (teachX-25, teachY-40))
                window.blit(cursor, (middleX-25, middleY-40))

    def state_manager(self):
        if self.state == 'home':    
            self.displayHomeScreen()
        elif self.state == 'game':
            self.displayGameScreen()
        elif self.state == 'end':
            self.displayEndScreen()
        else: # state is name
            self.displayNameScreen()

scene_manager = SceneManager()
homeMusic.play(-1)

# Mainloop  
while True:
    # Get events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    # Helps change scenes based on state
    scene_manager.state_manager()

    # Update Display
    pygame.display.update()
    # Set FPS
    clock.tick(fps)
