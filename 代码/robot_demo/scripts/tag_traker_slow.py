#!/usr/bin/env python
# -*- coding: utf-8 -*-
import CMDcontrol
import rospy
import tf
import time
import threading
import numpy as np
from math import sqrt
from geometry_msgs.msg import PoseWithCovarianceStamped
from ar_track_alvar_msgs.msg import AlvarMarkers
from ar_track_alvar_msgs.msg import AlvarMarker
from kickBallOnly import kick_ball



def angle_between(v1, v2):
    cosTh = np.dot(v1, v2)
    sinTh = np.cross(v1, v2)
    angle = np.rad2deg(np.arctan2(sinTh, cosTh))[2]
    return angle

class TagConverter():
    def __init__(self):
        self.p_0 = np.array([-0.1429473853758271, -0.004343588010841607, 0.1392410096834090876])
        self.p_1 = np.array([-0.043167954694022376, -0.00023977932710763676, 0.2964736797698838])
        self.sub = rospy.Subscriber('/ar_pose_marker', AlvarMarkers, self.sub_cb)
        self.markers = []
        self.vd = self.p_1 - self.p_0

    def sub_cb(self, msg):
        self.markers = []
        for marker in msg.markers:
            pos = marker.pose.pose.position
            p_l = np.array([pos.x, pos.y, pos.z])
            v_pl = np.array([pos.x, pos.y, pos.z]) - self.p_0
            dist = sqrt(
                (p_l[0] - self.p_0[0])**2 + \
                (p_l[1] - self.p_0[1])**2 + \
                (p_l[2] - self.p_0[2])**2
            )
            angle = angle_between(self.vd, v_pl)
            self.markers.append([marker.id, dist, angle])

    def get_markers(self):
        return self.markers

def thread_move_action():
    CMDcontrol.CMD_transfer()


def action(act_name):
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
        time.sleep(1)

def walk_fast(n=1):
    for _ in range(n):
        action('Forwalk02')
        time.sleep(1)

def Back2Run(n=1):
    for _ in range(n):
        action('Back2Run')
        time.sleep(1)

def turn_right10(n=1):
    for _ in range(n):
        action('turn010R')
        time.sleep(2)

def UpBridge2(n=1):
    for _ in range(n):
        action('UpBridge2')
        time.sleep(5)

def turn_and_walk(dist, angle):
    # turn
    if (abs(angle) > 10) and (dist > 0.03):
        if angle < -10 and angle > -20:
            turn_left()
        if angle > 10 and angle < 20:
            turn_right()
        if angle < -20 and angle > -30:
            turn_left03()
        if angle > 20 and angle < 30:
            turn_right03()
        if angle < -30:
            turn_left04()
        if angle > 30:
            turn_right04()

    else:
        walk_slow()

    time.sleep(2)


class TagFollower:
    def __init__(self, tag):
        self.last_id = 0
        self.tag = tag
        self.is_found = False
        self.done_counter = 0

    def follow_once(self, target_id):
        if_has_tag = False
        markers = self.tag.get_markers()
        for marker in markers:
            if (marker[0] >= target_id and marker[0] < 6) or (marker[0] == target_id - 1):
                turn_and_walk(marker[1], marker[2])
                self.is_found = True
                if_has_tag = True
        print(f'target_id = {target_id}, is_found = {self.is_found} if_has_tag = {if_has_tag}')
        print(markers)
        
        if not if_has_tag and not self.is_found:
            if target_id == 8:
                turn_right04()
                time.sleep(5)

        if not if_has_tag and self.is_found:
            if self.done_counter < 10:
                self.done_counter += 1
                self.is_found = True
                return False
            else:
                self.done_counter = 0
                print('done!')
                self.is_found = False
                return True
        else:
            return False


def main():
    try:
        cur_tagid = 0
        step = 0
        
        rospy.init_node('ar_tag_tracker')
        tag = TagConverter()
        
        print('Start action thread ...')
        init_action_thread()
        time.sleep(1)

        follower = TagFollower(tag)
        print('tag follower')

        while not rospy.is_shutdown():
            time.sleep(0.1)
            is_done = follower.follow_once(cur_tagid)
            if is_done:
                cur_tagid += 1
            if (cur_tagid == 8) and is_done:
                walk_slow()
                turn_right10()
            if cur_tagid == 9: 
                if step == 0:
                    walk_slow()
                    walk_slow00()
                    UpBridge2()
                    step += 1
                if step == 1 or step == 2:
                    UpBridge2()
                    step += 1
                else:
                    kick_ball(CMDcontrol)
                    
    except rospy.ROSInterruptException:
        pass


if __name__ == '__main__':
    main()