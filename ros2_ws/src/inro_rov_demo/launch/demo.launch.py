import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, SetEnvironmentVariable, Shutdown
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    share = get_package_share_directory('inro_rov_demo')
    world = os.path.join(share, 'worlds', 'pool.sdf')
    return LaunchDescription([
        DeclareLaunchArgument('gui', default_value='true'),
        SetEnvironmentVariable('GZ_PARTITION', 'inro_bluerov2'),
        SetEnvironmentVariable('GZ_SIM_RESOURCE_PATH', os.path.join(share, 'models') + ':' + os.environ.get('GZ_SIM_RESOURCE_PATH','')),
        ExecuteProcess(cmd=['gz','sim','-r','-v','3',world], condition=IfCondition(LaunchConfiguration('gui')), output='screen', on_exit=[Shutdown()]),
        ExecuteProcess(cmd=['gz','sim','-r','-v','3','-s',world], condition=UnlessCondition(LaunchConfiguration('gui')), output='screen', on_exit=[Shutdown()]),
        Node(package='ros_gz_bridge', executable='parameter_bridge', name='inro_bridge', parameters=[{'config_file':os.path.join(share,'config','bridge.yaml')}], on_exit=[Shutdown()]),
        Node(package='inro_rov_demo', executable='controller', name='inro_thruster_mixer', output='screen', on_exit=[Shutdown()]),
    ])
