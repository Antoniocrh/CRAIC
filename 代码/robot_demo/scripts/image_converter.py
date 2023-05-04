#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import numpy as np


class ImgConverter():
    def __init__(self):
        self.bridge = CvBridge()        
        self.sub_chest = rospy.Subscriber('/usb_cam_chest/image_raw', Image, self.cb_chest)
        # self.pub_chest_rotated = rospy.Publisher("/usb_cam/image_rotated", Image)
        self.img_chest = None
        

    def cb_chest(self, msg):
        cv2_img = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        self.img_chest = cv2_img
        
        # cv2_img_rot = np.rot90(cv2_img)
        # self.pub_chest_rotated.publish(self.bridge.cv2_to_imgmsg(cv2_img_rot, "bgr8"))

    def chest_image(self):
        return True, self.img_chest
        

def main():
    try:
        rospy.init_node('image_listener')
        print('Node init')
        image_reader = ImgConverter()
        
        while True:
            rospy.spin()
            time.sleep(0.01)
            
    except rospy.ROSInterruptException:
        pass
    
# testing
if __name__ == '__main__':
    main()
