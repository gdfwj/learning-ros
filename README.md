# 2023软件工程——补丁嵌入队

历次展示视频：[2023软工-补丁嵌入队-展示视频](https://bhpan.buaa.edu.cn:443/link/FB62ABE4C4EEA21784BAAABAA1155ACD)

## 项目概述

随着人工智能、计算机和机器人操作系统ROS的飞速发展和进步，机器人逐渐向生活化、服务化的方向发展，应用范围不断扩大。目前市场上已经出现了很多类型的机器人，例如可以自动识别房间地形、完成清扫任务的扫地机器人，以及帮助人类寻路的导航机器人。2022年末，chatGPT的出现也预示着机器人又将迎来一次发展的热潮。

本项目将开发一种智能家庭服务机器人。它可以实现语音控制、取物送物、自动建图、路径规划、动态避障等功能，并具有美观的人机交互界面。该机器人将在家政服务中具有通用性，实现在多种场景下的服务需求，同时促进相关的进一步研究。

## 项目成员

补丁嵌入队的成员及分工如下：

| 学号     | 姓名   | 分工                       |
| :------- | :----- | -------------------------- |
| 20373159 | 李国玮 | 项目组长，后端和数据库开发 |
| 20373276 | 王子豪 | 需求分析师，导航和语音     |
| 20373146 | 景泓斌 | 系统架构师，ROS主控设计    |
| 20373142 | 高渤宇 | 测试人员，前端开发         |
| 20373969 | 刘子奇 | 测试人员，建图和标注       |

## 项目介绍

### 硬件结构

![硬件结构](images/hardware.jpg)

### 系统结构

#### 文件目录

```bash
├── backend                 # 后端代码
├── docs                    # 文档
├── images                  # 展示图片
├── ros_web                 # 前端代码
├── src                     # ROS包
│   ├── patch_embedding         # 主要功能包
│   │   ├── config                  # 配置文件
│   │   ├── launch                  # launch文件
│   │   ├── maps                    # 保存的地图
│   │   ├── marks                   # 保存的航点
│   │   ├── scripts                 # python代码
│   │   ├── src                     # c代码
│   │   └── srv                     # 自定义服务类型
│   ├── rplidar_ros             # 激光雷达包（官方包）
│   ├── iai_kinect2             # 相机包（官方包）
│   ├── waterplus_map_tools     # 标注工具包（官方包）
│   ├── wpb_home                # 机器人功能包（官方包）
│   ├── wpr_simulation          # 模拟包（官方包）
│   └── xfyun_waterplus         # 语音包（官方包）
└── test                    # 测试脚本
```

#### 系统架构

![系统架构](images/system.png)

### 技术介绍

- 前端：`vue`框架，`element-ui`组件库，`axios`数据交互。
- 后端：`django`框架，`pymysql`连接数据库。
- 数据库：`MySQL`。
- 机器人端：`ROS`，主从机，`ssh`。

## 环境配置

### 环境及软件需求

- Ubuntu 18.04 LTS
- ROS Melodic
- python 3.6
- MySQL 5.7

### ROS包的安装

- 相关系统包

```bash
sudo apt-get install ros-melodic-joy
sudo apt-get install ros-melodic-hector-mapping
sudo apt-get install ros-melodic-gmapping
sudo apt-get install ros-melodic-map-server
sudo apt-get install ros-melodic-navigation
sudo apt-get install ros-melodic-move-base
sudo apt-get install ros-melodic-amcl
sudo apt-get install ros-melodic-cv-bridge
sudo apt-get install ros-melodic-audio-common
sudo apt-get install libasound2
sudo apt-get install ros-melodic-sound-play
```

- `wpb_home`包参考：https://github.com/6-robot/wpb_home
- `wpr_simulation`包参考：https://github.com/6-robot/wpr_simulation
- `waterplus_map_tools`包参考：https://github.com/6-robot/waterplus_map_tools
- `rplidar_ros`包参考：https://github.com/robopeak/rplidar_ros
- `iai_kinect`2包参考：https://github.com/code-iai/iai_kinect2

### python包的安装

- 通过pip安装以下包，或在`scripts`目录下执行`pip3 install -r requirements.txt`。

```
Pillow==9.5.0
psutil==5.9.4
PyYAML==6.0
websockets==9.1
```

- 通过apt安装以下包：

```bash
sudo apt install python3-tk
```

### SSH配置

- 机器人端和客户端都安装`openssh-server`和`openssh-client`。
- 机器人端安装`sshpass`：

```bash
sudo apt install sshpass
```

### ROS主从机配置

假设机器人主机的IP地址为：`192.168.8.201`，客户端主机的IP地址为：`192.168.8.100`，则各主机配置如下。

#### 机器人主机

- `~/.bashrc`文件中添加：

```bash
export ROS_HOSTNAME=192.168.8.201
export ROS_MASTER_URI=http://192.168.8.201:11311
export ROS_IP=192.168.8.201
```

- `/etc/hosts`文件中添加：

```
192.168.8.201   客户端主机hostname
```

#### 客户端主机

- `~/.bashrc`文件中添加：

```bash
export ROS_HOSTNAME=192.168.8.100
export ROS_MASTER_URI=http://192.168.8.201:11311
export ROS_IP=192.168.8.201
```

- `/etc/hosts`文件中添加：

```
192.168.8.201   robot
```

## 项目运行

### 机器人端

在`scripts`目录下执行：`python3 controller.py`。

### 客户端

- 主控服务端：在`scripts`目录下执行`python3 controller_client.py`。
- 后端：在`backend`目录下执行`python3 manage.py runserver`。
- 前端：在`ros_web`目录下执行`yarn run dev`，打开http://localhost:8080即可。

## 参考资料

- 机器人官方包：https://github.com/6-robot
- SSH配置：https://zhuanlan.zhihu.com/p/577082732
- ROS主从机配置：https://blog.csdn.net/zhanghm1995/article/details/106781954

