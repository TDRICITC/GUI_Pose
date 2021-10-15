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
import cv2
import time
import json                    
import requests
from PIL import Image
from io import BytesIO
from cvzone.HandTrackingModule import HandDetector

def video_loop():
    success, img = camera.read()  # 从摄像头读取照片
    hands, img = detector.findHands(img)
    if success:
        #cv2.waitKey(1)
        cv2image = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)#转换颜色从BGR到RGBA
        current_image = Image.fromarray(cv2image)#将图像转换成Image对象
        imgtk = ImageTk.PhotoImage(image=current_image)
        panel.imgtk = imgtk
        panel.config(image=imgtk)
        root.after(1, video_loop)


def recognition():
    btn['state'] = tk.DISABLED
    start = time.time()
    end = time.time()
    l = ["沒比動作喔"]
    i=0
    while end - start  < 3:
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
                end = time.time()
                i+=1
            except Exception:
                i+=1
                end = time.time()

    maxlabel = max(l,key=l.count)
    if n == maxlabel:
        answer = "相同"
    else:
        answer = "不相同"

    if answer =="不相同":
        hands, img = detector.findHands(img)
        cv2.imwrite('Error_pose/'+str(n)+'_{}.jpg'.format(time.time()), img)


    message ='''
    
    你的答案是:''' + str(maxlabel) + '''
    與題目:'''+ answer +'''
    總共辨識了:''' + str(i)+''' 張
    
     '''
    text_box.delete("1.0", "end") 
    text_box.insert('end', message)

    btn['state'] = tk.NORMAL

def recognition_go():
    threading.Thread(target=recognition).start()

def open_img():
    global n
    n = random.randrange(1,5,1)
    img = Image.open(str(n)+".jpg")
    img = img.resize((250, 250), Image.ANTIALIAS)
    img = ImageTk.PhotoImage(img)
    
    #panelB = Label(root, image=img)
    panelB.pack(padx=10, pady=10)
    panelB.config(image=img)
    panelB.image = img
    panelB.pack()
    
detector = HandDetector(detectionCon=0.7, maxHands=2)
url = 'http://34.80.31.212/tdri/api/vision/analyze_async?return_features=pose'
wCam, hCam = 640, 480
camera = cv2.VideoCapture(0)    #摄像头
camera.set(3, wCam)
camera.set(4, hCam)

n = 0

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


btn = Button(root, text='點我出現題目', command=lambda:[open_img(), recognition_go()])

btn.pack(fill="both", expand=True, padx=10, pady=10)

video_loop()
root.mainloop()
# 当一切都完成后，关闭摄像头并释放所占资源
camera.release()
cv2.destroyAllWindows()
