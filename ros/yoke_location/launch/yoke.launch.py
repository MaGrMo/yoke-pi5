"""Starts the GPS reader, location monitor and notifier. Nodes restart if they crash."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    def node(executable, parameters=None):
        return Node(package='yoke_location', executable=executable, name=executable,
                    parameters=parameters or [], output='screen',
                    respawn=True, respawn_delay=5.0)

    return LaunchDescription([
        DeclareLaunchArgument('gps_port', default_value='/dev/ttyAMA0'),
        DeclareLaunchArgument('gps_baud', default_value='9600'),
        DeclareLaunchArgument('threshold_m', default_value='10000.0'),

        node('notifier'),
        node('gps_node', [{
            'port': LaunchConfiguration('gps_port'),
            'baud': LaunchConfiguration('gps_baud'),
        }]),
        node('location_monitor', [{
            'threshold_m': LaunchConfiguration('threshold_m'),
        }]),
    ])
