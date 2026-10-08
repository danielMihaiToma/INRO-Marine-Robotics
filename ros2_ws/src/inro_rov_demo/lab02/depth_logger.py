#!/usr/bin/env python3
"""Laboratory 2 example: subscribe to depth and save it in a CSV file."""

import csv
from pathlib import Path

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64


OUTPUT_FILE = Path(__file__).with_name('depth_log.csv')


class DepthLogger(Node):
    def __init__(self):
        super().__init__('depth_logger')
        self.start_time = self.get_clock().now()
        self.last_print_second = -1

        self.csv_file = OUTPUT_FILE.open('w', newline='', encoding='utf-8')
        self.writer = csv.writer(self.csv_file)
        self.writer.writerow(['time_s', 'depth_m'])

        self.subscription = self.create_subscription(
            Float64,
            '/inro/depth',
            self.depth_callback,
            10,
        )

        self.get_logger().info(f'Recording depth in {OUTPUT_FILE}')

    def depth_callback(self, msg):
        """Run whenever a new depth message arrives."""
        elapsed = (self.get_clock().now() - self.start_time).nanoseconds / 1e9
        depth = msg.data

        self.writer.writerow([f'{elapsed:.3f}', f'{depth:.4f}'])
        self.csv_file.flush()

        whole_second = int(elapsed)
        if whole_second != self.last_print_second:
            self.last_print_second = whole_second
            print(f't={elapsed:5.1f} s  depth={depth:6.2f} m')

    def close_csv(self):
        if not self.csv_file.closed:
            self.csv_file.close()


def main():
    rclpy.init()
    node = DepthLogger()
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
