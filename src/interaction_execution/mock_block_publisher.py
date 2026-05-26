#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from jenga_interfaces.msg import JengaBlockStates, JengaBlockState
from geometry_msgs.msg import Pose

class JengaMockPublisher(Node):
    def __init__(self):
        super().__init__('jenga_mock_publisher')
        self.publisher_ = self.create_publisher(JengaBlockStates, '/jenga/block_states', 10)
        self.timer = self.create_timer(1.0, self.timer_callback)
        self.get_logger().info("Jenga Mock Publisher has started. Emulating 6 incomplete layers...")

    def timer_callback(self):
        msg = JengaBlockStates()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "camera_color_optical_frame"

        # Shifted position values from 1-3 to 0-2 (0=Left, 1=Middle, 2=Right)
        mock_tower_layout = [
            # Layer 0: Missing position 2
            {"layer": 0, "pos": 0, "id": 0, "colour": "red"},
            {"layer": 0, "pos": 1, "id": 1, "colour": "green"},
            {"layer": 0, "pos": 2, "id": 2, "colour": "purple"},
            
            # Layer 1: Missing positions 0 and 2
            {"layer": 1, "pos": 0, "id": 3, "colour": "green"},
            {"layer": 1, "pos": 1, "id": 4, "colour": "blue"},
            {"layer": 1, "pos": 2, "id": 5, "colour": "purple"},
            
            # Layer 2: Missing position 1
            {"layer": 2, "pos": 0, "id": 4, "colour": "yellow"},
            {"layer": 2, "pos": 2, "id": 5, "colour": "natural"},
            
            # Layer 3: Missing position 0
            
            {"layer": 3, "pos": 2, "id": 7, "colour": "black"},
            
            # Layer 4: Missing positions 1 and 2
            {"layer": 4, "pos": 0, "id": 12, "colour": "red"},
            {"layer": 4, "pos": 1, "id": 13, "colour": "purple"},
            {"layer": 4, "pos": 2, "id": 14, "colour": "green"},         
            
            # Layer 5 (Topmost Layer): Missing position 1
            {"layer": 5, "pos": 0, "id": 9, "colour": "green"}
               
        ]

        blocks_list = []
        for item in mock_tower_layout:
            block = JengaBlockState()
            block.block_id = item["id"]
            block.colour = item["colour"]
            block.layer = item["layer"]
            block.layer_position = item["pos"] # Now values 0, 1, or 2
            
            block.pose = Pose()
            block.pose.orientation.w = 1.0
            blocks_list.append(block)

        msg.blocks = blocks_list
        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = JengaMockPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()