#!/usr/bin/env python
# -*- coding: utf-8 -*-
import CMDcontrol
import rospy
import tf
import time
import threading
import numpy as np
import math
from math import sqrt
from geometry_msgs.msg import PoseWithCovarianceStamped
from ar_track_alvar_msgs.msg import AlvarMarkers
from ar_track_alvar_msgs.msg import AlvarMarker
from kickBallOnly import kick_ball
from startDoorOnly import start_door


class TagConverter():
    def __init__(self):
        self.sub = rospy.Subscriber('/ar_pose_marker', AlvarMarkers, self.sub_cb)
        self.markers = []

    def sub_cb(self, msg):
        self.markers = []
        time_sec = msg.header.stamp.secs
        for marker in msg.markers:
            pos = marker.pose.pose.position
            quat = marker.pose.pose.orientation

            # print(marker)

            rpy = tf.transformations.euler_from_quaternion([quat.x, quat.y, quat.z, quat.w])
            rpy_arc = [0, 0, 0]
            for i in range(len(rpy)):
                rpy_arc[i] = rpy[i] / math.pi * 180
            
            # print(rpy_arc)
            # print("poseX:", pos.x, "poseY:", pos.y, "poseZ:", pos.z)
            #print("poseX--poseY--rpy_y:", pos.x, ",", pos.y, ",",rpy_arc[2])       # 测试标点

            self.markers.append([marker.id, pos.x, pos.y, rpy_arc[2], time_sec])

    def get_markers(self):
        return self.markers

    def get_nearest_marker(self):
        '''
        返回最小id二维码
        '''
        min_id = 999
        min_idx = 0
        markers = []
        for i in range(50):
            time.sleep(0.01)
            markers += self.markers
        
        for index, m in enumerate(markers):
            if m[0] < min_id:
                min_idx = index
                min_id = m[0]
        if min_id == 999:
            return []
        else:
            return markers[min_idx]

def thread_move_action():
    CMDcontrol.CMD_transfer()


def action(act_name):
    print(f'执行动作: {act_name}')
    time.sleep(1)
    CMDcontrol.action_append(act_name) 


def init_action_thread():
    th2 = threading.Thread(target=thread_move_action)
    th2.setDaemon(True)
    th2.start()

def stand(n=1):
    for _ in range(n):
        action('Stand')
        time.sleep(1)

def turn_left(n=1):
    for _ in range(n):
        action('turn001L')
        time.sleep(1)

def turn_right(n=1):
    for _ in range(n):
        action('turn001R')
        time.sleep(1)

def turn_left03(n=1):
    for _ in range(n):
        action('turn003L')
        time.sleep(1)

def turn_right03(n=1):
    for _ in range(n):
        action('turn003R')
        time.sleep(1)

def turn_left04(n=1):
    for _ in range(n):
        action('turn004L')
        time.sleep(1)

def turn_right04(n=1):
    for _ in range(n):
        action('turn004R')
        time.sleep(1)

def walk_slow00(n=1):
    for _ in range(n):
        action('Forwalk00')
        time.sleep(1)

def walk_slow(n=1):
    for _ in range(n):
        action('Forwalk01')
        # time.sleep(1)

def walk_fast(n=1):
    for _ in range(n):
        action('Forwalk02')
        # time.sleep(1)

def Back2Run(n=1):
    for _ in range(n):
        action('Back2Run')
        # time.sleep(1)

def turn_right10(n=1):
    for _ in range(n):
        action('turn010R')
        # time.sleep(2)

def UpBridge2(n=1):
    for _ in range(n):
        action('UpBridge2')
        time.sleep(1)

def turn_once(dist, angle, side_threshold=0.1):
    dist_side = dist * math.sin(abs(angle)*(math.pi/180))
    is_turn_done = False
    # action('Stand')
    if (abs(angle) > 7) and (dist > 0.03):
        if dist_side > side_threshold:
            action('Left02move') if angle < 0 else action('Right02move')
        else:
            action('turn001L') if angle < 0 else action('turn001R')
    else:
        is_turn_done = True
    return is_turn_done

def turn_once_fast(dist, angle, side_threshold=0.1):
    dist_side = dist * math.sin(abs(angle)*(math.pi/180))
    is_turn_done = False

    if (abs(angle) > 7) and (dist > 0.03):
        if dist_side > side_threshold:
            if dist_side < 0.05:
                action('Left02move') if angle < 0 else action('Right02move')
            else:
                action('Left3move') if angle < 0 else action('Right3move')
        else:
            action('turn001L') if angle < 0 else action('turn001R')
    else:
        is_turn_done = True
    return is_turn_done

def turn_once_corner(dist, angle, side_threshold=0.1):
    dist_side = dist * math.sin(abs(angle)*(math.pi/180))
    is_turn_done = False 
    
    if (abs(angle) > 8) and (dist > 0.03):
        if dist_side > side_threshold:
            action('Left02move') if angle < 0 else action('Right02move')
        else:
            if angle < 0:
                if -15 < angle < 0:
                    action('turn001L')
                if -30 < angle < -15:
                    action('turn003L')
                if angle < -30:
                    action('turn004L')
            if angle > 0:
                if 0 < angle < 15:
                    action('turn001R') 
                if 15 < angle < 30:
                    action('turn003R') 
                if angle > 30:
                    action('turn004R') 
    else:
        is_turn_done = True
    return is_turn_done
            

def turn_and_walk(dist, angle, side_threshold=0.1):
    is_turn_done = turn_once(dist, angle, side_threshold=side_threshold)
    if is_turn_done:
        walk_slow()


def turn_and_walk_corner(dist, angle):
    is_turn_done = turn_once_corner(dist, angle)
    if is_turn_done:
        walk_slow()
        

def turn_to_tag(dis_x,dis_y,theta,x_offset=0,y_offset=0,theta_offset=-90,x_threshold=0.09,y_threshold=0.015,theta_threshold=4):
    is_turn_done = False
    
    x_error = dis_x-x_offset
    y_error = dis_y-y_offset
    theta_error = theta-theta_offset
    print("theta:",theta,"theta_offset",theta_offset)
    print("x_error:",x_error,"y_error:",y_error,"theta_error:",theta_error)


    if (x_error<x_threshold-0.03):
        print("2后退")
        action("Back2Run")

    elif (y_error<-y_threshold-0.10):
        print("1右移动  ")
        action("Right02move")
    elif (y_error>y_threshold+0.10):
        print("1左移动 ")
        action("Left02move")

    elif (theta_error<-theta_threshold):
        print("1右转")
        action("turn001R")
    elif (theta_error>theta_threshold):
        print("1左转")
        action("turn001L")
    
    elif (y_error<-y_threshold):
        print("2右移动  ")
        action("Right02move")
    elif (y_error>y_threshold):
        print("2左移动 ")
        action("Left02move")
    
    elif (x_error>x_threshold+0.10):
        print("1前进")
        action("Forwalk01")


    elif (theta_error<-theta_threshold):
        print("2右转")
        action("turn001R")
    elif (theta_error>theta_threshold):
        print("2左转")
        action("turn001L")


    elif (x_error>x_threshold+0.06):
        print("2前进")
        action("Forwalk01")
    elif (x_error>x_threshold):
        print("2前进")
        action("Forwalk00")

    else:
        print("turn to tag ok")
        print("dis_x**:",dis_x,"dis_y**:",dis_y,"theta**:",theta)
        # time.sleep(5)
        is_turn_done = True

    return is_turn_done

def main():
    try:
        rospy.init_node('ar_tag_tracker')
        tag = TagConverter()
        
        print('Start action thread ...')
        init_action_thread()
        time.sleep(1)

        stage = 'start_door' # 第一关开始

        marker_review = 0

        while not rospy.is_shutdown():
            time.sleep(0.1)
            
            if(stage == 'start_door'):
                time.sleep(1)
                is_door_open = start_door(CMDcontrol)
                if(is_door_open == True):
                    stage = 'stage_one'
                else:
                    stage = 'start_door'

            marker = tag.get_nearest_marker() # id x y yaw

            # 没看到二维码的处理
            if len(marker) == 0:
                print('No marker found ! Stop? ',stage)
                # time.sleep(5) # fftest

                if (stage == 'stage_one' and marker_review < 3):
                    action('Back2Run')

                if stage == 'bridge_start':
                    print('过桥开始，没看到二维码')
                    action('Back2Run')

                if stage == 'bridge_end':
                    print('过桥结束，没看到二维码')
                    action('Back2Run')

                if stage == 'corner_turn':
                    print('看不到7，再右转一次，或者 需要后退？？')
                    for i in range(0):
                        action('forwardSlow0403')
                        time.sleep(1)
                    action('turn001L')
                    time.sleep(1)
                
                if stage == 'prepare_up_floor':
                    print('开始上台阶')
                    
                    action("Forwalk00")
                    # step1
                    # action('turn005R')
                    # action('turn001R')
                    # action('turn001R')
                    for i in range(1):
                        walk_slow()
                    action("turn001L")
                    action("Forwalk00")
                    
                    action('UpBridge2')
                    walk_slow00()
                    
                    # step2
                    action('UpBridge2')
                    walk_slow00()

                    # step3
                    action('UpBridge2')
                    time.sleep(1)
                    action('turn001L')
                    stage = 'kick_ball'
                
                if stage == 'kick_ball':
                    print('开始踢球------')
                    time.sleep(1)
                    kick_ball(CMDcontrol)

                continue

            robot_tag_x = marker[1]
            robot_tag_y = marker[2]
            tag_yaw = marker[3]
            time_tag = marker[4]

            print("tag ID:", marker[0], "timenow ", time.time()," ", time_tag)
            marker_review = marker[0]
            

            # 依据各个关卡执行对准后的动作
            # 快走阶段
            if marker[0] < 3 :
                
                if (marker[0] == 0) and (stage == 'stage_one' ):
                    print('看不到栏杆直接快走5555')
                    action('fastForward05')
                elif marker[0] == 1:
                    result = turn_to_tag(robot_tag_x,robot_tag_y,tag_yaw,0.0,-0.009835190726083295,-98.82063010064245)
                    if(result ==True):
                        print('快走5555')
                        action('fastForward05')
                else:
                    result = turn_to_tag(robot_tag_x,robot_tag_y,tag_yaw)
                    if(result ==True):
                        print('快走5555')
                        action('fastForward05')
            


            # 准备行走到窄桥起点，对齐二维码执行快走
            elif marker[0] == 3:
                stage = 'bridge_start'
                result = turn_to_tag(robot_tag_x,robot_tag_y,tag_yaw,0.09067939730036177,-0.0042162378165889886,-96.2819728571365)
                if (result == False):
                    continue

                print("dis_x:",robot_tag_x,"dis_y:",robot_tag_y,"theta:",tag_yaw)
                print('快走过桥')
                # time.sleep(5)
                action('fastForward05')

            # 窄桥中间
            elif marker[0] == 4:
                stage = 'bridge_middle'
                
                result = turn_to_tag(robot_tag_x,robot_tag_y,tag_yaw)
                if (result == False):
                    continue
                print('行走至独木桥中间')
                action('fastForward03')

            # 窄桥终点
            elif marker[0] == 5:
                stage = 'bridge_end'

                result = turn_to_tag(robot_tag_x,robot_tag_y,tag_yaw)
                if (result == False):
                    continue
                print('快走333至独木桥终点')

                action('fastForward03')
                time.sleep(3)


            elif marker[0] == 6:
                stage = 'corner_turn'
                result = turn_to_tag(robot_tag_x,robot_tag_y,tag_yaw)
                if (result == False):
                    continue
                
                print('行走至转向位，然后转向')
                
                action('Forwalk02')
                
                action('turn010R')
                action('Back2Run')
                action('turn010R')
                time.sleep(5)

                print("66666666666")
                # time.sleep(5)

            elif marker[0] == 7:
                
                stage = 'prepare_up_floor'
                result = turn_to_tag(robot_tag_x,robot_tag_y,tag_yaw,x_threshold=0)
                if (result == False):
                    continue
                
                # follow once 到楼梯起始位
                # 往前挪几步贴住台阶
                # 执行上台阶动作1、2、3
                print('准备上台阶')
                action('Forwalk02')
                
                
                # is_turn_done = turn_once_corner(marker[1], marker[2], side_threshold=0.04)
                # if is_turn_done:
                #     action('forwardSlow0403')

            else :
                print("marker id error !",marker[0])
                result = turn_to_tag(robot_tag_x,robot_tag_y,tag_yaw,0.1064763482548694,-0.018499921552315692,-93.2819728571365)
                if (result == False):
                    continue


    except rospy.ROSInterruptException:
        pass


if __name__ == '__main__':
    main()