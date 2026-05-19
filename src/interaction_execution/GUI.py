#!/usr/bin/env python3

import threading
import json
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import Image
from std_msgs.msg import String, Int8MultiArray
from std_srvs.srv import SetBool  # Required for service calls
from cv_bridge import CvBridge
import tkinter as tk
from PIL import Image as PILImage, ImageTk

try:
    _PIL_RESAMPLE = PILImage.Resampling.LANCZOS
except AttributeError:
    _PIL_RESAMPLE = PILImage.LANCZOS  # Pillow < 9.1

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
    """Normalise /top_layer_state JSON into a bottom-first list (L0 / GUI L1 at index 0)."""
    if isinstance(data, list):
        layers = data
    elif isinstance(data, dict):
        if "layers" in data or "tower" in data:
            layers = data.get("layers", data.get("tower", []))
        elif "blocks" in data:
            layers = [data]
        else:
            layers = []
    else:
        layers = []
    if not layers:
        return []
    return sorted(layers, key=lambda layer: layer.get("layer", 0))

class RealSenseCameraNode(Node):
    def __init__(self):
        super().__init__('realsense_gui_node')
        self.topic_name = '/camera/camera/color/image_raw'
        self.state_topic = '/robot_state'
        self.override_topic = '/ee_override_array'
        self.top_layer_topic = '/top_layer_state'
        self.goal_topic = '/selected_goal'

        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )
        
        # Subscriptions
        self.subscription = self.create_subscription(Image, self.topic_name, self.listener_callback, qos_profile)
        self.state_subscription = self.create_subscription(String, self.state_topic, self.state_callback, 10)
        self.top_layer_sub = self.create_subscription(String, self.top_layer_topic, self.top_layer_callback, 10)
        
        # Publishers
        self.override_pub = self.create_publisher(Int8MultiArray, self.override_topic, 10)
        self.goal_pub = self.create_publisher(String, self.goal_topic, 10)

        # Service Client for E-STOP
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
        except Exception as e:
            self.get_logger().error(f"CvBridge Error: {e}")

    def state_callback(self, msg):
        self.robot_state_str = msg.data

    def top_layer_callback(self, msg):
        try:
            self.top_layer_data = json.loads(msg.data)
        except Exception as e:
            self.get_logger().error(f"Failed to parse tower data JSON: {e}")

    def publish_override(self, boolean_array):
        msg = Int8MultiArray()
        msg.data = [int(val) for val in boolean_array]
        self.override_pub.publish(msg)

    def publish_goal(self, goal_matrix):
        msg = String()
        msg.data = json.dumps(goal_matrix)
        self.goal_pub.publish(msg)

    def call_estop_service(self, state: bool):
        """Asynchronously calls the /estop service"""
        if not self.estop_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().error('Service /estop not available!')
            return
        
        request = SetBool.Request()
        request.data = state
        self.estop_client.call_async(request)
        self.get_logger().info(f"Service Call Sent: /estop data={state}")

class JengaInterfaceApp:
    def __init__(self, root, ros_node):
        self.root = root
        self.ros_node = ros_node
        self.root.title("JENGA Tower Interface")
        self.root.configure(bg=COLOUR_BLACK)

        self.ee_override_array = [False, False, True] 
        self.estop_active = False 
        
        # Sequence Matrix state machine tracking
        self.sequence_state = "WAITING_PICK"  # WAITING_PICK, WAITING_PLACE, COMPLETE
        self.pick_selection = None            # [Block ID, Layer, Position]
        self.place_selection = None           # [Block ID, Layer, Position]
        
        self.buttons = {}
        self.goal_buttons = {}  # (layer 0–5, position 1–3) -> Button widget; L0 = bottom
        self.estop_button = None 
        self.cam_label = None
        self.state_label = None
        self.goal_status_label = None
    
        self.setup_ui()
        self.refresh_buttons()
        self.ros_node.publish_override(self.ee_override_array)
        self.update_gui_loop()

    def setup_ui(self):
        banner = tk.Frame(self.root, bg=COLOUR_YELLOW)
        banner.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        tk.Label(banner, text="JENGA Tower Interface", bg=COLOUR_YELLOW, fg=COLOUR_BLACK, 
                 font=("Arial", 28, "bold")).pack(anchor="w", padx=20)

        main_frame = tk.Frame(self.root, bg=COLOUR_BLACK)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        left_column = tk.Frame(main_frame, bg=COLOUR_BLACK)
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        cam_container = tk.Frame(left_column, bg=COLOUR_WHITE)
        cam_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.cam_label = tk.Label(cam_container, bg=COLOUR_WHITE, text="Waiting for RealSense...")
        self.cam_label.pack(fill=tk.BOTH, expand=True)

        state_container = tk.Frame(left_column, bg=COLOUR_LIGHT_GRAY, height=60)
        state_container.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        state_container.pack_propagate(False) 
        tk.Label(state_container, text="Robot State:", bg=COLOUR_LIGHT_GRAY, font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=10)
        self.state_label = tk.Label(state_container, text="No Robot State received.", 
                                    bg=COLOUR_LIGHT_GRAY, fg="blue", font=("Arial", 12, "italic"))
        self.state_label.pack(side=tk.LEFT, padx=5)

        ctrl_container = tk.Frame(main_frame, bg=COLOUR_LIGHT_GRAY, width=320)
        ctrl_container.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        
        # --- Gripper Override Section ---
        tk.Label(ctrl_container, text="Gripper Override", bg=COLOUR_LIGHT_GRAY, font=("Arial", 14, "bold")).pack(pady=5)
        btns = [("close", "Override to\nclosed", 0), ("open", "Override to\nopened", 1), ("release", "Release\nOverride", 2)]
        for key, txt, idx in btns:
            b = tk.Button(ctrl_container, text=txt, bg=COLOUR_YELLOW, fg=COLOUR_BLACK, font=("Arial", 10), width=18, height=2, command=lambda i=idx: self.handle_press(i))
            b.pack(pady=3)
            self.buttons[idx] = b

        # --- 6 Layer Tower Selection Grid ---
        tk.Label(ctrl_container, text="Tower Layers", bg=COLOUR_LIGHT_GRAY, font=("Arial", 14, "bold")).pack(pady=(15, 2))
        
        goal_btn_frame = tk.Frame(ctrl_container, bg=COLOUR_LIGHT_GRAY)
        goal_btn_frame.pack(pady=2)

        # Build grid top-down on screen: L5 at top … L0 at bottom (matches perception).
        for layer in range(5, -1, -1):
            row_frame = tk.Frame(goal_btn_frame, bg=COLOUR_LIGHT_GRAY)
            row_frame.pack(pady=2)

            tk.Label(row_frame, text=f"L{layer}:", bg=COLOUR_LIGHT_GRAY, font=("Arial", 10, "bold"), width=4).pack(side=tk.LEFT)

            # Position indices: 1 = left, 2 = middle, 3 = right
            for pos_idx in range(1, 4):
                btn = tk.Button(row_frame, text="000", bg=COLOUR_WHITE, fg=COLOUR_BLACK, font=("Arial", 9, "bold"),
                                width=6, height=2, relief="raised",
                                command=lambda l=layer, p=pos_idx: self.select_block_sequence(l, p))
                btn.pack(side=tk.LEFT, padx=3)
                self.goal_buttons[(layer, pos_idx)] = btn

        self.goal_status_label = tk.Label(ctrl_container, text="Select next block to be picked up", 
                                          bg=COLOUR_LIGHT_GRAY, fg=COLOUR_BLACK, font=("Arial", 10, "italic"), 
                                          wraplength=280, justify="center")
        self.goal_status_label.pack(pady=10)

        # --- ESTOP Section ---
        tk.Label(ctrl_container, text="ESTOP", bg=COLOUR_LIGHT_GRAY, font=("Arial", 14, "bold")).pack(pady=(10, 2))
        self.estop_button = tk.Button(ctrl_container, text="OFF", bg=COLOUR_BLACK, fg=COLOUR_WHITE, 
                                      font=("Arial", 12, "bold"), width=18, height=2, 
                                      command=self.toggle_estop)
        self.estop_button.pack(pady=3)

    def toggle_estop(self):
        """Toggles the ESTOP state and calls the ROS service"""
        self.estop_active = not self.estop_active
        if self.estop_active:
            self.estop_button.config(text="ON", bg=COLOUR_RED)
        else:
            self.estop_button.config(text="OFF", bg=COLOUR_BLACK)
        self.ros_node.call_estop_service(self.estop_active)

    def handle_press(self, index):
        self.ee_override_array[index] = not self.ee_override_array[index]
        if index == 0 and self.ee_override_array[0]:
            self.ee_override_array[1] = False; self.ee_override_array[2] = False
        elif index == 1 and self.ee_override_array[1]:
            self.ee_override_array[0] = False; self.ee_override_array[2] = False
        elif index == 2 and self.ee_override_array[2]:
            self.ee_override_array[0] = False; self.ee_override_array[1] = False
        if self.ee_override_array[0] or self.ee_override_array[1]:
            self.ee_override_array[2] = False
        self.refresh_buttons()
        self.ros_node.publish_override(self.ee_override_array)

    def _get_block_id_from_memory(self, layer, pos_idx):
        """Helper to lookup active block ID string from the node's stored JSON data."""
        if not self.ros_node.top_layer_data:
            return "000"

        layers_list = _layers_from_tower_message(self.ros_node.top_layer_data)

        if 0 <= layer < len(layers_list):
            layer_data = layers_list[layer]
            if isinstance(layer_data, dict):
                blocks = layer_data.get("blocks", [])
                block_idx = pos_idx - 1  # 1-3 to 0-2
                if 0 <= block_idx < len(blocks):
                    b_id = blocks[block_idx].get("id", "000")
                    return str(b_id) if b_id is not None and b_id != "" else "000"
        return "000"

    def get_top_incomplete_layer(self):
        """Finds the highest layer (0-5) that has any empty spots."""
        if not self.ros_node.top_layer_data: return 0
        layers = _layers_from_tower_message(self.ros_node.top_layer_data)
        for layer in range(len(layers) - 1, -1, -1):
            blocks = layers[layer].get("blocks", [])
            # Layer is incomplete if it has missing blocks or unknown/none colours
            for b in blocks:
                if not b.get("present", False) or b.get("colour") in ["unknown", "none", None]:
                    return layer
        return 0

    def is_eligible(self, layer, pos_idx):
        """Returns True if the spot is actually available."""
        target_layer = self.get_top_incomplete_layer()
        if layer != target_layer: return False
        
        layers = _layers_from_tower_message(self.ros_node.top_layer_data)
        if layer < len(layers):
            blocks = layers[layer].get("blocks", [])
            b = blocks[pos_idx - 1] if (pos_idx - 1) < len(blocks) else {}
            return not b.get("present", False) or b.get("colour") in ["unknown", "none", None]
        return True

    def select_block_sequence(self, layer, pos_idx):
        if self.sequence_state == "COMPLETE":
            self.sequence_state = "WAITING_PICK"
            self.pick_selection = None
            self.place_selection = None

        if self.sequence_state == "WAITING_PICK":
            # Optional: Add logic here to restrict picking as well if desired
            self.pick_selection = [self._get_block_id_from_memory(layer, pos_idx), layer, pos_idx]
            self.sequence_state = "WAITING_PLACE"
            target = self.get_top_incomplete_layer()
            self.goal_status_label.config(
                text=f"Selected L{layer} P{pos_idx}. Now click an empty spot on L{target}.",
                fg="blue"
            )

        elif self.sequence_state == "WAITING_PLACE":
            if self.is_eligible(layer, pos_idx):
                self.place_selection = [self._get_block_id_from_memory(layer, pos_idx), layer, pos_idx]
                self.sequence_state = "COMPLETE"
                self.goal_status_label.config(text="Valid placement selected.", fg="green")
                # Publish
                self.ros_node.publish_goal([self.pick_selection, self.place_selection])
            else:
                self.goal_status_label.config(
                    text=f"Invalid! Only empty spots on L{self.get_top_incomplete_layer()} are eligible.",
                    fg="red"
                )
                
    def refresh_buttons(self):
        for idx, active in enumerate(self.ee_override_array):
            color = COLOUR_RED if active else COLOUR_YELLOW
            text_color = COLOUR_WHITE if active else COLOUR_BLACK
            self.buttons[idx].config(bg=color, fg=text_color, activebackground=color)

    def update_gui_loop(self):
        # Update Image Frame window
        if self.ros_node.new_image_flag:
            with self.ros_node.image_lock:
                frame = self.ros_node.cv_image.copy()
                self.ros_node.new_image_flag = False
            im_pil = PILImage.fromarray(frame)
            im_pil.thumbnail((800, 600), _PIL_RESAMPLE)
            img_tk = ImageTk.PhotoImage(image=im_pil)
            self.cam_label.config(image=img_tk)
            self.cam_label.image = img_tk
            
        if self.ros_node.robot_state_str:
            self.state_label.config(text=self.ros_node.robot_state_str, font=("Arial", 12, "bold"), fg=COLOUR_BLACK)
            
        # Update full tower matrix colors and ID text labels dynamically
        if self.ros_node.top_layer_data:
            layers_list = _layers_from_tower_message(self.ros_node.top_layer_data)
            
            for layer in range(6):
                for pos_idx in range(1, 4):
                    block_idx = pos_idx - 1
                    target_color = COLOUR_WHITE
                    block_id_str = "000"

                    if layer < len(layers_list):
                        layer_data = layers_list[layer]
                        if isinstance(layer_data, dict):
                            blocks = layer_data.get("blocks", [])
                            if block_idx < len(blocks):
                                block = blocks[block_idx]
                                if block.get("present", False):
                                    c_name = block.get("colour", "unknown")
                                    target_color = BLOCK_COLOURS.get(c_name, COLOUR_WHITE)
                                b_id = block.get("id", "000")
                                if b_id is not None and b_id != "":
                                    block_id_str = str(b_id)
                                    
                    btn = self.goal_buttons.get((layer, pos_idx))
                    if btn:
                        btn.config(text=block_id_str, bg=target_color, activebackground=target_color)
                        
        self.root.after(33, self.update_gui_loop)

def main():
    rclpy.init()
    node = RealSenseCameraNode()
    root = tk.Tk()
    app = JengaInterfaceApp(root, node)
    threading.Thread(target=lambda: rclpy.spin(node), daemon=True).start()
    try:
        root.mainloop()
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()