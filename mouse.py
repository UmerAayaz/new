import cv2 
import mediapipe as mp 
import pyautogui 
import math 
from enum import IntEnum 
from ctypes import cast, POINTER 
from comtypes import CLSCTX_ALL 
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume 
from google.protobuf.json_format import MessageToDict 
import screen_brightness_control as sbcontrol
import os
import streamlit as st
from PIL import Image


# To create GUI 
import tkinter as tk 
from PIL import ImageTk, Image 
pyautogui.FAILSAFE = False
mp_drawing = mp.solutions.drawing_utils 
mp_hands = mp.solutions.hands 

class gesturechec:  
    def __init__(this, hand_check):
        this.prev_sign = Gestures.PALM_NO_FINGER
        this.frame_count = 0
        this.ori__sign = Gestures.PALM_NO_FINGER
        this.result = None
        this.hand_check = hand_check
        this.finger = 0 
    
    #[8,5,0] shahadat wale ongale  [12,9,0] middle fingers [16,13,0] chote ongle barabr wale [20,17,0] chote onglae
    def set_finger(this): 
        if this.result == None: 
            return
        coordinates = [[8,5,0],[12,9,0],[16,13,0],[20,17,0]] 
        this.finger = 0
        this.finger = this.finger | 0 #thumb 
        for x, coordinate in enumerate(coordinates):             
            distance_of_c1 = this.get_distance(coordinate[:2]) 
            distance_of_c2 = this.get_distance(coordinate[1:])         
            try: 
                ratio = round(distance_of_c1/distance_of_c2,1) 
            except: 
                ratio = round(distance_of_c1/0.01,1) 
            this.finger = this.finger << 1
            if ratio > 0.5 : 
                this.finger = this.finger | 1


    def get_dist(this, coordinate): 
        dist = (this.result.landmark[coordinate[0]].x - this.result.landmark[coordinate[1]].x)**2
        dist += (this.result.landmark[coordinate[0]].y - this.result.landmark[coordinate[1]].y)**2
        dist = math.sqrt(dist) 
        return dist 
    
    
    def get_z_axis(this, coordinate): 
        return abs(this.result.landmark[coordinate[0]].z - this.result.landmark[coordinate[1]].z) 
    

    def updateresult(this, result): 
        this.result = result 

    
    def get_distance(this, coordinate): 
        sign = -1
        if this.result.landmark[coordinate[0]].y < this.result.landmark[coordinate[1]].y: 
            sign = 1
        distance = (this.result.landmark[coordinate[0]].x - this.result.landmark[coordinate[1]].x)**2
        distance += (this.result.landmark[coordinate[0]].y - this.result.landmark[coordinate[1]].y)**2
        distance = math.sqrt(distance) 
        return distance*sign 
    
    def Creation_of_gesture(this): 
        if this.result == None: 
            return Gestures.PALM_NO_FINGER
        curr_sign = Gestures.PALM_NO_FINGER
        if this.finger in [Gestures.LITTLE_FINGER]: 
            if this.hand_check == HandchecK.Left : 
                curr_sign = Gestures.P_LEFT
            else: 
                curr_sign = Gestures.P_RIGHT                  
        elif Gestures.F_2FINGER == this.finger : 
            coordinate = [[8,12],[5,9]] 
            distance_of_c1 = this.get_dist(coordinate[0]) 
            distance_of_c2 = this.get_dist(coordinate[1]) 
            ratio = distance_of_c1/distance_of_c2 
            if ratio > 1.7: 
                curr_sign = Gestures.MOUSE_MOVEMENT
            else: 
                if this.get_z_axis([8,12]) < 0.1: 
                    curr_sign = Gestures.DOUBLE_C
                else: 
                    curr_sign = Gestures.MIDDLE_F      
        else: 
            curr_sign = this.finger 
        
        if curr_sign == this.prev_sign: 
            this.frame_count += 1
        else: 
            this.frame_count = 0
        this.prev_sign = curr_sign 
        if this.frame_count > 4 : 
            this.ori__sign = curr_sign 
        return this.ori__sign

class HandchecK(IntEnum):  
    Left= 0   ;    Right = 1   


class HandController: 
    prev_hand = None; flag = False; grabflag = False; pinchmajorflag = False; pinchminorflag = False; 
    pinchstartxcoord = None; pinchstartycoord = None; grabflag = False; pinchdirectionflag = None; 
    flag = False; pinchlv = 0; framecount = 0; prev_hand = None; pinch_threshold = 0.3; prevpinchlv = 0
    
    def getpinchylv(result): 
        dist = round((HandController.pinchstartycoord - result.landmark[8].y)*10,1) 
        return dist 
    
    def scrollHorizontal(): 
        pyautogui.keyDown('shift') 
        pyautogui.keyDown('ctrl') 
        pyautogui.scroll(-120 if HandController.pinchlv > 0.0 else 120) 
        pyautogui.keyUp('ctrl') 
        pyautogui.keyUp('shift') 
    
    


    def brightnesschange(): 
        currentBrightnessLv = sbcontrol.get_brightness()/100.0
        currentBrightnessLv += HandController.pinchlv/50.0
        if currentBrightnessLv > 1.0: 
            currentBrightnessLv = 1.0
        elif currentBrightnessLv < 0.0: 
            currentBrightnessLv = 0.0    
        sbcontrol.fade_brightness(int(100*currentBrightnessLv) , start = sbcontrol.get_brightness()) 
   
    def getpinchxlv(result): 
        dist = round((result.landmark[8].x - HandController.pinchstartxcoord)*10,1) 
        return dist 

    def volumechange(): 
        devices = AudioUtilities.GetSpeakers() 
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None) 
        volume = cast(interface, POINTER(IAudioEndpointVolume)) 
        currentVolumeLv = volume.GetMasterVolumeLevelScalar() 
        currentVolumeLv += HandController.pinchlv/50.0
        if currentVolumeLv > 1.0: 
            currentVolumeLv = 1.0
        elif currentVolumeLv < 0.0: 
            currentVolumeLv = 0.0
        volume.SetMasterVolumeLevelScalar(currentVolumeLv, None) 
    
    def scrollVertical(): 
        pyautogui.scroll(120 if HandController.pinchlv > 0.0 else -120)     
    
    def getpinchylv(result): 
        dist = round((HandController.pinchstartycoord - result.landmark[8].y)*10,1) 
        return dist 
   
    def get_position(result): 
        coordinate = 9
        position = [result.landmark[coordinate].x , result.landmark[coordinate].y]                                                                                                                                                                                                      
        sx, sy = pyautogui.size() 
        x_old, y_old = pyautogui.position() 
        x = int(position[0]*sx) 
        y = int(position[1]*sy) 
        if HandController.prev_hand is None: 
            HandController.prev_hand = x, y 
        delta_x = x - HandController.prev_hand[0] 
        delta_y = y - HandController.prev_hand[1] 
        distsq = delta_x**2 + delta_y**2
        ratio = 1
        HandController.prev_hand = [x, y] 
        if distsq <= 25: 
            ratio = 0
        elif distsq <= 900: 
            ratio = 0.07 * (distsq ** (1/2)) 
        else: 
            ratio = 2.1
        x, y = x_old + delta_x * ratio, y_old + delta_y * ratio 
        return (x, y) 
    
    def pinch_control_init(result): 
        HandController.pinchstartxcoord = result.landmark[8].x 
        HandController.pinchstartycoord = result.landmark[8].y 
        HandController.pinchlv = 0
        HandController.prevpinchlv = 0
        HandController.framecount = 0
    
    # Hold final position for 5 frames to change status 
    def pinch_control(result, controlHorizontal, controlVertical): 
        if HandController.framecount == 5: 
            HandController.framecount = 0
            HandController.pinchlv = HandController.prevpinchlv 

            if HandController.pinchdirectionflag == True: 
                controlHorizontal() #x 

            elif HandController.pinchdirectionflag == False: 
                controlVertical() #y 
        lvx = HandController.getpinchxlv(result) 
        lvy = HandController.getpinchylv(result)         
        if abs(lvy) > abs(lvx) and abs(lvy) > HandController.pinch_threshold: 
            HandController.pinchdirectionflag = False
            if abs(HandController.prevpinchlv - lvy) < HandController.pinch_threshold: 
                HandController.framecount += 1
            else: 
                HandController.prevpinchlv = lvy 
                HandController.framecount = 0
        elif abs(lvx) > HandController.pinch_threshold: 
            HandController.pinchdirectionflag = True
            if abs(HandController.prevpinchlv - lvx) < HandController.pinch_threshold: 
                HandController.framecount += 1
            else: 
                HandController.prevpinchlv = lvx 
                HandController.framecount = 0
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                
    def handle_controls(gesture, result):             
        x, y = None, None
        if gesture != Gestures.PALM_NO_FINGER: 
            x, y = HandController.get_position(result)     
        # flag reset 
        if gesture != Gestures.PUNCH and HandController.grabflag: 
            HandController.grabflag = False
            pyautogui.mouseUp(button = "left") 
        if gesture != Gestures.P_RIGHT and HandController.pinchmajorflag: 
            HandController.pinchmajorflag = False
        if gesture != Gestures.P_LEFT and HandController.pinchminorflag: 
            HandController.pinchminorflag = False
        # implementation 
        if gesture == Gestures.MOUSE_MOVEMENT: 
            HandController.flag = True
            pyautogui.moveTo(x, y, duration = 0.1) 
        elif gesture == Gestures.PUNCH: 
            if not HandController.grabflag : 
                HandController.grabflag = True
                pyautogui.mouseDown(button = "left") 
            pyautogui.moveTo(x, y, duration = 0.1) 
        elif gesture == Gestures.MIDDLE_F and HandController.flag: 
            pyautogui.click(button = "left")
            HandController.flag = False
        elif gesture == Gestures.I_FINGER and HandController.flag: 
            pyautogui.click(button='right') 
            
            HandController.flag = False
        elif gesture == Gestures.DOUBLE_C and HandController.flag: 
            pyautogui.doubleClick() 
            HandController.flag = False
        elif gesture == Gestures.P_LEFT: 
            if HandController.pinchminorflag == False: 
                HandController.pinch_control_init(result) 
                HandController.pinchminorflag = True
            HandController.pinch_control(result, HandController.scrollHorizontal, HandController.scrollVertical)     
        elif gesture == Gestures.P_RIGHT: 
            if HandController.pinchmajorflag == False: 
                HandController.pinch_control_init(result) 
                HandController.pinchmajorflag = True
            HandController.pinch_control(result, HandController.brightnesschange, HandController.volumechange)

class Gestures(IntEnum): 
    PUNCH = 0; LITTLE_FINGER = 1; MIDDLE_F = 4; I_FINGER = 8; F_2FINGER = 12; 
    PALM_NO_FINGER = 31; MOUSE_MOVEMENT = 33; DOUBLE_C = 34; P_RIGHT = 35; P_LEFT = 36


class GestureController: 
    gc_mode = 0; cap = None; CAM_HEIGHT = None; CAM_WIDTH = None; 
    hr_major = None; hr_minor = None; dom_hand = True

    
    def classify_hands(results): 
        left, right = None, None
        try: 
            handedness_dict = MessageToDict(results.multi_handedness[0]) 
            if handedness_dict['classification'][0]['label'] == 'Right': 
                right = results.multi_hand_landmarks[0] 
            else: 
                left = results.multi_hand_landmarks[0] 
        except: 
            pass
        try: 
            handedness_dict = MessageToDict(results.multi_handedness[1]) 
            if handedness_dict['classification'][0]['label'] == 'Right': 
                right = results.multi_hand_landmarks[1] 
            else: 
                left = results.multi_hand_landmarks[1] 
        except: 
            pass    
        if GestureController.dom_hand == True: 
            GestureController.hr_major = right 
            GestureController.hr_minor = left 
        else: 
            GestureController.hr_major = left 
            GestureController.hr_minor = right 

    def __init__(this): 
        GestureController.gc_mode = 1
        GestureController.cap = cv2.VideoCapture(0) 
        GestureController.CAM_HEIGHT = GestureController.cap.get(cv2.CAP_PROP_FRAME_HEIGHT) 
        GestureController.CAM_WIDTH = GestureController.cap.get(cv2.CAP_PROP_FRAME_WIDTH) 

    def start(this):     
        handmajor = gesturechec(HandchecK.Right) 
        handminor = gesturechec(HandchecK.Left) 

        with mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands: 
            while GestureController.cap.isOpened() and GestureController.gc_mode: 
                success, image = GestureController.cap.read() 

                if not success: 
                    print("Ignoring empty camera frame.") 
                    continue                
                image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB) 
                image.flags.writeable = False
                results = hands.process(image)         
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR) 
                if results.multi_hand_landmarks:                 
                    GestureController.classify_hands(results) 
                    handmajor.updateresult(GestureController.hr_major) 
                    handminor.updateresult(GestureController.hr_minor) 
                    handmajor.set_finger() 
                    handminor.set_finger() 
                    gest_name = handminor.Creation_of_gesture() 
                    if gest_name == Gestures.P_LEFT: 
                        HandController.handle_controls(gest_name, handminor.result) 
                    else: 
                        gest_name = handmajor.Creation_of_gesture() 
                        HandController.handle_controls(gest_name, handmajor.result) 
                    
                    for hand_landmarks in results.multi_hand_landmarks:
                        mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS, 
                                   mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=2, circle_radius=4),
                                   mp_drawing.DrawingSpec(color=(110, 50, 50), thickness=2)) 
                else: 
                    HandController.prev_hand = None
                cv2.imshow('GESTURE RECOGNITION SYSTEM', image) 
                if cv2.waitKey(5) & 0xFF == 13: 
                    break
        GestureController.cap.release() 
        cv2.destroyAllWindows()
 # Assuming mouse.py contains the GestureController class and runvirtualmouse function

def run_virtual_mouse():
    global gc1
    gc1 = GestureController()
    gc1.start()

def close_program():
    if 'gc1' in globals():
        gc1.gc_mode = 0  # Stop gesture recognition
    st.stop()

st.set_page_config(page_title="Gesture Recognition System", page_icon="LOGONEW.PNG")

# Load background image
bg_image = Image.open("aaaa (5).png")  # Replace "background_image.jpg" with the path to your image

# Display background image
st.image(bg_image, use_column_width=True)

# Create buttons
col1, col2 = st.columns(2)
with col1:
    start_button = st.button("START", key="start_button", help="Start gesture recognition", on_click=run_virtual_mouse)

with col2:
    close_button = st.button("CLOSE", key="close_button", help="Close the program", on_click=close_program)

# You can add more Streamlit components as needed

# This line is not necessary as Streamlit automatically runs the app
# st.run_app()
