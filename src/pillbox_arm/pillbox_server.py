import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.executors import MultiThreadedExecutor
from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from visualization_msgs.msg import Marker, MarkerArray
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import threading
import time

DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
TIMES = ["am", "pm", "eve", "bed"]
TIME_COLORS = {
    "am":  (0.2, 0.85, 0.2),
    "pm":  (0.9, 0.85, 0.1),
    "eve": (0.9, 0.45, 0.1),
    "bed": (0.5, 0.2,  0.9),
}

SLOT_W = 0.08
SLOT_H = 0.08
SLOT_D = 0.06

USER_BOXES = {
    "user_001": {"start_x": 0.30, "start_y": -0.12, "color": (0.2, 0.5, 1.0)},
    "user_002": {"start_x": -0.12, "start_y": -0.30, "color": (1.0, 0.3, 0.3)},
}

RFID_SCHEDULE = {
    "user_001": {"name": "使用者一"},
    "user_002": {"name": "使用者二"},
}

def get_joint_angles(user_id, day_idx, time_idx):
    if user_id == "user_001":
        base     =  0.0  + day_idx * 0.05
        shoulder = -1.35 + time_idx * 0.07
        elbow    =  1.55
        w1       = -1.75
        w2       = -1.57
        w3       =  0.0
    else:
        base     = -1.57 + day_idx * 0.05
        shoulder = -1.35 + time_idx * 0.07
        elbow    =  1.55
        w1       = -1.75
        w2       = -1.57
        w3       =  0.0
    return [base, shoulder, elbow, w1, w2, w3]

HOME_ANGLES = [0.0, -1.57, 0.0, -1.57, 0.0, 0.0]
JOINT_NAMES = [
    "shoulder_pan_joint", "shoulder_lift_joint", "elbow_joint",
    "wrist_1_joint", "wrist_2_joint", "wrist_3_joint",
]

# 全域節點引用
arm_node_ref = None
marker_node_ref = None

class MarkerNode(Node):
    def __init__(self):
        super().__init__("pillbox_marker")
        self.marker_pub = self.create_publisher(MarkerArray, "/pillbox_markers", 10)
        self.taken_slots = set()
        self.create_timer(0.3, self.publish_markers)

    def make_cube(self, mid, x, y, z, sx, sy, sz, r, g, b, a=1.0):
        m = Marker()
        m.header.frame_id = "world"
        m.header.stamp = self.get_clock().now().to_msg()
        m.ns = "pillbox"
        m.id = mid
        m.type = Marker.CUBE
        m.action = Marker.ADD
        m.pose.position.x = x
        m.pose.position.y = y
        m.pose.position.z = z
        m.pose.orientation.w = 1.0
        m.scale.x = sx
        m.scale.y = sy
        m.scale.z = sz
        m.color.r = r
        m.color.g = g
        m.color.b = b
        m.color.a = a
        return m

    def make_text(self, mid, x, y, z, text, size=0.10):
        m = Marker()
        m.header.frame_id = "world"
        m.header.stamp = self.get_clock().now().to_msg()
        m.ns = "pillbox"
        m.id = mid
        m.type = Marker.TEXT_VIEW_FACING
        m.action = Marker.ADD
        m.pose.position.x = x
        m.pose.position.y = y
        m.pose.position.z = z
        m.pose.orientation.w = 1.0
        m.scale.z = size
        m.color.r = 1.0
        m.color.g = 1.0
        m.color.b = 1.0
        m.color.a = 1.0
        m.text = text
        return m

    def publish_markers(self):
        marker_array = MarkerArray()
        mid = 0
        for user_id, box in USER_BOXES.items():
            cr, cg, cb = box["color"]
            if user_id == "user_001":
                sx = box["start_x"]
                sy = box["start_y"]
                bx = sx + 3 * SLOT_W
                by = sy + 1.5 * SLOT_H
                bw = 7 * SLOT_W + 0.02
                bh = 4 * SLOT_H + 0.02
                marker_array.markers.append(
                    self.make_cube(mid, bx, by, 0.02, bw, bh, 0.04,
                                   cr*0.3, cg*0.3, cb*0.3))
                mid += 1
                marker_array.markers.append(
                    self.make_text(mid, bx, by, 0.35,
                                   RFID_SCHEDULE[user_id]["name"]))
                mid += 1
                for di in range(7):
                    for ti, t in enumerate(TIMES):
                        slot = f"{user_id}_{DAYS[di]}_{t}"
                        x = sx + di * SLOT_W
                        y = sy + ti * SLOT_H
                        z = 0.05 + SLOT_D / 2
                        if slot in self.taken_slots:
                            r2, g2, b2 = 0.25, 0.25, 0.25
                        else:
                            r2, g2, b2 = TIME_COLORS[t]
                        marker_array.markers.append(
                            self.make_cube(mid, x, y, z,
                                           SLOT_W-0.01, SLOT_H-0.01, SLOT_D,
                                           r2, g2, b2))
                        mid += 1
            else:
                sx = box["start_x"]
                sy = box["start_y"]
                bx = sx + 1.5 * SLOT_H
                by = sy - 3 * SLOT_W
                bw = 4 * SLOT_H + 0.02
                bh = 7 * SLOT_W + 0.02
                marker_array.markers.append(
                    self.make_cube(mid, bx, by, 0.02, bw, bh, 0.04,
                                   cr*0.3, cg*0.3, cb*0.3))
                mid += 1
                marker_array.markers.append(
                    self.make_text(mid, bx, by, 0.35,
                                   RFID_SCHEDULE[user_id]["name"]))
                mid += 1
                for di in range(7):
                    for ti, t in enumerate(TIMES):
                        slot = f"{user_id}_{DAYS[di]}_{t}"
                        x = sx + ti * SLOT_H
                        y = sy - di * SLOT_W
                        z = 0.05 + SLOT_D / 2
                        if slot in self.taken_slots:
                            r2, g2, b2 = 0.25, 0.25, 0.25
                        else:
                            r2, g2, b2 = TIME_COLORS[t]
                        marker_array.markers.append(
                            self.make_cube(mid, x, y, z,
                                           SLOT_H-0.01, SLOT_W-0.01, SLOT_D,
                                           r2, g2, b2))
                        mid += 1
        self.marker_pub.publish(marker_array)


class ArmNode(Node):
    def __init__(self, marker_node):
        super().__init__("pillbox_arm")
        self.marker_node = marker_node
        self.busy = False
        self._action_client = ActionClient(
            self, FollowJointTrajectory,
            "/scaled_joint_trajectory_controller/follow_joint_trajectory"
        )

    def move_to_angles(self, angles, duration=4):
        goal = FollowJointTrajectory.Goal()
        traj = JointTrajectory()
        traj.joint_names = JOINT_NAMES
        point = JointTrajectoryPoint()
        point.positions = angles
        point.time_from_start.sec = duration
        traj.points = [point]
        goal.trajectory = traj
        self._action_client.wait_for_server()
        send_future = self._action_client.send_goal_async(goal)
        event = threading.Event()

        def goal_cb(future):
            gh = future.result()
            if not gh.accepted:
                event.set()
                return
            res_future = gh.get_result_async()
            res_future.add_done_callback(lambda f: event.set())

        send_future.add_done_callback(goal_cb)
        event.wait(timeout=15)
        time.sleep(0.5)

    def fetch_slot(self, user_id, day_idx, time_key):
        self.busy = True
        slot = f"{user_id}_{DAYS[day_idx]}_{time_key}"
        time_idx = TIMES.index(time_key)
        print(f"→ 移動到藥格：{slot}")
        angles = get_joint_angles(user_id, day_idx, time_idx)
        self.move_to_angles(angles)
        self.marker_node.taken_slots.add(slot)
        print(f"✓ 取藥完成！")
        time.sleep(0.8)
        print("→ 歸位中...")
        self.move_to_angles(HOME_ANGLES, duration=3)
        print("✓ 歸位完成！")
        self.busy = False


class PillboxHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/fetch":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            data = json.loads(body)
            user_id = data.get("user")
            day_idx = int(data.get("day", 0))
            time_key = data.get("time")

            if arm_node_ref and not arm_node_ref.busy:
                threading.Thread(
                    target=arm_node_ref.fetch_slot,
                    args=(user_id, day_idx, time_key),
                    daemon=True
                ).start()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "ok"}).encode())
            else:
                self.send_response(429)
                self.end_headers()
                self.wfile.write(json.dumps({"status": "busy"}).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, format, *args):
        pass


def main():
    global arm_node_ref, marker_node_ref

    rclpy.init()
    marker_node = MarkerNode()
    arm_node = ArmNode(marker_node)
    arm_node_ref = arm_node
    marker_node_ref = marker_node

    executor = MultiThreadedExecutor()
    executor.add_node(marker_node)
    executor.add_node(arm_node)

    executor_thread = threading.Thread(target=executor.spin, daemon=True)
    executor_thread.start()

    server = HTTPServer(("0.0.0.0", 5000), PillboxHandler)
    print("藥盒手臂控制伺服器啟動於 http://localhost:5000")
    print("等待 Node-RED Dashboard 指令...")
    server.serve_forever()


if __name__ == "__main__":
    main()
