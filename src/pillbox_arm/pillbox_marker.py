import rclpy
from rclpy.node import Node
from visualization_msgs.msg import Marker, MarkerArray
from geometry_msgs.msg import Point
import time

DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
TIMES = ["am", "pm", "eve"]

TIME_COLORS = {
    "am":  (0.2, 0.8, 0.2),
    "pm":  (0.8, 0.8, 0.2),
    "eve": (0.9, 0.5, 0.1),
}

class PillboxMarker(Node):
    def __init__(self):
        super().__init__("pillbox_marker")
        self.pub = self.create_publisher(MarkerArray, "/pillbox_markers", 10)
        self.taken_slots = set()
        self.timer = self.create_timer(0.5, self.publish_markers)
        self.get_logger().info("藥盒 Marker 發布中...")

    def publish_markers(self):
        marker_array = MarkerArray()
        marker_id = 0

        for di, day in enumerate(DAYS):
            for ti, t in enumerate(TIMES):
                slot = f"{day}_{t}"
                marker = Marker()
                marker.header.frame_id = "world"
                marker.header.stamp = self.get_clock().now().to_msg()
                marker.ns = "pillbox"
                marker.id = marker_id
                marker.type = Marker.CUBE
                marker.action = Marker.ADD

                marker.pose.position.x = 0.4 - di * 0.05
                marker.pose.position.y = 0.08 - ti * 0.08
                marker.pose.position.z = 0.05
                marker.pose.orientation.w = 1.0

                marker.scale.x = 0.04
                marker.scale.y = 0.06
                marker.scale.z = 0.04

                if slot in self.taken_slots:
                    marker.color.r = 0.3
                    marker.color.g = 0.3
                    marker.color.b = 0.3
                    marker.color.a = 1.0
                else:
                    r, g, b = TIME_COLORS[t]
                    marker.color.r = r
                    marker.color.g = g
                    marker.color.b = b
                    marker.color.a = 1.0

                marker_array.markers.append(marker)
                marker_id += 1

        # 藥盒底座
        base = Marker()
        base.header.frame_id = "world"
        base.header.stamp = self.get_clock().now().to_msg()
        base.ns = "pillbox"
        base.id = marker_id
        base.type = Marker.CUBE
        base.action = Marker.ADD
        base.pose.position.x = 0.25
        base.pose.position.y = 0.0
        base.pose.position.z = 0.01
        base.pose.orientation.w = 1.0
        base.scale.x = 0.37
        base.scale.y = 0.27
        base.scale.z = 0.02
        base.color.r = 0.9
        base.color.g = 0.9
        base.color.b = 0.9
        base.color.a = 0.8
        marker_array.markers.append(base)

        self.pub.publish(marker_array)

    def mark_taken(self, slot):
        self.taken_slots.add(slot)
        self.get_logger().info(f"藥格 {slot} 已取藥（變灰）")

def main():
    rclpy.init()
    node = PillboxMarker()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == "__main__":
    main()
