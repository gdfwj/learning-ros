from utils.sqlHelper import SqlHelper
from django.views import View
from django.http import JsonResponse
from datetime import datetime
import asyncio
import websockets
import os

PREFIX = "E:\\学习\\大三下\\软工\\项目开发\\"
import sys

# 是否开启语音服务
VOICE_ON = False
# 当前正在标注航点的地图id
Map_id_now = 1
DEBUG = False
# if DEBUG:
#     ip_address = 'ws://localhost'
# else :
ip_address = 'ws://192.168.8.100:10086'
# ip_address = 'ws://localhost:8765'

import asyncio
import websockets


async def hello(uri, message):
    async with websockets.connect(uri) as websocket:
        await websocket.send(message)
        recv_text = await websocket.recv()
        print(recv_text)


def webClient(message, *args):
    if DEBUG:
        return
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    for arg in args:
        message = message + ":" + str(arg)
    loop.run_until_complete(hello(ip_address, message))


def checkWord(inputs: str):
    string = "~!:@#$%^&*()_+-*/<>,.[]\/"
    for i in string:
        if i in inputs:
            raise Exception('check failed')


class ResetAll(View):
    def post(self, request):
        res = {'code': 400, 'msg': '恢复出厂设置成功', 'data': []}
        # request = getRequest(request)
        # class_name = request.get("class_name")
        try:
            sqlHelper = SqlHelper()
            # sqlHelper.delete('tb_label')
            # sqlHelper.delete('tb_map')
            sqlHelper.executeCommit("drop table if exists tb_label")
            sqlHelper.executeCommit("drop table if exists tb_map")
            sql = """create table if not exists tb_map(
                        map_id int unsigned primary key auto_increment, -- map id
                        map_name varchar(20) not null ,                 -- map name
                        map_time datetime not null ,                    -- create time
                        map_remark varchar(100) default null ,            -- detail
                        unique key unique_map(map_name)
                    )auto_increment=2;"""
            sqlHelper.executeCommit(sql)
            sql = """create table if not exists tb_label(
                        label_id int unsigned primary key auto_increment, -- label id
                        label_name varchar(20) not null ,                 -- label name
                        label_map int unsigned,                           -- which map it belongs
                        foreign key (label_map) references tb_map(map_id) on delete cascade,
                        label_remark varchar(100) default null,              -- detail
                        UNIQUE key label_unique(label_name, label_map)
                    ) auto_increment=2;"""
            sqlHelper.executeCommit(sql)
            res['code'] = 200
        except Exception as e:
            print(e)
            res['msg'] = '恢复出厂设置失败'
        return JsonResponse(res)


class Update(View):
    def post(self, request):
        res = {'code': 400, 'msg': '升级成功', 'data': []}
        try:
            os.system("cd ~/SE/team03-project; git pull origin main > tmp")
            with open('/home/jinghongbin/SE/team03-project/tmp', encoding='utf-8') as f:
                if f.read().startswith('已经是最新的。'):
                    res['code'] = 400
                    res['msg'] = '已经是最新版'
                else:
                    res['code'] = 200
            os.system("cd ~/SE/team03-project; rm tmp")
        except Exception as e:
            print(e)
            res['msg'] = '升级失败'
        return JsonResponse(res)


class ShowAll(View):
    def post(self, request):
        res = {'code': 400, 'msg': '获取全部地图成功', 'data': []}
        # request = getRequest(request)
        try:
            sqlHelper = SqlHelper()
            results = sqlHelper.select('tb_map', all=True)
            for ares in results:
                dic = {"map_id": ares[0], "map_name": ares[1], "map_time": ares[2], "map_remark": ares[3],
                       "url": PREFIX + "1.png"}
                res['data'].append(dic)
            res['code'] = 200
        except Exception as e:
            print(e)
            res['msg'] = '获取全部地图失败'
        return JsonResponse(res)


class Create_map(View):
    def post(self, request):
        res = {'code': 400, 'msg': '新建地图成功', 'data': []}
        # request = getRequest(request)
        try:
            message = 'map/create/'
            webClient(message)
            res['code'] = 200
        except Exception as e:
            print(e)
            res['msg'] = '新建地图失败'
        return JsonResponse(res)


class Save_map(View):
    def post(self, request):
        res = {'code': 400, 'msg': '保存地图成功', 'data': []}
        request = getRequest(request)
        map_name = request.get("map_name")
        map_remark = request.get("map_remark")
        try:
            checkWord(map_name)
            message = 'map/save/'
            sqlHelper = SqlHelper()
            sqlHelper.insert('tb_map', {"map_name": map_name, "map_remark": map_remark, "map_time": getNowTime()})
            map_id = sqlHelper.select('tb_map', listnames=['map_id'], cond_dict={"map_name": map_name})
            map_id = map_id[0]
            webClient(message, map_id)
            res['code'] = 200
        except Exception as e:
            print(e)
            res['msg'] = '保存地图失败'
        return JsonResponse(res)


class DeleteMap(View):
    def post(self, request):
        res = {'code': 400, 'msg': '删除地图成功', 'data': []}
        request = getRequest(request)
        map_id = int(request.get("map_id"))
        try:
            sqlHelper = SqlHelper()
            sqlHelper.delete('tb_map', {"map_id": map_id})
            res['code'] = 200
        except Exception as e:
            print(e)
            res['msg'] = '删除地图失败'
        return JsonResponse(res)


class ShowMark(View):
    def post(self, request):
        res = {'code': 400, 'msg': '显示指定地图所有航点成功', 'data': []}
        request = getRequest(request)
        # print(request)
        map_id = int(request.get("map_id"))
        try:
            sqlHelper = SqlHelper()
            results = sqlHelper.select('tb_label', listnames=['label_id', 'label_name', 'label_remark'],
                                       cond_dict={"label_map": map_id})
            for ares in results:
                dic = {"label_id": ares[0], "label_name": ares[1], "label_remark": ares[2]}
                res['data'].append(dic)
            res['code'] = 200
            print(res['data'])
        except Exception as e:
            print(e)
            res['msg'] = '显示指定地图所有航点失败'
        return JsonResponse(res)


class CreateMark(View):
    def post(self, request):
        global Map_id_now
        res = {'code': 400, 'msg': '开始标注航点成功', 'data': []}
        request = getRequest(request)
        map_id = int(request.get("map_id"))
        Map_id_now = map_id
        try:
            message = "mark/create/"
            webClient(message, map_id)
            res['code'] = 200
        except Exception as e:
            print(e)
            res['msg'] = '开始标注航点失败'
        return JsonResponse(res)


class SaveMark(View):
    def post(self, request):
        res = {'code': 400, 'msg': '保存航点标注成功', 'data': []}
        request = getRequest(request)
        label_name = request.get("label_name")
        label_remark = request.get("label_remark")
        try:
            checkWord(label_name)
            message = "mark/save/"
            sqlHelper = SqlHelper()
            sqlHelper.insert('tb_label', params_dict={'label_name': label_name, 'label_remark': label_remark,
                                                      'label_map': Map_id_now})
            label_id = sqlHelper.select('tb_label', listnames=['label_id'], cond_dict={"label_name": label_name})
            label_id = label_id[0][0]
            webClient(message, str(Map_id_now), label_name)
            res['code'] = 200
        except Exception as e:
            print(e)
            res['msg'] = '保存航点标注失败'
        return JsonResponse(res)


class DeleteMark(View):
    def post(self, request):
        res = {'code': 400, 'msg': '删除航点成功', 'data': []}
        request = getRequest(request)
        label_id = int(request.get("label_id"))
        try:
            sqlHelper = SqlHelper()
            sqlHelper.delete("tb_label", {"label_id": label_id})
            res['code'] = 200
        except Exception as e:
            print(e)
            res['msg'] = '删除航点失败'
        return JsonResponse(res)


class ServiceInit(View):
    def post(self, request):
        res = {'code': 400, 'msg': '初始化服务成功', 'data': []}
        request = getRequest(request)
        map_id = int(request.get("map_id"))
        Map_id_now = map_id
        try:
            message = "service/init/"
            webClient(message, map_id)
            res['code'] = 200
        except Exception as e:
            print(e)
            res['msg'] = '初始化服务失败'
        return JsonResponse(res)


class Navigation(View):
    def post(self, request):
        res = {'code': 400, 'msg': '导航成功', 'data': []}
        request = getRequest(request)
        label_id = int(request.get("label_id"))
        # label_name = request.get("label_name")
        try:
            sqlHelper = SqlHelper()
            results = sqlHelper.select("tb_label", listnames=["label_name"], cond_dict={"label_id":label_id})
            label_name = results[0][0]
            message = "navigation/begin/"
            webClient(message, label_name)
            res['code'] = 200
        except Exception as e:
            print(e)
            res['msg'] = '导航失败'
        return JsonResponse(res)


class Navigation_Finish(View):
    def post(self, request):
        res = {'code': 400, 'msg': '导航结束成功', 'data': []}
        request = getRequest(request)
        # label_id = int(request.get("label_id"))
        # label_name = request.get("label_name")
        try:
            # sqlHelper = SqlHelper()
            # results = sqlHelper.select("tb_label", listnames=["label_id"], cond_dict={"label_name":label_name})
            # label_id = int(results[0][0])
            message = "navigation/finish/"
            webClient(message)
            res['code'] = 200
        except Exception as e:
            print(e)
            res['msg'] = '导航结束失败'
        return JsonResponse(res)


class Fetch(View):
    def post(self, request):
        res = {'code': 400, 'msg': '取物成功', 'data': []}
        request = getRequest(request)
        # 桌子的id
        label_id1 = int(request.get("label_id1"))
        # 取物后返回的目的地id
        label_id2 = int(request.get("label_id2"))
        try:
            if label_id1 == -1:
                message = "object/fetch/"
                webClient(message)
            else:
                message = "object/allFetch/"
                # print("**************************heher")
                sqlHelper = SqlHelper()
                results = sqlHelper.select("tb_label", listnames=["label_name"], cond_dict={"label_id": label_id1})
                label_name1 = results[0][0]
                sqlHelper = SqlHelper()
                results = sqlHelper.select("tb_label", listnames=["label_name"], cond_dict={"label_id": label_id2})
                label_name2 = results[0][0]
                webClient(message, label_name1, label_name2)
            res['code'] = 200
        except Exception as e:
            print(e)
            res['msg'] = '取物失败'
        return JsonResponse(res)


class PassObj(View):
    def post(self, request):
        res = {'code': 400, 'msg': '递物成功', 'data': []}
        try:
            message = "object/pass/"
            webClient(message)
            res['code'] = 200
        except Exception as e:
            print(e)
            res['msg'] = '递物失败'
        return JsonResponse(res)


class VoiceChange(View):
    def post(self, request):
        res = {'code': 400, 'msg': '语音服务成功', 'data': []}
        # request = getRequest(request)
        try:
            message = "control/voice/"
            webClient(message)
            res['code'] = 200
        except Exception as e:
            print(e)
            res['msg'] = '语音服务失败'
        return JsonResponse(res)


def getRequest(request):
    """
    获取预处理后的request
    """
    request = str(request.body).replace("true", "True").replace("false", "False")
    return eval(eval(request))


def getNowTime():
    """
    获取当前时间
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
