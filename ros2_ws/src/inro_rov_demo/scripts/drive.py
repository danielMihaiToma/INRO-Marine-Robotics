#!/usr/bin/env python3
"""Publish a finite-duration normalized effort command for the simulation."""
import argparse
import math
import time
import rclpy
from std_msgs.msg import Float64MultiArray

def main():
    actions={'forward':[1,0,0], 'backward':[-1,0,0], 'up':[0,1,0], 'down':[0,-1,0], 'left':[0,0,1], 'right':[0,0,-1], 'stop':[0,0,0]}
    parser=argparse.ArgumentParser()
    parser.add_argument('action', choices=actions)
    parser.add_argument('--seconds', type=float, default=4.0)
    parser.add_argument('--power', type=float, default=0.4)
    args=parser.parse_args()
    if not math.isfinite(args.seconds) or not 0<args.seconds<=30 or not math.isfinite(args.power) or not 0<=args.power<=1:
        parser.error('seconds must be in (0,30]; power must be in [0,1]')
    rclpy.init()
    node=rclpy.create_node('inro_drive_command')
    pub=node.create_publisher(Float64MultiArray,'/inro/command',10)
    try:
        # Allow ROS discovery before starting the timed motion.
        discovery_end=time.monotonic()+5
        while pub.get_subscription_count()==0 and time.monotonic()<discovery_end:
            rclpy.spin_once(node,timeout_sec=0.1)
        if pub.get_subscription_count()==0:
            raise RuntimeError('No thruster mixer found. Start demo.launch.py first.')
        end=time.monotonic()+args.seconds
        while time.monotonic()<end:
            pub.publish(Float64MultiArray(data=[float(v*args.power) for v in actions[args.action]]))
            rclpy.spin_once(node,timeout_sec=0.1)
    except KeyboardInterrupt:
        pass
    finally:
        for _ in range(3):
            pub.publish(Float64MultiArray(data=[0.0,0.0,0.0]))
            rclpy.spin_once(node,timeout_sec=0.05)
        node.destroy_node()
        if rclpy.ok(): rclpy.shutdown()
if __name__=='__main__': main()
