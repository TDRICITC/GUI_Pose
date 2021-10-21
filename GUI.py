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
import random
from random import choice
import cv2
import time
import json                    
import requests
from PIL import Image
from io import BytesIO
from cvzone.HandTrackingModule import HandDetector


def video_loop():

    global switch
    success, img = camera.read()  # 从摄像头读取照片
    img = cv2.flip(img,1)

    hands, img = detector.findHands(img)
    cv2.putText(img, text=watch_where, org=(10,30),
                fontFace= cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.8, color=(0,0,0),
                thickness=2, lineType=cv2.LINE_AA)
    cv2.rectangle(img, (400, 10), (640, 230), (0, 255, 0), 2)

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
        cv2image = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)#转换颜色从BGR到RGBA
        current_image = Image.fromarray(cv2image)#将图像转换成Image对象
        imgtk = ImageTk.PhotoImage(image=current_image)
        panel.imgtk = imgtk
        panel.config(image=imgtk)
        root.after(1, video_loop)
       

def Watch():
    i = 0
    global watch_where
    while i == 0:
        i = i+1
        success, img = camera.read()  # 从摄像头读取照片
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
                result = json.loads(r.text)
                result = result["feature_list"][0]['face_list'][0]['head_pose']

                if abs(result['pitch']) < 15 and abs(result['yaw']) < 20:
                    watch_where  =  'Watching'
                else:
                    watch_where  =  'Not watching'
                print(result)
            except Exception:
                pass

def thread(i):
    global l
    success, img = camera.read()  # 从摄像头读取照片
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
            #result = result['pose_list'][0]['label']
            l.append(result)
            print(time.time())
        except Exception:
            pass


def recognition():
    global switch
    switch = 1
    text_box.delete("1.0", "end") 
    start = time.time()
    end = time.time()
    global l
    l = ["沒比動作喔"]
    i=0
   
    Execution_time = 0
    count = 0
    threads = []

    while count<5: 
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
    threading.Thread(target=Watch).start()

def open_img():
    global n
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
url2 = 'http://34.80.31.212/tdri/api/vision/analyze?return_features=face'
wCam, hCam = 640, 480
camera = cv2.VideoCapture(0)    #摄像头
camera.set(3, wCam)
camera.set(4, hCam)

n = 0
switch = 0
watch_where = '1'
l = []

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

message = '''點擊按鈕，根據上面手勢三秒內做一樣的動作 '''

text_box.insert('end', message)
panelB = Label(root, text = "跟著我比pose")  # initialize image panel
panelB.pack(side="top",padx=10, pady=10)

root.config(cursor="arrow")


btn = Button(root, text='點我出現題目', command=lambda:[open_img()])
btn.pack(fill="both", expand=True, padx=10, pady=10)

btn2 = Button(root, text='有沒有注視', command=lambda:[Watch_go()])
btn2.pack(fill="both", expand=True, padx=10, pady=10)

video_loop()


root.mainloop()
# 当一切都完成后，关闭摄像头并释放所占资源
camera.release()
cv2.destroyAllWindows()
