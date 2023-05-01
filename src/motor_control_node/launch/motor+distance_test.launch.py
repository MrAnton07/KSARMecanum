import os
from launch import LaunchDescription
from launch_ros.actions import Node

import time

def generate_launch_description():
    ld = LaunchDescription()

    motor_node = Node(
        package = 'motor_control_node',
        executable = 'motor_control',
        name = 'motor_control'
    )
    distance_node = Node(
        package = 'distance_node',
        executable = 'distance_publisher',
        name = 'distance_publisher'
    )

    ld.add_action(distance_node)
    ld.add_action(motor_node)

    return ld
