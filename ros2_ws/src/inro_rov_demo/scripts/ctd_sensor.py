#!/usr/bin/env python3
"""Publish interpolated CTD profile values at the simulated ROV depth."""

import csv
from pathlib import Path

import rclpy
from ament_index_python.packages import get_package_share_directory
from nav_msgs.msg import Odometry
from rclpy.node import Node
from std_msgs.msg import Float64


class CtdSensor(Node):
    def __init__(self):
        super().__init__('inro_ctd_sensor')
        default_profile = str(
            Path(get_package_share_directory('inro_rov_demo'))
            / 'profiles' / 'depth_temperature_density.csv'
        )
        self.declare_parameter('profile_file', default_profile)
        self.declare_parameter('density_scale', 8.0)
        self.declare_parameter('profile_reference_density', 1024.0)
        self.declare_parameter('simulation_reference_density', 1000.0)
        self.profile = self._read_profile(
            Path(self.get_parameter('profile_file').value)
        )
        self.density_scale = float(self.get_parameter('density_scale').value)
        self.profile_reference = float(
            self.get_parameter('profile_reference_density').value
        )
        self.simulation_reference = float(
            self.get_parameter('simulation_reference_density').value
        )
        self.depth_pub = self.create_publisher(Float64, '/inro/ctd/depth', 10)
        self.temperature_pub = self.create_publisher(
            Float64, '/inro/ctd/temperature', 10
        )
        self.density_pub = self.create_publisher(
            Float64, '/inro/ctd/density', 10
        )
        self.sim_density_pub = self.create_publisher(
            Float64, '/inro/ctd/simulation_density', 10
        )
        self.create_subscription(Odometry, '/inro/odometry', self._update, 10)

    @staticmethod
    def _read_profile(path):
        with path.open(newline='', encoding='utf-8') as stream:
            rows = [
                (float(row['depth [m]']),
                 float(row['temperature [degC]']),
                 float(row['density [kg/m3]']))
                for row in csv.DictReader(stream)
            ]
        if len(rows) < 2 or any(rows[i][0] >= rows[i + 1][0]
                                for i in range(len(rows) - 1)):
            raise ValueError('CTD profile needs at least two increasing depths')
        return rows

    def _interpolate(self, depth):
        depth = max(self.profile[0][0], min(depth, self.profile[-1][0]))
        for lower, upper in zip(self.profile, self.profile[1:]):
            if depth <= upper[0]:
                fraction = (depth - lower[0]) / (upper[0] - lower[0])
                temperature = lower[1] + fraction * (upper[1] - lower[1])
                density = lower[2] + fraction * (upper[2] - lower[2])
                return temperature, density
        return self.profile[-1][1], self.profile[-1][2]

    def _update(self, msg):
        depth = max(0.0, -msg.pose.pose.position.z)
        temperature, density = self._interpolate(depth)
        simulation_density = self.simulation_reference + self.density_scale * (
            density - self.profile_reference
        )
        self.depth_pub.publish(Float64(data=depth))
        self.temperature_pub.publish(Float64(data=temperature))
        self.density_pub.publish(Float64(data=density))
        self.sim_density_pub.publish(Float64(data=simulation_density))


def main():
    rclpy.init()
    node = CtdSensor()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
