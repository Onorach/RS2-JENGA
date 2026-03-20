import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/fergus/ros2_ws/src/RS2-JENGA/install/motion_planning'
