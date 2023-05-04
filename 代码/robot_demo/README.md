<!--
 * @Author: dongdongmingming
 * @Date: 2021-06-28 18:59:31
 * @LastEditors: Please set LastEditors
 * @LastEditTime: 2021-06-28 22:28:26
 * @FilePath: \aelos_race\README.md
 * @Description: 
-->
# aelos  race

## 准备工作

- 需要准备 1 台路由器，需要将 Wi-Fi 设置为
  - ssid：`nasa5G`
  - 密码: `mayday666`

- 机器人启动后，进入路由器管理员后台，查看机器人 `IP` 地址，如 `192.168.123.154`

## 使用步骤

- ssh 登录机器人
  - `ssh lemon@192.168.123.154`
  - 登录密码为: `leju123`

- 启动机器人摄像头
  - `roslaunch robot_demo ar_track.launch`
  - 打开 `http://192.168.123.154:8080/stream_viewer?topic=/usb_cam/image_raw` 可查看摄像头视频流

- 将机器人放置于赛道起点后，启动机器人赛道程序
  - 进入程序目录 `cd /home/lemon/catkin_ws/src/robot_demo/scripts`
  - 执行比赛程序 `python tag_traker_fast.py`

## 注意

- 踢球需要颜色识别，请自行标记球与球门的颜色，编辑文件 `kickBallOnly.py`，在如图所示位置修改颜色的 RGB 值

取色

![](./img/20210512101514.png)

修改编辑文件 `kickBallOnly.py`，在如下位置修改取色工具获取到的颜色值

![](./img/20210512101210.png)

- **代码更新**
  - 更新指令 `scp -r ./robot_demo lemon@lemon.local:/home/lemon/catkin_ws/src/`
  - 详细操作见视频  branch:with_video  https://www.lejuhub.com/doming_test/aelos_race/-/tree/with_video/img