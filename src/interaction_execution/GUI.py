#!/usr/bin/env python3

import threading
import json
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import Image
from std_msgs.msg import String, Int8MultiArray
from std_srvs.srv import SetBool
from cv_bridge import CvBridge
import tkinter as tk
from PIL import Image as PILImage, ImageTk

try:
    _PIL_RESAMPLE = PILImage.Resampling.LANCZOS
except AttributeError:
    _PIL_RESAMPLE = PILImage.LANCZOS

# --- Color Definitions ---
COLOUR_YELLOW = "#ffff00"  
COLOUR_BLACK = "#000000"   
COLOUR_LIGHT_GRAY = "#D3D3D3" 
COLOUR_WHITE = "#FFFFFF"   
COLOUR_RED = "#FF0000"     

BLOCK_COLOURS = {
    "red": "#FF0000",
    "green": "#00FF00",
    "blue": "#0000FF",
    "yellow": "#FFFF00",
    "black": "#000000",
    "natural": "#DEB887",
    "purple": "#800080",
    "none": "#FFFFFF",
    "unknown": "#FFFFFF",
}

def _layers_from_tower_message(data) -> list:
    if isinstance(data, list):
        layers = data
    elif isinstance(data, dict):
        layers = data.get("layers", data.get("tower", []))
    else:
        layers = []
    return sorted(layers, key=lambda layer: layer.get("layer", 0))

class RealSenseCameraNode(Node):
    def __init__(self):
        super().__init__('realsense_gui_node')
        self.topic_name = '/camera/camera/color/image_raw'
        self.state_topic = '/robot_state'
        self.override_topic = '/ee_override_array'
        self.top_layer_topic = '/top_layer_state'
        self.goal_topic = '/selected_goal'

        qos_profile = QoSProfile(reliability=ReliabilityPolicy.BEST_EFFORT, history=HistoryPolicy.KEEP_LAST, depth=1)
        self.subscription = self.create_subscription(Image, self.topic_name, self.listener_callback, qos_profile)
        self.state_subscription = self.create_subscription(String, self.state_topic, self.state_callback, 10)
        self.top_layer_sub = self.create_subscription(String, self.top_layer_topic, self.top_layer_callback, 10)
        self.override_pub = self.create_publisher(Int8MultiArray, self.override_topic, 10)
        self.goal_pub = self.create_publisher(String, self.goal_topic, 10)
        self.estop_client = self.create_client(SetBool, '/estop')
        self.bridge = CvBridge()
        self.cv_image = None
        self.new_image_flag = False
        self.robot_state_str = None
        self.top_layer_data = None 
        self.image_lock = threading.Lock()
        
    def listener_callback(self, msg):
        try:
            cv_img = self.bridge.imgmsg_to_cv2(msg, desired_encoding='rgb8')
            with self.image_lock:
                self.cv_image = cv_img
                self.new_image_flag = True
        except Exception as e: self.get_logger().error(f"CvBridge Error: {e}")

    def state_callback(self, msg): self.robot_state_str = msg.data
    def top_layer_callback(self, msg):
        try: self.top_layer_data = json.loads(msg.data)
        except Exception as e: self.get_logger().error(f"Failed to parse tower data JSON: {e}")

    def publish_override(self, boolean_array):
        msg = Int8MultiArray()
        msg.data = [int(val) for val in boolean_array]
        self.override_pub.publish(msg)

    def publish_goal(self, goal_matrix):
        msg = String()
        msg.data = json.dumps(goal_matrix)
        self.goal_pub.publish(msg)

    def call_estop_service(self, state: bool):
        if not self.estop_client.wait_for_service(timeout_sec=1.0): return
        request = SetBool.Request(); request.data = state
        self.estop_client.call_async(request)

class JengaInterfaceApp:
    def __init__(self, root, ros_node):
        self.root = root
        self.ros_node = ros_node
        self.root.title("JENGA Tower Interface")
        self.root.configure(bg=COLOUR_BLACK)
        self.ee_override_array = [False, False, True] 
        self.estop_active = False 
        self.sequence_state = "WAITING_PICK"
        self.pick_selection = None
        self.place_selection = None
        self.buttons = {}
        self.goal_buttons = {}
        self.setup_ui()
        self.refresh_buttons()
        self.update_gui_loop()

    def get_highest_incomplete_layer(self):
        if not self.ros_node.top_layer_data: return 0
        layers_list = _layers_from_tower_message(self.ros_node.top_layer_data)
        for layer in range(len(layers_list) - 1, -1, -1):
            blocks = layers_list[layer].get("blocks", [])
            if any(not b.get("present", False) for b in blocks): return layer
        return 0

    def _is_position_empty(self, layer, pos_idx):
        layers_list = _layers_from_tower_message(self.ros_node.top_layer_data)
        if layer < len(layers_list):
            blocks = layers_list[layer].get("blocks", [])
            block_idx = pos_idx - 1
            if block_idx < len(blocks): return not blocks[block_idx].get("present", False)
        return True

    def setup_ui(self):
        # ... (UI setup remains same as your original, abbreviated for conciseness)
        # Note: Ensure you keep your setup_ui definition exactly as provided in your prompt
        pass 

    # --- Add or Replace these methods in your existing class ---

    def select_block_sequence(self, layer, pos_idx):
        if self.sequence_state == "COMPLETE":
            self.sequence_state = "WAITING_PICK"
            self.pick_selection = None

        if self.sequence_state == "WAITING_PICK":
            self.pick_selection = [self._get_block_id_from_memory(layer, pos_idx), layer, pos_idx]
            self.sequence_state = "WAITING_PLACE"
            self.goal_status_label.config(text=f"Selected L{layer} P{pos_idx}. Pick an EMPTY spot on L{self.get_highest_incomplete_layer()}.", fg="blue")

        elif self.sequence_state == "WAITING_PLACE":
            target_layer = self.get_highest_incomplete_layer()
            if layer == target_layer and self._is_position_empty(layer, pos_idx):
                self.place_selection = [self._get_block_id_from_memory(layer, pos_idx), layer, pos_idx]
                self.sequence_state = "COMPLETE"
                self.goal_status_label.config(text="Placement confirmed.", fg="green")
                self.ros_node.publish_goal([self.pick_selection, self.place_selection])
            else:
                self.goal_status_label.config(text="Uneligible position pick another placement position.", fg="red")

    def _get_block_id_from_memory(self, layer, pos_idx):
        if not self.ros_node.top_layer_data: return "000"
        layers_list = _layers_from_tower_message(self.ros_node.top_layer_data)
        if 0 <= layer < len(layers_list):
            blocks = layers_list[layer].get("blocks", [])
            block_idx = pos_idx - 1
            if 0 <= block_idx < len(blocks):
                b_id = blocks[block_idx].get("id", "000")
                return str(b_id) if b_id else "111" # Returns 111 for empty
        return "000"

    def update_gui_loop(self):
        # ... (Include your existing image and robot state updates)
        if self.ros_node.top_layer_data:
            layers_list = _layers_from_tower_message(self.ros_node.top_layer_data)
            for layer in range(6):
                for pos_idx in range(1, 4):
                    block_idx = pos_idx - 1
                    target_color, block_id_str = COLOUR_WHITE, "111" # Default empty ID is 111
                    if layer < len(layers_list):
                        blocks = layers_list[layer].get("blocks", [])
                        if block_idx < len(blocks):
                            block = blocks[block_idx]
                            if block.get("present", False):
                                target_color = BLOCK_COLOURS.get(block.get("colour", "unknown"), COLOUR_WHITE)
                                block_id_str = str(block.get("id", "000"))
                    btn = self.goal_buttons.get((layer, pos_idx))
                    if btn:
                        # Only show ID if it's not the empty ID (111)
                        display_text = block_id_str if block_id_str != "111" else ""
                        btn.config(text=display_text, bg=target_color, activebackground=target_color)
        self.root.after(33, self.update_gui_loop)

# (Rest of your existing main function...)