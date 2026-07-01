import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose
import math

# 藥盒 21 格座標定義（單位：公尺）
# 早/午/晚 x 7天，先定義示範用的幾格
PILL_SLOTS = {
    "mon_am": {"x": 0.3, "y": 0.2, "z": 0.3},
    "mon_pm": {"x": 0.3, "y": 0.0, "z": 0.3},
    "mon_eve": {"x": 0.3, "y": -0.2, "z": 0.3},
    "tue_am": {"x": 0.2, "y": 0.2, "z": 0.3},
    "tue_pm": {"x": 0.2, "y": 0.0, "z": 0.3},
    "tue_eve": {"x": 0.2, "y": -0.2, "z": 0.3},
    "home":   {"x": 0.0, "y": 0.3, "z": 0.5},
}

class PillboxArmController(Node):
    def __init__(self):
        super().__init__('pillbox_arm_controller')
        self.get_logger().info('藥盒手臂控制器啟動')
        self.publisher = self.create_publisher(Pose, '/target_pose', 10)

    def move_to_slot(self, slot_name):
        if slot_name not in PILL_SLOTS:
            self.get_logger().error(f'找不到藥格：{slot_name}')
            return
        pos = PILL_SLOTS[slot_name]
        pose = Pose()
        pose.position.x = pos["x"]
        pose.position.y = pos["y"]
        pose.position.z = pos["z"]
        pose.orientation.w = 1.0
        self.publisher.publish(pose)
        self.get_logger().info(f'移動到藥格 {slot_name}：x={pos["x"]}, y={pos["y"]}, z={pos["z"]}')

def main():
    rclpy.init()
    node = PillboxArmController()
    
    # 測試：依序移動到幾個藥格
    import time
    slots = ["mon_am", "mon_pm", "mon_eve", "home"]
    for slot in slots:
        node.move_to_slot(slot)
        time.sleep(2)
    
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
