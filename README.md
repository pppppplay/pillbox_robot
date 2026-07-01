# 智慧家用藥盒管理系統 + 機械手臂

以 ROS2 + URSim + MoveIt2 + Node-RED 為核心的智慧藥盒手臂控制系統

## 系統需求

- Windows 11 + WSL2
- Ubuntu 22.04
- Docker Desktop
- ROS2 Humble
- Node-RED

## 快速部署

### 1. 安裝 ROS2 Humble
```bash
sudo apt install -y ros-humble-desktop ros-humble-ur ros-humble-moveit ros-humble-moveit-ros-planning-interface
```

### 2. 安裝 Node-RED
```bash
sudo npm install -g --unsafe-perm node-red
cd ~/.node-red && npm install @flowfuse/node-red-dashboard
```

### 3. 下載專案
```bash
git clone https://github.com/你的帳號/pillbox_robot.git ~/pillbox_robot
```

### 4. 一鍵啟動
```bash
~/pillbox_robot/start_pillbox.sh
```

## 展示網址

- URSim Polyscope：http://localhost:6080/vnc.html
- Node-RED 編輯器：http://localhost:1880
- Dashboard 展示：http://localhost:1880/dashboard

## 系統架構

- **RViz**：顯示 UR10 手臂 + 兩個使用者藥盒 3D 模型
- **MoveIt2**：手臂路徑規劃與控制
- **Python**：藥盒邏輯、HTTP 伺服器、手臂控制
- **Node-RED**：Dashboard 身份識別、藥格選擇、服藥紀錄

## 使用流程

1. 開啟 Dashboard
2. 點選使用者（使用者一 / 使用者二）
3. 選擇星期與時段（早/午/晚/睡前）
4. 點「確認取藥」
5. RViz 手臂自動移動到對應藥格
6. 藥格變灰，服藥紀錄自動更新
