from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='investigation_robot',
            executable='sensor_node',
            name='sensor_node',
            output='screen'
        ),
        Node(
            package='investigation_robot',
            executable='teleop_node',
            name='teleop_node',
            output='screen'
        ),
        Node(
            package='investigation_robot',
            executable='logger_node',
            name='logger_node',
            output='screen'
        ),
    ])