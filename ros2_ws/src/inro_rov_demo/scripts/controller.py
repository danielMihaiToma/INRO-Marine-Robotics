#!/usr/bin/env python3
"""Direct normalized effort mixer. Not a velocity or depth controller."""
import math
import time
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64, Float64MultiArray
from nav_msgs.msg import Odometry

class Mixer(Node):
    def __init__(self):
        super().__init__('inro_thruster_mixer')
        self.command = [0.0, 0.0, 0.0]
        self.last_command = 0.0
        self.outputs = [self.create_publisher(Float64, f'/inro/thruster_{i}/force', 10) for i in range(1,7)]
        self.depth = self.create_publisher(Float64, '/inro/depth', 10)
        self.create_subscription(Float64MultiArray, '/inro/command', self.receive, 10)
        self.create_subscription(Odometry, '/inro/odometry', self.feedback, 10)
        self.create_timer(0.05, self.update)

    def receive(self, msg):
        if len(msg.data) != 3 or not all(math.isfinite(v) for v in msg.data):
            self.command = [0.0, 0.0, 0.0]
            self.last_command = 0.0
            return
        self.command = [max(-1.0, min(1.0, v)) for v in msg.data]
        self.last_command = time.monotonic()

    def feedback(self, msg):
        self.depth.publish(Float64(data=-msg.pose.pose.position.z))

    def update(self):
        surge, heave, yaw = self.command if time.monotonic()-self.last_command < 0.5 else (0.0,0.0,0.0)
        # Positive surge: forward; positive heave: up; positive yaw: turn left.
        values = [-surge-yaw, -surge+yaw, surge+yaw, surge-yaw, -heave, -heave]
        for pub, value in zip(self.outputs, values):
            pub.publish(Float64(data=5.0*max(-1.0,min(1.0,value))))

def main():
    rclpy.init()
    node = Mixer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        for pub in node.outputs:
            pub.publish(Float64(data=0.0))
        node.destroy_node()
        if rclpy.ok(): rclpy.shutdown()
if __name__ == '__main__': main()
