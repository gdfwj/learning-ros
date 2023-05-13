#!/usr/bin/env python
# coding=utf-8

import os
import signal
import time
import multiprocessing
import rospy
import yaml
import psutil
import tkinter
from std_srvs.srv import Trigger, TriggerRequest
from std_msgs.msg import String
from patch_embedding.srv import Base
from util import terminate_process


params = {}
controller = None
tkinterUI = None

class Controller:

    def __init__(self):

        def launch_init():
            if params['simulate']:
                os.system("roslaunch patch_embedding sim_init.launch")
            else:
                os.system("roslaunch patch_embedding robot_init.launch")

        p = multiprocessing.Process(target=launch_init)
        p.start()
        self.init_pid = p.pid

        rospy.init_node("controller")
        for key in params:
            rospy.set_param(key, params[key])

    def create_map_start(self):
        """开始建图。
        """
        client = rospy.ServiceProxy('/control/create_map/start', Base)
        rospy.wait_for_service('/control/create_map/start')
        resp = client('start')
        loginfo(resp.response)

    def create_map_save(self, map_id=None):
        """结束建图，保存地图。需要传入地图id。

        Args:
            map_id (int): 地图ID
        """
        client = rospy.ServiceProxy('/control/create_map/save', Base)
        rospy.wait_for_service('/control/create_map/save')
        if params['use_tkinter'] and map_id == None:
            map_id = tkinterUI.t.get()
        save_path = params['pkg_path'] + '/maps/map' + str(map_id)
        resp = client(save_path)
        loginfo(resp.response)

    def edit_mark(self, map_id=None):
        """编辑航点。需传入地图id。

        Args:
            map_id (int): 地图ID
        """
        client = rospy.ServiceProxy('/control/mark/edit', Base)
        rospy.wait_for_service('/control/mark/edit')
        if params['use_tkinter'] and map_id == None:
            map_id = tkinterUI.t.get()
        map_path = params['pkg_path'] + '/maps/map' + str(map_id) + '.yaml'
        resp = client(map_path)
        loginfo(resp.response)
    
    def save_mark(self):
        """保存航点。
        """
        client = rospy.ServiceProxy('/control/mark/save', Base)
        rospy.wait_for_service('/control/mark/save')
        resp = client('save')
        loginfo(resp.response)

    def navigation_init(self, map_id=None):
        """选择一张地图进行导航初始化，调整机器人初始位置。

        Args:
            map_id (int): 地图ID
        """
        client = rospy.ServiceProxy('/control/navigation/init', Base)
        rospy.wait_for_service('/control/navigation/init')
        if params['use_tkinter'] and map_id == None:
            map_id = tkinterUI.t.get()
        map_path = params['pkg_path'] + '/maps/map' + str(map_id) + '.yaml'
        resp = client(map_path)
        loginfo(resp.response)

    # def navigation_ready(self):
    #     client = rospy.ServiceProxy('/control/navigation/ready', Base)
    #     rospy.wait_for_service('/control/navigation/ready')
    #     resp = client('start')
    #     loginfo(resp.response)

    def navigation_begin(self, dst=None):
        client = rospy.ServiceProxy('/control/navigation/begin', Base)
        rospy.wait_for_service('/control/navigation/begin')
        if params['use_tkinter'] and dst == None:
            dst = tkinterUI.t.get()
        resp = client(dst)
        loginfo(resp.response)

    def grab(self):
        """在当前位置执行抓取
        """
        client = rospy.ServiceProxy('/control/arm', Base)
        rospy.wait_for_service('/control/arm')
        resp = client('start')
        loginfo(resp.response)

    def exit(self):
        terminate_process(self.init_pid)
        if params['use_tkinter']:
            tkinterUI.window.destroy()


class TkinterUI:
    def __init__(self, controller: Controller):
        self.window = tkinter.Tk()
        self.window.geometry('400x500')
        frame = tkinter.Frame(self.window)
        frame.pack(fill='both', expand='yes')

        b1 = tkinter.Button(frame,text="开启建图",command=controller.create_map_start)
        b1.pack()
        b2 = tkinter.Button(frame,text="保存地图",command=controller.create_map_save)
        b2.pack()
        b6 = tkinter.Button(frame,text="编辑航点",command=controller.edit_mark)
        b6.pack()
        b7 = tkinter.Button(frame,text="保存航点",command=controller.save_mark)
        b7.pack()
        b3 = tkinter.Button(frame,text="校准导航",command=controller.navigation_init)
        b3.pack()
        b3 = tkinter.Button(frame,text="导航到目标点",command=controller.navigation_begin)
        b3.pack()
        b4 = tkinter.Button(frame,text="抓取",command=controller.grab)
        b4.pack()
        b5 = tkinter.Button(frame,text="退出",command=controller.exit)
        b5.pack()
        self.t = tkinter.Entry(frame)
        self.t.pack()

        l = tkinter.Label(frame, text='输出信息', font=('微软雅黑', 10, 'bold'), width=500, justify='left', anchor='w')
        l.pack()
        s1 = tkinter.Scrollbar(frame)      # 设置垂直滚动条
        s2 = tkinter.Scrollbar(frame, orient='horizontal')    # 水平滚动条
        s1.pack(side='right', fill='y')     # 靠右，充满Y轴
        s2.pack(side='bottom', fill='x')    # 靠下，充满x轴
        self.output = tkinter.Text(frame, font=('Consolas', 9), undo=True, autoseparators=False, 
            wrap='none', xscrollcommand=s2.set, yscrollcommand=s1.set)  # , state=DISABLED, wrap='none'表示不自动换行
        self.output.pack(fill='both', expand='yes')
        s1.config(command=self.output.yview)  # Text随着滚动条移动被控制移动
        s2.config(command=self.output.xview)

    def loop(self):
        self.window.mainloop()

    def log(self, text):
        now_time = time.strftime("%H:%M:%S")
        self.output.insert('end','[' + now_time + '] ' + text + '\n')


def loginfo(text):
    if params['use_tkinter']:
        tkinterUI.log(text)

def start_webserver():
    os.system("python3 webServer.py")

if __name__ == '__main__':
    pkg_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(pkg_path + "/config/control.yaml", 'r') as file:
        params = yaml.load(file.read(), Loader=yaml.FullLoader)
        params['pkg_path'] = pkg_path

    controller = Controller()
    if params['use_tkinter']:
        tkinterUI = TkinterUI(controller)
        tkinterUI.loop()
    rospy.spin()
    
