#!/usr/bin/env python3
"""Laboratory 2: publish a simple BlueROV2 motion sequence."""

import time

import rclpy
from std_msgs.msg import Float64MultiArray


# Each row is: (description, surge, heave, yaw, duration_seconds)
# Positive surge moves forward. Negative heave moves down.
MISSION = [
    ('descend', 0.00, -0.25, 0.00, 2.5),
    ('move forward', 0.30, 0.00, 0.00, 3.0),
    ('ascend', 0.00, +0.25, 0.00, 2.5),
]

COMMAND_TOPIC = '/inro/command'
PUBLISH_PERIOD = 0.1
PAUSE_BETWEEN_MOTIONS = 1.0


def publish_for(node, publisher, description, surge, heave, yaw, duration):
    """Publish one command repeatedly for the requested duration."""
    print(
        f'{description}: surge={surge:+.2f}, heave={heave:+.2f}, '
        f'yaw={yaw:+.2f}, duration={duration:.1f} s'
    )
    message = Float64MultiArray(data=[surge, heave, yaw])
    end_time = time.monotonic() + duration
    while time.monotonic() < end_time:
        publisher.publish(message)
        rclpy.spin_once(node, timeout_sec=PUBLISH_PERIOD)


def stop_vehicle(node, publisher, duration=PAUSE_BETWEEN_MOTIONS):
    """Publish zero effort for a short pause."""
    publish_for(node, publisher, 'pause', 0.0, 0.0, 0.0, duration)


def main():
    rclpy.init()
    node = rclpy.create_node('student_motion_sequence')
    publisher = node.create_publisher(
        Float64MultiArray, COMMAND_TOPIC, 10
    )

    try:
        deadline = time.monotonic() + 5.0
        while publisher.get_subscription_count() == 0:
            if time.monotonic() >= deadline:
                raise RuntimeError('Start demo.launch.py before this script')
            rclpy.spin_once(node, timeout_sec=0.1)

        for description, surge, heave, yaw, duration in MISSION:
            publish_for(
                node, publisher, description, surge, heave, yaw, duration
            )
            stop_vehicle(node, publisher)
    except KeyboardInterrupt:
        print('Mission interrupted by user.')
    finally:
        if rclpy.ok():
            for _ in range(5):
                publisher.publish(Float64MultiArray(data=[0.0, 0.0, 0.0]))
                rclpy.spin_once(node, timeout_sec=0.05)
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
        print('Mission finished. All command efforts are zero.')


if __name__ == '__main__':
    main()
