#!/usr/bin/env python3
# coding:utf-8

import numpy as np
import cv2
import math
import threading
import time
import datetime
import rospy
import hashlib

from image_converter import ImgConverter
from color_filter import color_filter

CMDcontrol = None

chest_r_width = 480
chest_r_height = 640
head_r_width = 640
head_r_height = 480

obs_rec = False
baf_rec = False
hole_rec = False
bridge_rec = False
door_rec = False
kick_ball_rec = False
floor_rec = False


img_debug = 0
action_DEBUG = False
box_debug = False
stream_pic = True
single_debug = 0
robot_IP = "192.168.123.163"

chest_ret = True     # 读取图像标志位
ret = False           # 读取图像标志位
ChestOrg_img = None   # 原始图像更新
HeadOrg_img = None    # 原始图像更新
ChestOrg_copy = None
HeadOrg_copy = None

sleep_time_s = 0.01
sleep_time_l = 0.05
real_test = 1
reset = 0


rgb_hole = [0,113,150]
rgb_hole_thred = 18
rgb_ball = [88,34,25]
rgb_ball_thred = 16

ros_view_debug = True


################################################读取图像线程#################################################

def get_img():
    global ChestOrg_img, HeadOrg_img, HeadOrg_img, chest_ret
    global ret

    image_reader_chest = ImgConverter()
    while True:
        chest_ret, ChestOrg_img = image_reader_chest.chest_image()
        time.sleep(0.05)


# 读取图像线程

th1 = threading.Thread(target=get_img)
th1.setDaemon(True)
th1.start()


#################################################################动作执行####################################

# def move_action():
#     global org_img
#     global step, level
#     global golf_angle_hole
#     global golf_angle_ball, golf_angle
#     global golf_dis, golf_dis_y
#     global golf_angle_flag
#     global golf_angle_start, golf_dis_start
#     global golf_ok
#     global golf_hole, golf_ball

#     # if real_test:
#     #     CMDcontrol.CMD_transfer()

# # 动作执行线程
# th2 = threading.Thread(target=move_action)
# th2.setDaemon(True)
# th2.start()


acted_name = ""
def action_append(act_name):
    global acted_name

    # print("please enter to continue...")
    # cv2.waitKey(0)

    if action_DEBUG == False:
        if act_name == "forwardSlow0403" and (acted_name == "Forwalk02RL" or acted_name == "Forwalk02L"):
            acted_name = "Forwalk02LR"
        elif act_name == "forwardSlow0403" and (acted_name == "Forwalk02LR" or acted_name == "Forwalk02R"):
            acted_name = "Forwalk02RL"
        elif act_name != "forwardSlow0403" and (acted_name == "Forwalk02LR" or acted_name == "Forwalk02R"):
            # CMDcontrol.action_list.append("Forwalk02RS")
            # acted_name = act_name
            print(act_name,"动作未执行 执行 Stand")
            acted_name = "Forwalk02RS"
        elif act_name != "forwardSlow0403" and (acted_name == "Forwalk02RL" or acted_name == "Forwalk02L"):
            # CMDcontrol.action_list.append("Forwalk02LS")
            # acted_name = act_name
            print(act_name,"动作未执行 执行 Stand")
            acted_name = "Forwalk02LS"
        elif act_name == "forwardSlow0403":
            acted_name = "Forwalk02R"
        else:
            acted_name = act_name

        
        m = hashlib.md5()
        name_encode = bytes(act_name,encoding='utf8')
        m.update(name_encode)
        acted_name = 'leju_' + m.hexdigest()
        print(acted_name)#fftest

        CMDcontrol.actionComplete = False
        if len(CMDcontrol.action_list) > 0:
            print("队列超过一个动作")
            CMDcontrol.action_list.append(acted_name)
        else:
            if single_debug:
                cv2.waitKey(0)
            CMDcontrol.action_list.append(acted_name)
        CMDcontrol.action_wait()
        time.sleep(1)

    else:
        print("-----------------------执行动作名：", act_name)
        time.sleep(2)






color_dist = {'red': {'Lower': np.array([0, 160, 100]), 'Upper': np.array([180, 255, 250])},
               'black_dir': {'Lower': np.array([0, 0, 10]), 'Upper': np.array([170, 170, 45])},
               'black_line': {'Lower': np.array([0, 0, 12]), 'Upper': np.array([169 , 155 , 65])},
               
               
              'ball_red': {'Lower': np.array([1 , 118 , 117]), 'Upper': np.array([7 , 184 , 149])},
              'blue_hole': {'Lower': np.array([105 , 99 , 141]), 'Upper': np.array([109 , 170 , 222])},
              
              }


def getAreaMaxContour2(contours, area=1):
    contour_area_max = 0
    area_max_contour = None
    for c in contours:
        contour_area_temp = math.fabs(cv2.contourArea(c))
        if contour_area_temp > contour_area_max:
            contour_area_max = contour_area_temp
            if contour_area_temp > area:  
                area_max_contour = c
    return area_max_contour




################################################第七关：踢球########################################

golf_angle_ball = 90
Chest_ball_angle = 90
hole_Angle = 45
golf_angle = 0
ball_x = 0
ball_y = 0
golf_angle_flag = False
golf_dis_start = True
golf_angle_start = False
golf_ok = False
hole_flag = False
Chest_ball_flag = False
Chest_golf_angle = 0

ball_dis_start = True
hole_angle_start = False

head_state = 0      # 90 ~ -90      左+90   右-90   

hole_x = 0
hole_y = 0

angle_dis_count = 0
picnum = 0
fast_run = True

def act_move():
    global step, state, reset, skip
    global hole_Angle,ball_hole
    global golf_angle_ball, golf_angle ,Chest_ball_angle ,Chest_golf_angle
    global ball_x, ball_y,Chest_ball_x, Chest_ball_y 
    global golf_angle_flag
    global golf_angle_start, golf_dis_start
    global golf_ok
    global hole_flag,Chest_ball_flag
    global ball_dis_start,hole_angle_start
    global head_state, angle_dis_count ,fast_run
    ball_hole_angle_ok = False


        # 由脚底到红球延伸出一条射线，依据球洞与该射线的关系，调整机器人位置
        # ball_hole_local()

    if True:
        if step == 0:   # 发现球，发现球洞，记录球与球洞的相对位置
            # print("看黑线调整居中")
            if Chest_ball_flag == True:   # 前进到球跟前
                if fast_run:
                    if Chest_ball_y <= 210:  # 340
                        print("1870L 快走前进 fastForward04 ",Chest_ball_y)
                        # action_append("forwardSlow0403")
                        # action_append("forwardSlow0403")
                        action_append("Forwalk02")
                        # head_angle_dis()    # headfftest
                    elif Chest_ball_y <= 290:  # 340
                        print("1902L 快走前进 fastForward03 ",Chest_ball_y)
                        action_append("Forwalk02")
                        # head_angle_dis()    # headfftest
                    else:
                        print("1902L 快走完成",Chest_ball_y)
                        fast_run = False

                else:
                    if Chest_ball_y <350:   # 390
                        # X
                        if Chest_ball_x < 140:  # 240 - 100
                            print("159L Chest_ball_x < 180 左侧移 ",Chest_ball_x)
                            action_append("Left3move")
                        elif Chest_ball_x > 340:    # 240 + 100
                            print("161L Chest_ball_x > 300 右侧移 ",Chest_ball_x)
                            action_append("Right3move")
                        else:
                            print("168L 前挪一点点 1111111 ",Chest_ball_y)
                            # action_appendf289z("Forwalk01")
                            action_append("forwardSlow0403")
                    else: # Chest_ball_y>360
                        print("goto step1  ",Chest_ball_y)
                        step = 1
            else:
                print("183L 未发现红球  左右旋转头部摄像头 寻找红球")
                print("238L 前进 fastForward03")
                action_append("Forwalk02") # ffetst
                # 目前假设红球在正前方，能看到
                
                # if head_state == 0:
                #     print("头右转(-60)寻找球")
                #     head_state = -60
                # elif head_state == -60:
                #     print("头由右转变为左转(+60)寻找球")
                #     head_state = 60
                # elif head_state == 60:
                #     print("头部 恢复0 向前迈进")
                
        elif step == 1:     # 看球调整位置   逐步前进调整至看球洞
            if Chest_ball_y <= 350:
                print("174L 前挪一点点 Forwalk00 < 380 ",Chest_ball_y)
                action_append("Forwalk00")
            elif Chest_ball_y > 480:
                print("1903L 后一步 Back2Run > 480",Chest_ball_y)
                action_append("Back2Run")
            elif 350< Chest_ball_y <= 480:
                
                if hole_flag == True:
                    if head_state == -60:
                        print("头右看，看到球洞")
                        step = 2
                        # print("172L 头恢复0 向右平移")
                        # head_state = 0
                    elif head_state == 60:
                        print("头左看，看到球洞")
                        step = 3
                        # print("172L 头恢复0 向左平移")
                        # head_state = 0
                    elif head_state == 0:     # 头前看 看到球洞
                        print("270L step4")
                        step = 4
                else:
                    print("273error 左右旋转头 寻找球洞 ")
                    # 目前假设球洞在前方，head能看到
                
                    # if head_state == 0:
                    #     print("头右转(-60)寻找球")
                    #     head_state = -60
                    # elif head_state == -60:
                    #     print("头由右转变为左转(+60)寻找球")
                    #     head_state = 60
                    # elif head_state == 60:
                    #     print("头部 恢复0 向前迈进")
      


        elif step == 2:
            # 头右看，看到球洞
            print("22222222222找红球与球洞")
            if Chest_ball_y < 160:
                print("174L 一大步前进")

            elif Chest_ball_y < 360:  
                print("177L 后挪一点点")
            elif 160< Chest_ball_y < 320:
                print("找到了在左边跳第4步，找到了在右边跳第3步")

                if hole_flag == True:
                    if head_state == -60:
                        print("头右看，看到球")
                        step = 3
                        # print("172L 头恢复0 向右平移")
                        # head_state = 0
                    elif head_state == 60:
                        print("头左看，看到球")
                        step = 4
                        # print("172L 头恢复0 向左平移")
                        # head_state = 0
                    elif head_state == 0:     # 头前看 看到球洞
                        step = 1
                else:
                    print("左右旋转头 寻找球洞")
                    # 目前假设球洞在前方，head能看到
                
                    if head_state == 0:
                        print("头右转(-60)寻找球")
                        head_state = -60
                    elif head_state == -60:
                        print("头由右转变为左转(+60)寻找球")
                        head_state = 60
                    elif head_state == 60:
                        print("头部 恢复0 向前迈进")

        elif step == 3:
            # 头左看，看到球洞
            print("33333333333左侧移")
            if Chest_ball_y > 280:
                print("后挪一点点")
            elif Chest_ball_y < 150:
                print("前挪一点点")
            elif Chest_ball_x < 450:
                print("左侧移")
            
            if hole_flag == False:
                print("右转")
            else:
                step = 1
                ball_dis_start = True
                hole_angle_start = False
            # 完成左侧移后 右转
            # 找球洞
        
        



        elif step == 4:  # 粗略调整朝向   球与球洞大致在一条线
            # print("调整红球在左脚正前方不远处，看球洞的位置调整")
            if ball_dis_start:
                if Chest_ball_x <= 200:
                    if 240 - Chest_ball_x > 40:
                        print("373L4 需要左侧移 Left3move", Chest_ball_x)
                        action_append("Left3move")
                    else:
                        print("376L4 需要左侧移 Left02move", Chest_ball_x)
                        action_append("Left02move")
                    angle_dis_count = 0
                elif Chest_ball_x > 280:
                    if Chest_ball_x - 240 > 40:
                        print("359L4 需要右侧移 Right3move", Chest_ball_x)
                        action_append("Right3move")
                    else:
                        print("384L4 需要右侧移 Right02move", Chest_ball_x)
                        action_append("Right02move")
                    angle_dis_count = 0
                else:
                    print("388L4 Chest_ball_y---位置ok")
                    ball_dis_start = False
                    hole_angle_start = True
            if hole_angle_start:
                if hole_Angle <=0:
                    # angle
                    if hole_Angle > -86:
                        if hole_Angle >= -82:
                            if Chest_ball_y > 480:
                                print("392L4 需要后挪一点 Back2Run ",Chest_ball_y)
                                action_append("Back2Run")
                                angle_dis_count = 0
                            elif Chest_ball_y < 350:
                                print("395L4 需要前挪一点 Forwalk00",Chest_ball_y)
                                action_append("Forwalk00")
                                angle_dis_count = 0

                            print("381L4 大左转一下  turn004L ", hole_Angle)
                            action_append("turn004L")
                            angle_dis_count = 0
                        else:
                            if Chest_ball_y > 485:
                                print("386L4 需要后挪一点 Back1Run ",Chest_ball_y)
                                action_append("Back1Run")
                                angle_dis_count = 0
                            elif Chest_ball_y < 350:
                                print("427L4 需要前挪一点 Forwalk00 ",Chest_ball_y)
                                action_append("Forwalk00")
                                angle_dis_count = 0
                                
                            print("397L4 左转一下  turn001L ", hole_Angle)
                            action_append("turn001L")
                    else:
                        print("401L4 hole_Angle---角度ok")
                        angle_dis_count = angle_dis_count + 1
                        ball_dis_start = True
                        hole_angle_start = False

                    # ball_dis_start = True
                    # hole_angle_start = False
                if hole_Angle >0:
                    # angle
                    if hole_Angle < 86:
                        if hole_Angle <= 82:
                            if Chest_ball_y > 460:
                                print("409L4 需要后挪一点 Back2Run ",Chest_ball_y)
                                action_append("Back2Run")
                                angle_dis_count = 0
                            elif Chest_ball_y < 410:
                                print("427L4 需要前挪一点 Forwalk00 ",Chest_ball_y)
                                action_append("Forwalk00")
                                angle_dis_count = 0

                            print("250L4 大右转一下 turn004R ", hole_Angle)
                            action_append("turn004R")
                        else:
                            if Chest_ball_y > 460:
                                print("421L4 需要后挪一点 Back1Run ",Chest_ball_y)
                                action_append("Back1Run")
                                angle_dis_count = 0
                            elif Chest_ball_y < 400:
                                print("427L4 需要前挪一点 Forwalk00 ",Chest_ball_y)
                                action_append("Forwalk00")
                                angle_dis_count = 0

                            print("352L4 右转一下 turn001R ", hole_Angle)
                            action_append("turn001R")
                    else:
                        print("417L4 hole_Angle---角度OK")         
                        angle_dis_count = angle_dis_count + 1
                        ball_dis_start = True
                        hole_angle_start = False

                    # ball_dis_start = True
                    # hole_angle_start = False

                if angle_dis_count > 3:
                    angle_dis_count = 0
                    print("step step 5555")
                    step = 5
                    

        elif step == 5:  # 调整 球与球洞在一条直线    球范围  230<Chest_ball_y<250
            # print("55555 球与球洞都在")
            # print("调整红球在左脚正前方不远处，看球洞的位置调整")
            if ball_dis_start:  # 390<y<450  230<x<250
                if Chest_ball_x < 220:
                    # if 240 - Chest_ball_x > 40:
                    #     print("443L 需要左侧移 Left02move")
                    #     action_append("Left02move")
                    # else:
                    print("446L 需要左侧移 Left1move", Chest_ball_x)
                    action_append("Left1move")
                    angle_dis_count = 0
                elif Chest_ball_x > 260:
                    # if Chest_ball_x - 240 > 40:
                    #     print("451L 需要右侧移 Right02move")
                    #     action_append("Right02move")
                    # else:
                    print("454L 需要右侧移 Right1move", Chest_ball_x)
                    action_append("Right1move")
                    angle_dis_count = 0
                else:
                    print("340L Chest_ball_y---位置ok")
                    ball_dis_start = False
                    hole_angle_start = True
            if hole_angle_start:
                if hole_Angle <0:
                    # angle
                    if hole_Angle > -87:
                        # y
                        if Chest_ball_y > 460:
                            print("475L 需要后挪一点 Back1Run ",Chest_ball_y)
                            action_append("Back1Run")
                            angle_dis_count = 0
                        elif Chest_ball_y < 410:
                            print("368L 需要前挪一点 Forwalk00",Chest_ball_y)
                            action_append("Forwalk00")
                            angle_dis_count = 0

                        if hole_Angle >= -82:
                            print("465L 大左转一下  turn001L ", hole_Angle)
                            action_append("turn001L")
                        else:
                            print("468L 左转一下  turn001L ", hole_Angle)
                            action_append("turn001L")
                    else:
                        print("471L hole_Angle---角度ok")
                        angle_dis_count = angle_dis_count + 1

                    ball_dis_start = True
                    hole_angle_start = False
                if hole_Angle >0:
                    # angle
                    if hole_Angle < 87:
                        # y
                        if Chest_ball_y > 460:
                            print("475L 需要后挪一点 Back1Run ",Chest_ball_y)
                            action_append("Back1Run")
                            angle_dis_count = 0
                        elif Chest_ball_y < 410:
                            print("368L 需要前挪一点 Forwalk00 ",Chest_ball_y)
                            action_append("Forwalk00")
                            angle_dis_count = 0

                        if hole_Angle <= 82:
                            print("479L 大右转一下 turn001R ", hole_Angle)
                            action_append("turn001R")
                        else:
                            print("482L 右转一下 turn001R ", hole_Angle)
                            action_append("turn001R")
                    else:
                        print("485L hole_Angle---角度OK")               
                        angle_dis_count = angle_dis_count + 1

                    ball_dis_start = True
                    hole_angle_start = False

                if angle_dis_count > 2:
                    angle_dis_count = 0
                    step = 6


        elif step == 6:
            # print("666")
            if Chest_ball_angle > 88 and hole_Angle > 88:
                ball_hole_angle_ok = True
            if Chest_ball_angle < -88 and hole_Angle > 88:
                ball_hole_angle_ok = True
            if Chest_ball_angle < -88 and hole_Angle < -88:
                ball_hole_angle_ok = True
            if Chest_ball_angle > 88 and hole_Angle < -88:
                ball_hole_angle_ok = True

            if Chest_ball_angle > 86 and hole_Angle > 86 and ball_hole_angle_ok == False:
                print("391L 右转一点点 turn001R")
                action_append("turn001R")
            elif Chest_ball_angle < -86 and hole_Angle < -86 and ball_hole_angle_ok == False:
                print("393L 左转一点点 turn001L")
                action_append("turn001L")
            elif Chest_ball_y <= 430:
                print("289L 向前挪动一点点 Forwalk00 ",Chest_ball_y)
                action_append("Forwalk00")
            else:
                print("next step")
                step = 7

        elif step == 7:
            if Chest_ball_x > 200:  # 210
                print("410L 向右移动 Right1move")
                action_append("Right1move")
            elif Chest_ball_x < 180:
                print("412L 向左移动 Left1move")
                action_append("Left1move")
            elif Chest_ball_y < 440:
                print("289L 向前挪动一点点 Forwalk00 ",Chest_ball_y)
                action_append("Forwalk00")
            elif Chest_ball_y > 470:
                print("2244L 向后挪动一点点 Back0Run ",Chest_ball_y)
                action_append("Back0Run")
            else:
                print("414L 踢球踢球 LfootShot " ,Chest_ball_y)
                # action_append('turn001R')
                time.sleep(2)
                action_append('Forwalk00')
                action_append('Forwalk00')
                # action_append('Forwalk00')
                # action_append('turn001R')
                # action_append('turn001R')
                action_append("LfootShot")
                step = 8
                print("完成 77777")
                action_append("Stand")
                action_append("Wanyao20")
                action_append("Stand")


def kick_ball(cmd_ctrl):
    global state, state_sel, step, reset, skip
    global hole_Angle
    global golf_angle_ball, golf_angle ,Chest_ball_angle, Chest_golf_angle
    global ball_x, ball_y ,Chest_ball_x, Chest_ball_y 
    global hole_flag ,Chest_ball_flag
    global ChestOrg_img
    global picnum,img_debug
    global CMDcontrol
    CMDcontrol = cmd_ctrl

    # 初始化
    sum_contours = np.array([[[0, 0]], [[0, 1]], [[1, 1]], [[1, 0]]])
    step = 0
    state = 7

    while state == 7:
        if 0<=step < 8: #踢球的七步
            
            ChestOrg = ChestOrg_img.copy()
            ChestOrg=np.rot90(ChestOrg)
            
            Hole_OrgFrame = ChestOrg.copy()
            Ball_OrgFrame = ChestOrg.copy()

            img_h, img_w = Hole_OrgFrame.shape[:2]

            # 把上中心点和下中心点200改为640/2  fftest
            bottom_center = (int(240), int(img_h))  #图像底中点
            top_center = (int(240), int(0))     #图像顶中点
            # bottom_center = (int(640/2), int(img_h))  #图像底中点
            # top_center = (int(640/2), int(0))     #图像顶中点

            # 开始处理图像
            Hole_hsv = cv2.cvtColor(Hole_OrgFrame, cv2.COLOR_BGR2HSV)
            Hole_hsv= cv2.GaussianBlur(Hole_hsv, (3, 3), 0)

            Hole_Imask = cv2.inRange(Hole_hsv, color_dist['blue_hole']['Lower'], color_dist['blue_hole']['Upper'])
            Hole_Imask = cv2.erode(Hole_Imask, None, iterations=1)
            Hole_Imask = cv2.dilate(Hole_Imask, np.ones((3, 3), np.uint8), iterations=3)

            
            # cv2.imshow('hole_mask', Hole_Imask)      # hole mask
            # print('Press a key to continue:')
            # cv2.waitKey(0)


            # 初始化
            hole_center = [0, 0]
            Chest_ball_center = [0, 0]


          # chest 球洞处理
            hole_x = 0
            hole_y = 0

            cnts, hierachy = cv2.findContours(Hole_Imask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)    #**获得图片轮廓值  #遍历图像层级关系
            # cnts = color_filter(Hole_OrgFrame, rgb_hole, thred=rgb_hole_thred)

            # print(cnts)
            # *取得一个球洞的轮廓*
            for i in range(0, len(cnts)):               # 初始化sum_contours，使其等于其中一个c，便于之后拼接的格式统一
                area = cv2.contourArea(cnts[i])         #计算轮廓面积
                # print("area : ",area)
                if img_debug:
                    cv2.putText(Hole_OrgFrame, "area:" + str(area),(10, Hole_OrgFrame.shape[0] - 55), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 2)
                    cv2.waitKey(1)
                if 640 * 480 * 0.0005 < area < 640 * 480 * 0.45:  # 去掉很小的干扰轮廓以及最大的图像边界
                    # cv2.drawContours(Hole_OrgFrame, cnts, -1, (0, 255, 0), 3)
                    sum_contours = cnts[i]
                    break
                else:
                    # cv2.drawContours(Hole_OrgFrame, cnts, -1, (0, 0, 255), 3)
                    continue
            for c in cnts:
                area = cv2.contourArea(c)                                       #计算轮廓面积
                if 640 * 480 * 0.0005 < area < 640 * 480 * 0.45:
                    sum_contours = np.concatenate((sum_contours, c), axis=0)    #数组拼接
                    # cv2.drawContours(Hole_OrgFrame, c, -1, (0, 255, 0), 3)
                else:
                    # cv2.drawContours(Hole_OrgFrame, c, -1, (0, 0, 255), 3)
                    continue
            sum_area = cv2.contourArea(sum_contours)    #计算轮廓面积
            if sum_area > 3:
                cnt_large = sum_contours
            else:
                cnt_large = None

            if cnt_large is not None:
                hole_flag = True
                (hole_x, hole_y), radius = cv2.minEnclosingCircle(cnt_large)    #最小内接圆形
                hole_center = (int(hole_x), int(hole_y))
                radius = int(radius)
                # cv2.circle(Hole_OrgFrame, hole_center, radius, (100, 200, 30), 2)
                # ellipse = cv2.fitEllipse(cnt_large)
                # cv2.ellipse(OrgFrame,ellipse,(255,255,0),2)
                # cv2.line(Hole_OrgFrame, hole_center, bottom_center, (0, 0, 100), 2)
                if (hole_center[0] - bottom_center[0]) == 0:
                    hole_Angle = 90
                else:
                    # hole_Angle  (y1-y0)/(x1-x0)
                    hole_Angle = - math.atan((hole_center[1] - bottom_center[1]) / (hole_center[0] - bottom_center[0])) * 180.0 / math.pi
            else:
                hole_flag = False

            if img_debug:
                cv2.putText(Hole_OrgFrame, "step:" + str(step),
                            (10, Hole_OrgFrame.shape[0] - 35), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 2)
                cv2.putText(Hole_OrgFrame, "hole_angle:" + str(hole_Angle),
                            (10, Hole_OrgFrame.shape[0] - 115), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 2)
                cv2.putText(Hole_OrgFrame, "hole_x:" + str(hole_x),
                            (10, Hole_OrgFrame.shape[0] - 75), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 2)
                cv2.putText(Hole_OrgFrame, "hole_y:" + str(hole_y),
                            (220, Hole_OrgFrame.shape[0] - 75), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 2)
                cv2.putText(Hole_OrgFrame, "hole_flag:" + str(hole_flag),
                            (10, Hole_OrgFrame.shape[0] - 95), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 2)

                cv2.imshow("Hole_OrgFrame", Hole_OrgFrame)
                cv2.waitKey(10)


          # chest 红球处理
            Chest_ball_x = 0
            Chest_ball_y = 0


            Chest_Ball_hsv = cv2.cvtColor(Ball_OrgFrame, cv2.COLOR_BGR2HSV)
            Chest_Ball_hsv = cv2.GaussianBlur(Chest_Ball_hsv, (3, 3), 0)
            
            Chest_Ball_Imask = cv2.inRange(Chest_Ball_hsv, color_dist['ball_red']['Lower'], color_dist['ball_red']['Upper'])
            # Chest_Ball_Imask = cv2.erode(Chest_Ball_Imask, None, iterations=2)
            Chest_Ball_Imask = cv2.dilate(Chest_Ball_Imask, np.ones((3, 3), np.uint8), iterations=2)
            
            # cv2.imshow('ball_mask', Chest_Ball_Imask)    # ball mask
            # print('Press a key to continue:')
            # cv2.waitKey(0)

            cnts2, hierachy2 = cv2.findContours(Chest_Ball_Imask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            # cnts2 = color_filter(Ball_OrgFrame, rgb_ball, thred=rgb_ball_thred)

            if cnts2 is not None:
                cnt_large3 = getAreaMaxContour2(cnts2, 10)
            else:
                print("1135L cnt_large is None")
                continue
            
            # 圆球轮廓  计算角度 Chest_ball_angle
            if cnt_large3 is not None:
                Chest_ball_flag = True
                (Chest_circle_x, Chest_circle_y), Chest_radius = cv2.minEnclosingCircle(cnt_large3)
                Chest_ball_center = (int(Chest_circle_x), int(Chest_circle_y))
                Chest_radius = int(Chest_radius)
                # cv2.circle(Ball_OrgFrame, Chest_ball_center, Chest_radius, (100, 200, 20), 2)
                # cv2.line(Ball_OrgFrame, Chest_ball_center, top_center, (0, 100, 0), 2)
                # ellipse = cv2.fitEllipse(cnt_large)
                # cv2.ellipse(OrgFrame,ellipse,(255,255,0),2)
                if (Chest_ball_center[0] - top_center[0]) == 0:
                    Chest_ball_angle = 90
                else:
                    # *Chest_ball_angle*  (y1-y0)/(x1-x0)
                    Chest_ball_angle = - math.atan((Chest_ball_center[1] - top_center[1]) / (Chest_ball_center[0] - top_center[0])) * 180.0 / math.pi
                Chest_ball_x = int(Chest_circle_x)   # *ball_x*
                Chest_ball_y = int(Chest_circle_y) # *ball_y*
            else:
                Chest_ball_flag = False
                Chest_ball_y = 0

        if ros_view_debug:
            image_debug = cv2.circle(Ball_OrgFrame, (int(hole_x), int(hole_y)), 10, (255,0,0), 2)
            image_debug = cv2.circle(image_debug, (Chest_ball_x, Chest_ball_y), 10, (0,0,255), 2)
            cv2.imwrite('./debug.jpg', Ball_OrgFrame)
            cv2.imwrite('./raw_debug.jpg', ChestOrg)
            act_move()
        else:
            act_move()



# 踢球进洞
if __name__ == '__main__':
    import CMDcontrol
    
    def thread_move_action():
        CMDcontrol.CMD_transfer()

    th2 = threading.Thread(target=thread_move_action)
    th2.setDaemon(True)
    th2.start()

    rospy.init_node('kickballnodes')
    time.sleep(3)
    action_append("Stand")
    kick_ball(CMDcontrol)
