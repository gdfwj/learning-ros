#!/usr/bin/env python2
# coding=utf-8
import rospy
from patch_embedding.srv import Base, Conn
from std_msgs.msg import String
import sys

def get_text_type(text):
    if "去" in text and "回" in text:
        ind1 = text.index("去")
        ind2 = text.index("回")
        t = []
        t.append(text[ind1+3: ind2])
        t.append(text[ind2+3: len(text)-2])
        return 4, t
    elif "去" in text:
        ind = text.index('去')
        t = text[ind+3: len(text)-2]
        return  1, t
    elif "抓" in text:
        return 2, 0
    elif '渴' in text:
        return 3, 0
    elif '递' in text:
        return 6, 0
    elif 'to' in text and 'then go to' in text:
        ind1 = text.index("to")
        ind2 = text.index("then")
        x = text.split()
        t = []
        for i in range(len(x)-2):
            if x[i]=='to':
                t.append(x[i+1])
            if x[i]=='then' and x[i+1]=='go' and x[i+2]=='to':
                if x[i+3][-1]=='.':
                    t.append(x[i+3][:-1])
                else:
                    t.append(x[i+3])
        return 4, t
    elif 'to' in text:
        x = text.split()
        for i in range(len(x)):
            if x[i]=='to':
                if x[i+1][-1]=='.':
                    return 1,x[i+1][:-1]
                return 1, x[i+1]
    elif "grab" in text or "Grab" in text:
        return 2, 0
    elif 'thirsty' in text:
        return 3, 0
    elif "pass" in text:
        return 6, 0
    return 0, 0

def pub_tts(text):
    rate = rospy.Rate(1)
    pub = rospy.Publisher("tts_text_", String, queue_size=1000)
    pub_msg = String()
    pub_msg.data = text
    pub.publish(pub_msg)
    rate.sleep()
    pub.publish(pub_msg)


# def get_point_id(label_name):
#     from navigation import Waypoints
#     ids = Waypoints.getWaypointByName(label_name)
#     ids = sqlHelper.select("tb_label", {"label_name":label_name})
#     if len(ids)==0:
#         return 99999
#     else:
#         return ids[0]["label_id"]


if __name__ == "__main__":
    rospy.init_node("voicectrl")
    args = sys.argv[:]
    text = args[1]
    type, msg = get_text_type(text)
    print(msg)
    
    # times = 0
    # while not rospy.is_shutdown():
    #     pub_msg.data = "hello, ros! , times:"+str(times)
    #     print("pub hello, ros! , times:"+str(times))
    #     times+=1
    #     pub.publish(pub_msg)
    #     rate.sleep()

    print("启动语音")
    if type==1:  # 导航前往地点
        pub_tts("开始导航"+msg)
        client = rospy.ServiceProxy('/control/web', Conn)
        rospy.wait_for_service('/control/web')
        resp = client("navigation_begin",str(msg),"")
        # os.system('rostopic pub /tts_text std_msgs/String "开始导航"')
        # client = rospy.ServiceProxy('/control/web', Conn)
        # rospy.wait_for_service('/control/web')
        # id = get_point_id(msg)
        # if id==99999:
        #     pub.publish("航点错误，未知的"+msg)
        #     print("航点错误，未知的"+msg)
        # resp = client("navigation_begin", id, "")
        pub_tts("已经到达位置")
        # os.system('rostopic pub /tts_text std_msgs/String "已经到达位置"')
        resp = client("navigation_finish", 0, "")
    elif type==2:
        pub_tts("开始抓取")
        # os.system('rostopic pub /tts_text std_msgs/String "开始抓取"')
        client = rospy.ServiceProxy('/control/web', Conn)
        rospy.wait_for_service('/control/web')
        resp = client("grab", "0", "")
        pub_tts("抓取完成")
        # os.system('rostopic pub /tts_text std_msgs/String "抓取完成"')
    elif type == 3:
        pub_tts("你要喝点什么吗")
    elif type == 4:
        # id1 = get_point_id(msg[0])
        # if id1==99999:
        #     pub.publish("航点错误，未知的"+msg[0])
        #     print("航点错误，未知的"+msg[0])
        # id2 = get_point_id(msg[1])
        # if id2==99999:
        #     pub.publish("航点错误，未知的"+msg[1])
        #     print("航点错误，未知的"+msg[1])
        pub_tts("开始导航"+msg[0])
        client = rospy.ServiceProxy('/control/web', Conn)
        rospy.wait_for_service('/control/web')
        resp = client("navigation_begin",str(msg[0]),"")
        # os.system('rostopic pub /tts_text std_msgs/String "开始导航"')
        # client = rospy.ServiceProxy('/control/web', Conn)
        # rospy.wait_for_service('/control/web')
        # resp = client("navigation_begin", id1, "")
        pub_tts("已经到达抓取位置")
        rospy.wait_for_service('/control/web')
        client2 = rospy.ServiceProxy('/control/web', Conn)
        resp = client2("grab", "0", "")
        pub_tts("抓取完成")
        pub_tts("开始导航"+msg[1])
        resp = client("navigation_begin",str(msg[1]),"")
        # os.system('rostopic pub /tts_text std_msgs/String "开始导航"')
        # rospy.wait_for_service('/control/web')
        # resp = client("navigation_begin", id2, "")
        pub_tts("已经到达最终位置")
        rospy.wait_for_service('/control/web')
        resp = client("pass_obj", "0", "")
        # os.system('rostopic pub /tts_text std_msgs/String "已经到达位置"')
        resp = client("navigation_finish", 0, "")
    elif type==6:
        pub_tts("开始递物")
        client = rospy.ServiceProxy('/control/web', Conn)
        resp = client("pass_obj", "0", "")
    else:
        pub_tts("我不理解你在说什么")


        
    
