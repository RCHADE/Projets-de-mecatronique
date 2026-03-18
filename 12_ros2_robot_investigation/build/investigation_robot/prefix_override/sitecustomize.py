import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/root/GitHub/Projets-de-mecatronique/12_ros2_robot_investigation/install/investigation_robot'
