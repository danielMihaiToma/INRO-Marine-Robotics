#!/usr/bin/env python3
"""Student starter for INRO Laboratory 2.

Complete the two controller functions marked TODO. The ROS communication and
mission sequence are provided so the first exercise stays focused on control.
"""

import time

import rclpy
from nav_msgs.msg import Odometry
from rclpy.node import Node
from std_msgs.msg import Float64, Float64MultiArray, String


QUICK_TEST = False
FIRST_DEPTH = 5.0 if QUICK_TEST else 20.0
SECOND_DEPTH = 12.0 if QUICK_TEST else 50.0
HOLD_SECONDS = 5.0 if QUICK_TEST else 60.0
DESCENT_SPEED = 0.5
ASCENT_SPEED = 0.5
RECOVERY_DEPTH = 2.0
DEPTH_TOLERANCE = 0.25
MAX_EFFORT = 0.65


def clamp(value, lower, upper):
    return max(lower, min(upper, value))


class StudentDepthMission(Node):
    def __init__(self):
        super().__init__('student_depth_mission')
        self.depth = None
        self.depth_rate = 0.0
        self.phase = 'DESCEND_1'
        self.phase_started = time.monotonic()
        self.last_report = 0.0
        self.command_pub = self.create_publisher(
            Float64MultiArray, '/inro/command', 10
        )
        self.target_pub = self.create_publisher(
            Float64, '/inro/target_depth', 10
        )
        self.effort_pub = self.create_publisher(
            Float64, '/inro/vertical_effort', 10
        )
        self.state_pub = self.create_publisher(String, '/inro/mission/state', 10)
        self.create_subscription(Odometry, '/inro/odometry', self.odometry, 10)
        self.create_timer(0.1, self.control)

    def odometry(self, msg):
        # Gazebo uses z upward. Oceanographic depth is positive downward.
        self.depth = max(0.0, -msg.pose.pose.position.z)
        self.depth_rate = -msg.twist.twist.linear.z

    def effort_for_speed(self, desired_depth_rate):
        """Return normalized vertical effort for a requested depth rate.

        TODO 1:
        - Compute desired_depth_rate - self.depth_rate.
        - Convert the error to effort with a proportional gain.
        - Remember: negative heave effort moves the ROV down.
        - Clamp the result between -MAX_EFFORT and MAX_EFFORT.
        """
        return 0.0

    def effort_for_depth_hold(self, target_depth):
        """Return normalized vertical effort to hold target_depth.

        TODO 2:
        - Compute target_depth - self.depth.
        - Use proportional feedback and vertical-speed damping.
        - Clamp the result. Start with Kp=0.16 and Kd=0.35.
        - Optional: add a small integral term and anti-windup.
        """
        return 0.0

    def change_phase(self, phase):
        self.phase = phase
        self.phase_started = time.monotonic()
        self.get_logger().info(f'Mission state: {phase}')

    def travel_effort(self, target, speed):
        distance = target - self.depth
        direction = 1.0 if distance > 0 else -1.0
        requested_rate = direction * min(speed, max(0.05, 0.5 * abs(distance)))
        return self.effort_for_speed(requested_rate)

    def control(self):
        if self.depth is None:
            return
        if self.phase == 'DESCEND_1':
            target = FIRST_DEPTH
            effort = self.travel_effort(target, DESCENT_SPEED)
            if abs(self.depth - target) <= DEPTH_TOLERANCE:
                self.change_phase('HOLD_1')
        elif self.phase == 'HOLD_1':
            target = FIRST_DEPTH
            effort = self.effort_for_depth_hold(target)
            if time.monotonic() - self.phase_started >= HOLD_SECONDS:
                self.change_phase('DESCEND_2')
        elif self.phase == 'DESCEND_2':
            target = SECOND_DEPTH
            effort = self.travel_effort(target, DESCENT_SPEED)
            if abs(self.depth - target) <= DEPTH_TOLERANCE:
                self.change_phase('HOLD_2')
        elif self.phase == 'HOLD_2':
            target = SECOND_DEPTH
            effort = self.effort_for_depth_hold(target)
            if time.monotonic() - self.phase_started >= HOLD_SECONDS:
                self.change_phase('ASCEND')
        elif self.phase == 'ASCEND':
            target = RECOVERY_DEPTH
            effort = self.travel_effort(target, ASCENT_SPEED)
            if abs(self.depth - target) <= DEPTH_TOLERANCE:
                self.change_phase('COMPLETE')
        else:
            target = RECOVERY_DEPTH
            effort = 0.0
        self.command_pub.publish(
            Float64MultiArray(data=[0.0, float(effort), 0.0])
        )
        self.target_pub.publish(Float64(data=float(target)))
        self.effort_pub.publish(Float64(data=float(effort)))
        self.state_pub.publish(String(data=self.phase))
        now = time.monotonic()
        if now - self.last_report >= 1.0:
            self.last_report = now
            self.get_logger().info(
                f'{self.phase}: depth={self.depth:5.2f} m, '
                f'target={target:5.2f} m, '
                f'depth_rate={self.depth_rate:+.2f} m/s, '
                f'heave_effort={effort:+.2f}'
            )

    def stop(self):
        for _ in range(4):
            self.command_pub.publish(Float64MultiArray(data=[0.0, 0.0, 0.0]))
            rclpy.spin_once(self, timeout_sec=0.05)


def main():
    rclpy.init()
    node = StudentDepthMission()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Mission interrupted; stopping thrusters.')
    finally:
        node.stop()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
