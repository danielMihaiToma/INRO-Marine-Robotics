import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, SetEnvironmentVariable, Shutdown
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    share = get_package_share_directory('inro_rov_demo')
    world = os.path.join(share, 'worlds', 'lab1_ctd.sdf')
    bridge = os.path.join(share, 'config', 'bridge.yaml')
    common = ['gz', 'sim', '-r', '-v', '3']
    return LaunchDescription([
        DeclareLaunchArgument('gui', default_value='true'),
        SetEnvironmentVariable('GZ_PARTITION', 'inro_lab1'),
        SetEnvironmentVariable(
            'GZ_SIM_RESOURCE_PATH',
            os.path.join(share, 'models') + ':'
            + os.environ.get('GZ_SIM_RESOURCE_PATH', '')
        ),
        ExecuteProcess(
            cmd=common + [world],
            condition=IfCondition(LaunchConfiguration('gui')),
            output='screen', on_exit=[Shutdown()]
        ),
        ExecuteProcess(
            cmd=common + ['-s', world],
            condition=UnlessCondition(LaunchConfiguration('gui')),
            output='screen', on_exit=[Shutdown()]
        ),
        Node(
            package='ros_gz_bridge', executable='parameter_bridge',
            name='inro_bridge', parameters=[{'config_file': bridge}],
            on_exit=[Shutdown()]
        ),
        Node(
            package='inro_rov_demo', executable='controller',
            name='inro_thruster_mixer', output='screen', on_exit=[Shutdown()]
        ),
        Node(
            package='inro_rov_demo', executable='ctd_sensor',
            name='inro_ctd_sensor', output='screen',
            parameters=[{'density_scale': 8.0}],
            on_exit=[Shutdown()]
        ),
    ])
