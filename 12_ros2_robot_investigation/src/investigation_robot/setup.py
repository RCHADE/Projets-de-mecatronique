from setuptools import setup
import os
from glob import glob

package_name = 'investigation_robot'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Mohamed Ahmed',
    maintainer_email='mohamed-salem.mohamed-ahmed@etu.mines-ales.fr',
    description='ROS2 nodes for robot investigation simulation',
    license='MIT',
    entry_points={
        'console_scripts': [
            'sensor_node = investigation_robot.sensor_node:main',
            'teleop_node = investigation_robot.teleop_node:main',
            'logger_node = investigation_robot.logger_node:main',
            'visu_node = investigation_robot.visu_node:main',
        ],
    },
)