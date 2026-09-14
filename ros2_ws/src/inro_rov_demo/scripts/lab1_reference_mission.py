#!/usr/bin/env python3
"""Reference solution for the INRO Lab 1 depth mission."""

import argparse
import math
import time

import rclpy
from nav_msgs.msg import Odometry
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from std_msgs.msg import Float64, Float64MultiArray, String


def clamp(value, lower, upper):
    return max(lower, min(upper, value))


class DepthMission(Node):
    def __init__(self, args):
        super().__init__('inro_lab1_depth_mission')
        self.args = args
        self.depth = None
        self.depth_rate = 0.0
        self.phase = 'WAITING_FOR_ODOMETRY'
        self.phase_started = time.monotonic()
        self.last_update = time.monotonic()
        self.last_report = 0.0
        self.integral = 0.0
        self.speed_integral = 0.0
        self.finished = False
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
        self.create_subscription(Odometry, '/inro/odometry', self._odometry, 10)
        self.create_timer(0.1, self._control)

    def _odometry(self, msg):
        self.depth = max(0.0, -msg.pose.pose.position.z)
        self.depth_rate = -msg.twist.twist.linear.z

    def _set_phase(self, phase):
        self.phase = phase
        self.phase_started = time.monotonic()
        self.integral = 0.0
        self.speed_integral = 0.0
        self.get_logger().info(f'Mission state: {phase}')

    def _speed_effort(self, target_depth, speed, dt):
        distance = target_depth - self.depth
        direction = 1.0 if distance > 0 else -1.0
        desired_rate = direction * min(speed, max(0.05, 0.5 * abs(distance)))
        rate_error = desired_rate - self.depth_rate
        candidate = clamp(self.speed_integral + rate_error * dt, -2.0, 2.0)
        # Positive heave moves up, while positive depth rate moves down.
        unsaturated = (-self.args.speed_gain * rate_error
                       - self.args.speed_ki * candidate)
        effort = clamp(unsaturated, -self.args.max_effort,
                       self.args.max_effort)
        if effort == unsaturated:
            self.speed_integral = candidate
        return effort

    def _hold_effort(self, target_depth, dt):
        error = target_depth - self.depth
        candidate = clamp(self.integral + error * dt, -5.0, 5.0)
        unsaturated = (-self.args.depth_kp * error
                       + self.args.depth_kd * self.depth_rate
                       - self.args.depth_ki * candidate)
        effort = clamp(unsaturated, -self.args.max_effort,
                       self.args.max_effort)
        if effort == unsaturated:
            self.integral = candidate
        return effort

    def _publish(self, target, effort):
        self.command_pub.publish(
            Float64MultiArray(data=[0.0, float(effort), 0.0])
        )
        self.target_pub.publish(Float64(data=float(target)))
        self.effort_pub.publish(Float64(data=float(effort)))
        self.state_pub.publish(String(data=self.phase))

    def _report(self, now, target, effort):
        if now - self.last_report >= 1.0:
            self.last_report = now
            self.get_logger().info(
                f'{self.phase}: depth={self.depth:5.2f} m, '
                f'target={target:5.2f} m, '
                f'depth_rate={self.depth_rate:+.2f} m/s, '
                f'heave_effort={effort:+.2f}'
            )

    def _control(self):
        now = time.monotonic()
        dt = min(0.2, max(0.001, now - self.last_update))
        self.last_update = now
        if self.depth is None:
            return
        if self.phase == 'WAITING_FOR_ODOMETRY':
            self._set_phase('DESCEND_TO_FIRST_DEPTH')

        if self.phase == 'DESCEND_TO_FIRST_DEPTH':
            target = self.args.first_depth
            effort = self._speed_effort(target, self.args.descent_speed, dt)
            if abs(self.depth - target) <= self.args.depth_tolerance:
                self._set_phase('HOLD_FIRST_DEPTH')
        elif self.phase == 'HOLD_FIRST_DEPTH':
            target = self.args.first_depth
            effort = self._hold_effort(target, dt)
            if now - self.phase_started >= self.args.hold_seconds:
                self._set_phase('DESCEND_TO_SECOND_DEPTH')
        elif self.phase == 'DESCEND_TO_SECOND_DEPTH':
            target = self.args.second_depth
            effort = self._speed_effort(target, self.args.descent_speed, dt)
            if abs(self.depth - target) <= self.args.depth_tolerance:
                self._set_phase('HOLD_SECOND_DEPTH')
        elif self.phase == 'HOLD_SECOND_DEPTH':
            target = self.args.second_depth
            effort = self._hold_effort(target, dt)
            if now - self.phase_started >= self.args.hold_seconds:
                self._set_phase('ASCEND_TO_RECOVERY_DEPTH')
        elif self.phase == 'ASCEND_TO_RECOVERY_DEPTH':
            target = self.args.recovery_depth
            effort = self._speed_effort(target, self.args.ascent_speed, dt)
            if abs(self.depth - target) <= self.args.depth_tolerance:
                self._set_phase('COMPLETE')
        else:
            target = self.args.recovery_depth
            effort = 0.0
            self.finished = True
        self._publish(target, effort)
        self._report(now, target, effort)

    def stop(self):
        for _ in range(4):
            self._publish(self.args.recovery_depth, 0.0)
            rclpy.spin_once(self, timeout_sec=0.05)


def parse_args():
    parser = argparse.ArgumentParser(description='Run the INRO depth mission')
    parser.add_argument('--first-depth', type=float, default=20.0)
    parser.add_argument('--second-depth', type=float, default=50.0)
    parser.add_argument('--hold-seconds', type=float, default=60.0)
    parser.add_argument('--descent-speed', type=float, default=0.5)
    parser.add_argument('--ascent-speed', type=float, default=0.5)
    parser.add_argument('--recovery-depth', type=float, default=2.0)
    parser.add_argument('--depth-tolerance', type=float, default=0.25)
    parser.add_argument('--speed-gain', type=float, default=1.0)
    parser.add_argument('--speed-ki', type=float, default=0.35)
    parser.add_argument('--depth-kp', type=float, default=0.16)
    parser.add_argument('--depth-ki', type=float, default=0.025)
    parser.add_argument('--depth-kd', type=float, default=0.35)
    parser.add_argument('--max-effort', type=float, default=0.65)
    args, ros_args = parser.parse_known_args()
    if not (0 < args.recovery_depth < args.first_depth < args.second_depth < 60):
        parser.error('depths must satisfy 0 < recovery < first < second < 60 m')
    if not (0 < args.descent_speed <= 1 and 0 < args.ascent_speed <= 1):
        parser.error('speeds must be in (0, 1] m/s')
    if not (0 <= args.hold_seconds <= 600):
        parser.error('hold-seconds must be between 0 and 600')
    return args, ros_args


def main():
    args, ros_args = parse_args()
    rclpy.init(args=ros_args)
    node = DepthMission(args)
    try:
        while rclpy.ok() and not node.finished:
            rclpy.spin_once(node, timeout_sec=0.1)
        node.get_logger().info('Mission complete; vertical thrust is zero.')
    except (KeyboardInterrupt, ExternalShutdownException):
        if rclpy.ok():
            node.get_logger().info('Mission interrupted; stopping thrusters.')
    finally:
        if rclpy.ok():
            node.stop()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
