#!/usr/bin/env python3
"""Laboratory 2: record BlueROV2 position and depth in a CSV file."""

import csv
from pathlib import Path

import rclpy
from nav_msgs.msg import Odometry
from rclpy.node import Node
from std_msgs.msg import Float64


OUTPUT_FILE = Path(__file__).with_name('rov_trajectory.csv')


class TrajectoryLogger(Node):
    def __init__(self):
        super().__init__('student_trajectory_logger')
        self.latest_depth = None
        self.start_time = self.get_clock().now()
        self.last_print_second = -1

        self.csv_file = OUTPUT_FILE.open('w', newline='', encoding='utf-8')
        self.writer = csv.writer(self.csv_file)
        self.writer.writerow(['time_s', 'x_m', 'y_m', 'z_m', 'depth_m'])

        # A subscriber connects a topic to a callback function.
        self.create_subscription(
            Float64, '/inro/depth', self.depth_callback, 10
        )
        self.create_subscription(
            Odometry, '/inro/odometry', self.odometry_callback, 10
        )

        self.get_logger().info(f'Recording trajectory in {OUTPUT_FILE}')

    def depth_callback(self, msg):
        """Remember the most recent depth message."""
        self.latest_depth = msg.data

    def odometry_callback(self, msg):
        """Write one row whenever a new odometry message arrives."""
        position = msg.pose.pose.position
        elapsed = (self.get_clock().now() - self.start_time).nanoseconds / 1e9
        depth = '' if self.latest_depth is None else self.latest_depth

        self.writer.writerow([
            f'{elapsed:.3f}',
            f'{position.x:.4f}',
            f'{position.y:.4f}',
            f'{position.z:.4f}',
            '' if depth == '' else f'{depth:.4f}',
        ])
        self.csv_file.flush()

        whole_second = int(elapsed)
        if whole_second != self.last_print_second:
            self.last_print_second = whole_second
            depth_text = 'waiting' if depth == '' else f'{depth:.2f} m'
            print(
                f't={elapsed:5.1f} s  '
                f'x={position.x:+6.2f}  y={position.y:+6.2f}  '
                f'z={position.z:+6.2f}  depth={depth_text}'
            )

    def close_csv(self):
        if not self.csv_file.closed:
            self.csv_file.close()


def main():
    rclpy.init()
    node = TrajectoryLogger()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.close_csv()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
        print(f'CSV saved to {OUTPUT_FILE}')


if __name__ == '__main__':
    main()
