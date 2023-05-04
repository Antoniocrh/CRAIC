""" 图片鼠标取值HSV value  camera输出显示 """

import numpy as np
import copy as cp
import cv2 
import math
import threading
import time

import matplotlib.pyplot as plt
import seaborn as sns

pic_FLAG = False

photo_path='./img_screenshot_30.04.2021.png'
picture_test = cv2.imread(photo_path)
img  = picture_test.copy()


max_record = [0,0,0]
min_record = [255,255,255]


color_range = {'yellow_door': [(30, 140, 80), (40, 240, 150)],
               'black_door': [(25, 25, 10), (110, 150, 24)],
               'yellow_hole': [(25, 90, 70), (40, 255, 255)],
               'blue_hole': [(65, 45, 40), (130, 255, 90)],
               'redball': [(0, 160, 40), (190, 255, 255)],
               'black': [(50, 30, 20), (130, 145, 50)],
               'black_hole': [(10, 10, 10), (180, 190, 60)],
               'black_gap': [(0, 0, 0), (180, 255, 80)],
               'red_floor': [(0, 55, 135), (10, 190, 190)],
               'red_floor1': [(0, 40, 115), (179, 185, 185)],
               'red_floor2': [(156, 43, 46), (180, 255, 255)],
               'chest_red_floor1': [(0, 100, 60), (20,200, 210)],
               'chest_red_floor2': [(110, 100, 60), (180,200, 210)],
               

               'Cred_floor4': [(140, 40, 45), (190, 210, 230)],
                'green_bridge': [(66 , 118 , 36), (90 , 191 , 47)],

                'black_line': [(50, 30, 20), (130, 220, 80)],
               }
#################################################初始化#########################################################

color_mask = "green_bridge"

rawimg = img.copy()

# Running = False
Running = True
debug = True
step = 0
# state_sel = None
state_sel = 'floor'
reset = 0
skip = 0
#初始化头部舵机角度

chest_ret = False     # 读取图像标志位
ret = False     # 读取图像标志位
ChestOrg_img = None  # 原始图像更新
HeadOrg_img = None  # 原始图像更新
HeadOrg_img = None

plt_h = []
plt_s = []
plt_v = []



# 新建窗口
cv2.namedWindow("robotPreviewH",cv2.WINDOW_NORMAL)
cv2.namedWindow("robotPreviewH_HSV",cv2.WINDOW_NORMAL)
cv2.namedWindow("colorMask",cv2.WINDOW_NORMAL)

cv2.resizeWindow("Camera", 640, 480)
cv2.resizeWindow("robotPreviewH", 640, 480)
cv2.resizeWindow("robotPreviewH_HSV", 640, 480)
cv2.resizeWindow("colorMask", 640, 480)





def hsv_max(aa,bb):
    cc=[bb[0],bb[1],bb[2]]
    if aa[0]>bb[0]:
        cc[0]=aa[0]
    if aa[1]>bb[1]:
        cc[1]=aa[1]
    if aa[2]>bb[2]:
        cc[2]=aa[2]
    return cc

def hsv_min(aa,bb):
    cc=[bb[0],bb[1],bb[2]]
    if aa[0]<bb[0]:
        cc[0]=aa[0]
    if aa[1]<bb[1]:
        cc[1]=aa[1]
    if aa[2]<bb[2]:
        cc[2]=aa[2]
    return cc

def onmouse(event, x, y, flags, param):   #标准鼠标交互函数
    global max_record,min_record
    hsvimg = cv2.cvtColor(rawimg, cv2.COLOR_BGR2HSV)
    if event==cv2.EVENT_MOUSEMOVE:      #当鼠标移动时
        if sampling_flag == True:
            xy_hsv = hsvimg[y,x]
            print(x,y,xy_hsv, "正在采集，w停止采集")           #显示鼠标所在像素的数值，注意像素表示方法和坐标位置的不同
            plt_h.append(xy_hsv[0])
            plt_s.append(xy_hsv[1])
            plt_v.append(xy_hsv[2])
            max_record = hsv_max(xy_hsv,max_record)
            min_record = hsv_min(xy_hsv,min_record)
        else:
            print(min_record,"min停止采集,w开始采集max",max_record)
            print("[(" + str(min_record[0]) + " , " + str(min_record[1]) + " , " + str(min_record[2]) + "), (" + str(max_record[0]) + " , " + str(max_record[1]) + " , " + str(max_record[2]) + ")]," )

# 创建鼠标事件的回调函数
cv2.setMouseCallback("robotPreviewH", onmouse)




num = 0
sampling_flag = False
while True:
    

    hsvimg = cv2.cvtColor(rawimg, cv2.COLOR_BGR2HSV)
    h,s,v = cv2.split(rawimg)


    
    frame_green = cv2.inRange(hsvimg, color_range[color_mask][0],color_range[color_mask][1])  # 对原图像和掩模(颜色的字典)进行位运算
    # opened = cv2.morphologyEx(frame_green, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))  # 开运算 去噪点
    # closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))  # 闭运算 封闭连接
    # closed = opened
    cv2.imshow("colorMask", frame_green)


    cv2.imshow("robotPreviewH_HSV",hsvimg)
    cv2.imshow("robotPreviewH",rawimg)
    k = cv2.waitKey(500)

    # 如果按了'ESC'键，则关闭面板
    if k == 27:
        break
    if k == ord('s'):
        num += 1
        name = 'photo_save' + str(num) + '.bmp'
        print(name)
        cv2.imwrite(name,camera_img) #保存图片
    if k == ord('w'):
        if sampling_flag == True:
            sampling_flag = False
            print("停止采集")


            
            sns.distplot(plt_h, bins = None, kde = False, hist_kws = {'color':'steelblue'}, label = 'h')
            sns.distplot(plt_s, bins = None, kde = False, hist_kws = {'color':'purple'}, label = 's')
            sns.distplot(plt_v, bins = None, kde = False, hist_kws = {'color':'darkgreen'}, label = 'v')
            plt.title('hsv')
            plt.legend()
            plt.show()


        else:
            sampling_flag = True
            print("开始采集")




