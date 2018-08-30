#! /usr/bin/env python3

import sys
import time
import threading
import pymeasure

import rospy
import std_msgs
from std_msgs.msg import Float64


class lakeshore218_driver(object):

    def __init__(self, IP='', GPIB=1):
        self.IP = IP
        self.GPIB = GPIB
        self.com = pymeasure.gpib_prologix(self.IP, self.GPIB)

    def measure(self):
        self.com.open()
        self.com.send('KRDG?')
        raw = self.com.readline()
        ret = raw.strip().split(',')
        self.com.close()
        temperature = list(map(float, ret))
        
        return temperature

    def measure_ch(self, ch=1):
        self.com.open()
        self.com.send('KRDG? %d'%(ch))
        ret = self.com.readline()
        self.com.close()
        temperature = float(ret)

        return temperature

def str2list(param):
    return param.strip('[').strip(']').split(',')
    
if __name__ == '__main__':
    node_name = 'lakeshore_218'
    rospy.init_node(node_name)

    ch_number = 8
    topic_name_index = 0
    onoff_index = 1
    host = rospy.get_param('~host')
    port = rospy.get_param('~port')
    rate = rospy.get_param('~rate')
    topic_list = [str2list(rospy.get_param('~topic{}'.format(i+1))) for i in range(ch_number)]

    try:
        temp = lakeshore218_driver(host, port)
    except OSError as e:
        rospy.logerr("{e.strerror}. host={host}".format(**locals()))
        sys.exit()

    pub_list = [rospy.Publisher(topic_name[topic_name_index], Float64, queue_size=1) for topic_name in topic_list]
    msg_list = [Float64() for i in range(ch_number)]
    
    while not rospy.is_shutdown():

        ret = temp.measure()

        for topic, pub, msg, i in zip(topic_list, pub_list, msg_list, range(8)):
            if int(topic[onoff_index]) == 0: pass
            elif int(topic[onoff_index]) == 1:
                msg.data = ret[i]
                pub.publish(msg)
            continue
        continue
