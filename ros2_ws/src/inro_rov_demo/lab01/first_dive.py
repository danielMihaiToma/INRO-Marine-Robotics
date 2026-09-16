#!/usr/bin/env python3
"""Lab 1: send one short vertical-effort command to the simulated BlueROV2.

Change only HEAVE_EFFORT for the student exercise. This is normalized thrust
effort, not a speed in m/s. Negative values command downward thrust.
"""

import time

import rclpy
from std_msgs.msg import Float64MultiArray


# Student experiment: predict what this value will do, then try -0.20.
HEAVE_EFFORT = -0.40
DURATION_SECONDS = 4.0


def main():
    if not -0.65 <= HEAVE_EFFORT <= 0.65:
        raise ValueError('Keep HEAVE_EFFORT between -0.65 and +0.65')
    if not 0.0 < DURATION_SECONDS <= 10.0:
        raise ValueError('Keep DURATION_SECONDS between 0 and 10 seconds')

    rclpy.init()
    node = rclpy.create_node('inro_first_dive')
    publisher = node.create_publisher(Float64MultiArray, '/inro/command', 10)

    try:
        # Give ROS 2 a moment to discover the thruster mixer.
        discovery_deadline = time.monotonic() + 5.0
        while publisher.get_subscription_count() == 0:
            if time.monotonic() >= discovery_deadline:
                raise RuntimeError('Start demo.launch.py before running this script')
            rclpy.spin_once(node, timeout_sec=0.1)

        print(f'Sending heave effort {HEAVE_EFFORT:+.2f} for {DURATION_SECONDS:.1f} s')
        start = time.monotonic()
        while time.monotonic() - start < DURATION_SECONDS:
            # [surge, heave, yaw]: only heave is used in this exercise.
            publisher.publish(
                Float64MultiArray(data=[0.0, HEAVE_EFFORT, 0.0])
            )
            rclpy.spin_once(node, timeout_sec=0.1)
    except KeyboardInterrupt:
        print('Interrupted by user.')
    finally:
        # Zero effort does not instantly stop motion or hold depth.
        if rclpy.ok():
            for _ in range(3):
                publisher.publish(Float64MultiArray(data=[0.0, 0.0, 0.0]))
                rclpy.spin_once(node, timeout_sec=0.05)
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
        print('Command ended; observe the depth after thrust returns to zero.')


if __name__ == '__main__':
    main()
