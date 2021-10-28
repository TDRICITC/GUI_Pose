# -*- coding: utf-8 -*-
"""
Created on Fri Oct 15 10:03:17 2021

@author: GWJIANG
"""
import threading
import tkinter as tk
from tkinter import *
import cv2
from PIL import Image,ImageTk
from random import choice
import cv2
import time
import json                    
import requests
from PIL import Image
from io import BytesIO
from cvzone.HandTrackingModule import HandDetector

import mediapipe as mp

def video_loop():

    global switch
    global left
    global right
    global vertical

    success, img = camera.read()  
    img = cv2.flip(img,1)

    hands, img = detector.findHands(img)
    cv2.putText(img, text=watch_where, org=(10,30), fontFace= cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.6, color=(0,0,0), thickness=2, lineType=cv2.LINE_AA)
    cv2.putText(img, 'up & down:'+'%.3f'%vertical, (10, 60), cv2.FONT_HERSHEY_PLAIN,1, (0, 0, 255), 1, cv2.LINE_AA)
    cv2.putText(img, 'left:'+'%.3f'%right, (10, 80), cv2.FONT_HERSHEY_PLAIN,1, (0, 0, 255), 1, cv2.LINE_AA)
    cv2.putText(img, 'right:'+'%.3f'%left, (10, 100), cv2.FONT_HERSHEY_PLAIN,1, (0, 0, 255), 1, cv2.LINE_AA)

    
    if switch_watch == 1:
        results = face_mesh.process(img) 
        
        if results.multi_face_landmarks: 
            for face_landmarks in results.multi_face_landmarks: 
                
                mp_drawing.draw_landmarks( image=img, landmark_list=face_landmarks, connections=mp_face_mesh.FACE_CONNECTIONS, landmark_drawing_spec=drawing_spec, connection_drawing_spec=drawing_spec1) 




    if switch == 0:            
        cv2.rectangle(img, (400, 10), (640, 230), (0, 255, 0), 2)
    else:
        cv2.rectangle(img, (400, 10), (640, 230), (0, 0, 255), 2)

    if success:

        bbox1 = ''
        bbox2 = ''
        res_object1 = {}
        res_object2 = {}
        return_object ={}
        
        
        #############判斷手有沒有進方框################
        if hands:
            # Hand 1
            hand1 = hands[0]
            bbox1 = hand1["bbox"] # Bounding box info x,y,w,h
            res_object1 = {}

            res_object1['pose_rectangle'] =  {
                "top": bbox1[1],
                "left": bbox1[0],
                "width": bbox1[2],
                "height": bbox1[3]  
                }
        
            if len(hands) == 2:
                # Hand 2
                hand2 = hands[1]
                bbox2 = hand2["bbox"] 
                res_object2['pose_rectangle'] =  {
                    "top": bbox2[1],
                    "left": bbox2[0],
                    "width": bbox2[2],
                    "height": bbox2[3]  
                    }
                
        return_object = res_object1
        
        if bbox2 != '':
            if res_object2['pose_rectangle']['top'] < res_object1['pose_rectangle']['top']:
                return_object = res_object2

        if return_object != {}:
            if return_object['pose_rectangle']['top']+return_object['pose_rectangle']['height'] < 230 and return_object['pose_rectangle']['left']+return_object['pose_rectangle']['width'] > 400:
                if switch == 0 and btn['state'] == 'disabled':
                    recognition_go()

        

        ###########
        width = 640
        height = 480
        dim = (width, height)

        # resize image
        img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)

        cv2image = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)#转换颜色从BGR到RGBA
        current_image = Image.fromarray(cv2image)#将图像转换成Image对象
        imgtk = ImageTk.PhotoImage(image=current_image)
        panel.imgtk = imgtk
        panel.config(image=imgtk)
        root.after(1, video_loop)
       

def Watch():
    i = 1
    global switch_watch
    global watch_where
    global l2
    global left
    global right
    global vertical
    while switch_watch==1:
        
        i = i+1
        success, img = camera.read() 


        if success:
            try:
                frame_im = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                pil_im = Image.fromarray(frame_im)
                stream = BytesIO()
                pil_im.save(stream, format="JPEG")
                stream.seek(0)
                img_for_post = stream.read()
                
                files = {'image': img_for_post}
                r = requests.post(
                    url2,
                    files=files
                )
                return_text = json.loads(r.text)

                result = return_text["feature_list"][0]['head_pose_list'][0]['looking']
                left =  return_text["feature_list"][0]['head_pose_list'][0]['left_cheek_diff']
                right = return_text["feature_list"][0]['head_pose_list'][0]['right_cheek_diff']
                vertical = return_text["feature_list"][0]['head_pose_list'][0]['nor_vertical_diff']

                if len(l2) >= 5:
                    l2.pop(0)
                    l2.append(result)
                    if l2.count('focus')>=4:
                        watch_where  = 'Looking'
                    else:
                        watch_where  = 'No Looking'

                else:
                    l2.append(result)
                   
                    if l2.count('focus')>=4:
                        watch_where  = 'Looking'
                    else:
                        watch_where  = 'loading'
                print(l2)
                time.sleep(0.05)
            except Exception:
                pass

def thread(i):
    global l
    success, img = camera.read()  
    if success:
        try:
            frame_im = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            pil_im = Image.fromarray(frame_im)
            stream = BytesIO()
            pil_im.save(stream, format="JPEG")
            stream.seek(0)
            img_for_post = stream.read()
            
            files = {'image': img_for_post}
            r = requests.post(
                url,
                files=files
            )
            result = json.loads(r.text)
            result = result["feature_list"][0]['pose_list'][0]['label']
            l.append(result)
        except Exception:
            pass


def recognition():
    global switch
    switch = 1
    
    start = time.time()
    end = time.time()
    global l
    l = ["沒比動作喔"]
    i=0
   
    Execution_time = 0
    count = 0
    threads = []

    while count < 5 and i < 30: 
        time.sleep(0.1)
        threads.append(threading.Thread(target = thread, args = (i,)))
        threads[i].start()
        maxlabel = max(l,key=l.count)  
        count = l.count(maxlabel)
        i = i+1
       
    end = time.time()      

    Execution_time = end -start
    
    if n == maxlabel:
        answer = "相同"
    else:
        answer = "不相同"

    if answer =="不相同":
        success, img = camera.read()
        hands, img = detector.findHands(img)
        cv2.imwrite('Error_pose/'+str(n)+'_{}.jpg'.format(time.time()), img)

    message ='''
    
    你的答案是:''' + str(maxlabel) + '''
    與題目:'''+ answer +'''
    總共辨識了:''' + str(i)+''' 張
    執行時間:''' + str(Execution_time)+''' 秒
    
     '''
    text_box.delete("1.0", "end") 
    text_box.insert('end', message)

    btn['state'] = tk.NORMAL
    switch = 0

def recognition_go():
    threading.Thread(target=recognition).start()

def Watch_go():
    global switch_watch
    if switch_watch == 0:
        switch_watch = 1
    else:
        switch_watch = 0
    threading.Thread(target=Watch).start()

def open_img():
    global n
    text_box.delete("1.0", "end") 
    btn['state'] = tk.DISABLED
    num = [1, 2, 3, 4, 5] 
    if n != 0:
        num.remove(n)

    n= choice(num) # 隨機抽取一個

    img = Image.open(str(n)+".jpg")
    img = img.resize((250, 250), Image.ANTIALIAS)
    img = ImageTk.PhotoImage(img)
    
    #panelB = Label(root, image=img)
    panelB.pack(padx=10, pady=10)
    panelB.config(image=img)
    panelB.image = img
    panelB.pack()
    
detector = HandDetector(detectionCon=0.7, maxHands=2)
url = 'http://34.80.31.212/tdri/api/vision/analyze?return_features=pose'
url2 = 'http://34.80.31.212/tdri/api/vision/analyze?return_features=head_pose'
wCam, hCam = 640, 480

camera = cv2.VideoCapture(0)    #相機
camera.set(3, wCam)
camera.set(4, hCam)

mp_drawing = mp.solutions.drawing_utils 
mp_face_mesh = mp.solutions.face_mesh 
face_mesh = mp_face_mesh.FaceMesh( min_detection_confidence=0.5, min_tracking_confidence=0.5) 
drawing_spec = mp_drawing.DrawingSpec(thickness=2, circle_radius=1) 
drawing_spec1 = mp_drawing.DrawingSpec(thickness=2, circle_radius=1,color=(255,255,255)) 


n = 0
switch = 0
switch_watch = 0
watch_where = '1'
left = 0
right = 0
vertical = 0
l = []
l2 = []

root = Toplevel()
root.title("opencv + tkinter")

panel = Label(root)  # initialize image panel
panel.pack(side="left",padx=2, pady=2)


text_box = Text(
    root,
    height=12,
    width=40
)
text_box.pack(expand=True,side='bottom')

text_box.configure(font=(20))

message = ''' 請在綠框框內比手勢!! '''

text_box.insert('end', message)
panelB = Label(root, text = "跟著我比pose")  # initialize image panel
panelB.pack(side="top",padx=10, pady=10)

root.config(cursor="arrow")


btn = Button(root, text='點我出現題目', command=lambda:[open_img()])
btn.pack(fill="both", expand=True, padx=10, pady=10)
btn2 = Button(root, text='有沒有注視(再按一次關閉)', command=lambda:[Watch_go()])
btn2.pack(fill="both", expand=True, padx=10, pady=10)

video_loop()


root.mainloop()
# 当一切都完成后，关闭摄像头并释放所占资源
camera.release()
cv2.destroyAllWindows()
