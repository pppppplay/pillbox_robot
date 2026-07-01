import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
import time

PILL_SLOTS = {
    "mon_am":  [-1.57, -1.57,  1.57, -1.57, -1.57, 0.0],
    "mon_pm":  [-1.20, -1.57,  1.57, -1.57, -1.57, 0.0],
    "mon_eve": [-0.80, -1.57,  1.57, -1.57, -1.57, 0.0],
    "tue_am":  [-1.57, -1.20,  1.57, -1.57, -1.57, 0.0],
    "tue_pm":  [-1.20, -1.20,  1.57, -1.57, -1.57, 0.0],
    "tue_eve": [-0.80, -1.20,  1.57, -1.57, -1.57, 0.0],
    "home":    [ 0.00, -1.57,  0.00, -1.57,  0.00, 0.0],
}

RFID_SCHEDULE = {
    "user_001": ["mon_am", "mon_pm", "mon_eve"],
    "user_002": ["tue_am", "tue_pm"],
}

JOINT_NAMES = [
    "shoulder_pan_joint",
    "shoulder_lift_joint",
    "elbow_joint",
    "wrist_1_joint",
    "wrist_2_joint",
    "wrist_3_joint",
]

class PillboxController(Node):
    def __init__(self):
        super().__init__("pillbox_controller")
        self._action_client = ActionClient(
            self,
            FollowJointTrajectory,
            "/scaled_joint_trajectory_controller/follow_joint_trajectory"
        )

    def move_to_slot(self, slot_name):
        if slot_name not in PILL_SLOTS:
            self.get_logger().error(f"找不到藥格：{slot_name}")
            return

        angles = PILL_SLOTS[slot_name]
        self.get_logger().info(f"移動到藥格：{slot_name}")

        goal = FollowJointTrajectory.Goal()
        traj = JointTrajectory()
        traj.joint_names = JOINT_NAMES

        point = JointTrajectoryPoint()
        point.positions = angles
        point.time_from_start.sec = 4
        traj.points = [point]
        goal.trajectory = traj

        self._action_client.wait_for_server()
        future = self._action_client.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, future)

        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error("目標被拒絕！")
            return

        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)
        self.get_logger().info(f"藥格 {slot_name} 到位！")
        time.sleep(1)

def main():
    rclpy.init()
    node = PillboxController()

    rfid_id = "user_001"
    slots = RFID_SCHEDULE.get(rfid_id, [])
    print(f"使用者：{rfid_id}，藥格：{slots}")

    for slot in slots:
        node.move_to_slot(slot)

    print("歸位中...")
    node.move_to_slot("home")
    print("完成！")

    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
