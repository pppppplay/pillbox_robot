#!/bin/bash

echo "======================================"
echo "  智慧藥盒手臂控制系統 啟動中..."
echo "======================================"

# 終止之前殘留的程序
echo "→ 清理舊程序..."
pkill -f "pillbox_server.py" 2>/dev/null
fuser -k 5000/tcp 2>/dev/null
pkill -f "node-red" 2>/dev/null
pkill -f "ur_control" 2>/dev/null
pkill -f "ur_moveit" 2>/dev/null
docker stop $(docker ps -q --filter ancestor=universalrobots/ursim_e-series) 2>/dev/null
sleep 2

# 載入 ROS2 環境
source /opt/ros/humble/setup.bash
source ~/pillbox_robot/install/setup.bash 2>/dev/null

# 啟動 URSim
echo "→ 啟動 URSim..."
docker run --rm -d -p 5900:5900 -p 6080:6080 universalrobots/ursim_e-series
sleep 5

# 啟動 UR robot driver
echo "→ 啟動 UR Robot Driver..."
ros2 launch ur_robot_driver ur_control.launch.py \
    ur_type:=ur10 \
    robot_ip:=127.0.0.1 \
    use_fake_hardware:=true \
    launch_rviz:=false &
sleep 8

# 啟動 MoveIt2
echo "→ 啟動 MoveIt2..."
ros2 launch ur_moveit_config ur_moveit.launch.py \
    ur_type:=ur10 \
    use_fake_hardware:=true \
    launch_rviz:=false &
sleep 8

# 啟動 RViz 並載入藥盒設定
echo "→ 啟動 RViz..."
sleep 5
rviz2 -d /home/thx93/pillbox_robot/pillbox.rviz &
sleep 5

# 啟動 Python 手臂控制伺服器
echo "→ 啟動手臂控制伺服器..."
cd ~/pillbox_robot/src/pillbox_arm
python3 pillbox_server.py &
sleep 2

# 啟動 Node-RED
echo "→ 啟動 Node-RED..."
node-red &
sleep 5

echo ""
echo "======================================"
echo "  系統啟動完成！"
echo "======================================"
echo ""
echo "  URSim Polyscope：http://localhost:6080/vnc.html"
echo "  Node-RED 編輯器：http://localhost:1880"
echo "  Dashboard 展示：http://localhost:1880/dashboard"
echo ""
echo "  按 Ctrl+C 關閉所有程序"
echo "======================================"

# 等待直到按 Ctrl+C
trap 'echo "關閉系統..."; pkill -f pillbox_server.py; pkill -f node-red; pkill -f ur_control; pkill -f ur_moveit; docker stop $(docker ps -q --filter ancestor=universalrobots/ursim_e-series) 2>/dev/null; exit 0' INT

wait
