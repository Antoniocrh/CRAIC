#!/usr/bin/env python
# -*- coding: utf-8 -*-
import CMDcontrol
import rospy
import tf
import numpy as np
from math import sqrt
from geometry_msgs.msg import PoseWithCovarianceStamped
from ar_track_alvar_msgs.msg import AlvarMarkers
from ar_track_alvar_msgs.msg import AlvarMarker

def angle_between(v1, v2):
    cosTh = np.dot(v1, v2)
    sinTh = np.cross(v1, v2)
    angle = np.rad2deg(np.arctan2(sinTh, cosTh))[2]
    return angle

class pose_converter():
    def __init__(self):
        self.p_0 = np.array([-0.1429473853758271, -0.004343588010841607, 0.1392410096834090876])
        self.p_1 = np.array([-0.043167954694022376, -0.00023977932710763676, 0.2964736797698838])
        self.sub = rospy.Subscriber('ar_pose_marker',AlvarMarkers,self.sub_cb)
        self.makers = []
        self.vd = self.p_1 - self.p_0

    def sub_cb(self, msg):
        self.makers = []
        
        for marker in self.makers:
            pos = marker.pose.pose.position
            p_l = np.array([pos.x, pos.y, pos.z])
            v_pl = np.array([pos.x, pos.y, pos.z]) - self.p_0
            dist = sqrt(
                (p_l[0] - self.p_0[0])**2 + \
                (p_l[1] - self.p_0[1])**2 + \
                (p_l[2] - self.p_0[2])**2
            )
            angle = angle_between(self.vd, v_pl)
            self.makers.append([marker.id, dist, angle])

    def get_markers(self):
        return self.makers


if __name__ == '__main__':
    try:
        rospy.init_node('ar_tag_tracker')
        master = pose_converter()
        rospy.loginfo('Starting AR tracker Node!')
        while not rospy.is_shutdown():
            rospy.spin()
    except rospy.ROSInterruptException:
        pass
