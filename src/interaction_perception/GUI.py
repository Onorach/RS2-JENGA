#!/usr/bin/env python3

import threading
import json
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import Image
from std_msgs.msg import String, Int8MultiArray, Bool # Added Bool for ESTOP
from cv_bridge import CvBridge
import tkinter as tk
from PIL import Image as PILImage, ImageTk

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
    "unknown": "#FFFFFF" 
}

class RealSenseCameraNode(Node):
    def __init__(self):
        super().__init__('realsense_gui_node')
        self.topic_name = '/camera/camera/color/image_raw'
        self.state_topic = '/robot_state'
        self.override_topic = '/ee_override_array'
        self.top_layer_topic = '/top_layer_state'
        self.goal_topic = '/selected_goal'
        self.estop_topic = '/estop' # New ESTOP topic

        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )
        
        self.subscription = self.create_subscription(Image, self.topic_name, self.listener_callback, qos_profile)
        self.state_subscription = self.create_subscription(String, self.state_topic, self.state_callback, 10)
        self.top_layer_sub = self.create_subscription(String, self.top_layer_topic, self.top_layer_callback, 10)
        
        self.override_pub = self.create_publisher(Int8MultiArray, self.override_topic, 10)
        self.goal_pub = self.create_publisher(String, self.goal_topic, 10)
        self.estop_pub = self.create_publisher(Bool, self.estop_topic, 10) # ESTOP Publisher

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
            self.get_logger().error(f"Failed to parse top layer JSON: {e}")

    def publish_override(self, boolean_array):
        msg = Int8MultiArray()
        msg.data = [int(val) for val in boolean_array]
        self.override_pub.publish(msg)
        print(f"Published EE Override Array: {msg.data}")

    def publish_goal(self, goal_array):
        msg = String()
        msg.data = json.dumps(goal_array)
        self.goal_pub.publish(msg)
        print(f"Published Selected Goal: {msg.data}")

    def publish_estop(self, state: bool):
        msg = Bool()
        msg.data = state
        self.estop_pub.publish(msg)
        print(f"ESTOP Toggled: {state}") # Print to terminal

class JengaInterfaceApp:
    def __init__(self, root, ros_node):
        self.root = root
        self.ros_node = ros_node
        self.root.title("JENGA Tower Interface")
        self.root.configure(bg=COLOUR_BLACK)

        self.ee_override_array = [False, False, True] 
        self.selected_goal_data = [] 
        self.estop_active = False # ESTOP boolean variable
        
        self.buttons = {}
        self.goal_buttons = []
        self.estop_button = None # ESTOP button reference
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

        ctrl_container = tk.Frame(main_frame, bg=COLOUR_LIGHT_GRAY, width=280)
        ctrl_container.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        
        # --- Gripper Override Section ---
        tk.Label(ctrl_container, text="Gripper Override", bg=COLOUR_LIGHT_GRAY, font=("Arial", 14, "bold")).pack(pady=10)
        btns = [("close", "Override to\nclosed", 0), ("open", "Override to\nopened", 1), ("release", "Release\nOverride", 2)]
        for key, txt, idx in btns:
            b = tk.Button(ctrl_container, text=txt, bg=COLOUR_YELLOW, fg=COLOUR_BLACK, font=("Arial", 11), width=18, height=4, command=lambda i=idx: self.handle_press(i))
            b.pack(pady=5)
            self.buttons[idx] = b

        # --- Next Goal Section ---
        tk.Label(ctrl_container, text="Next Goal", bg=COLOUR_LIGHT_GRAY, font=("Arial", 14, "bold")).pack(pady=(25, 5))
        goal_btn_frame = tk.Frame(ctrl_container, bg=COLOUR_LIGHT_GRAY)
        goal_btn_frame.pack(pady=5)
        for i in range(3):
            btn = tk.Button(goal_btn_frame, bg=COLOUR_WHITE, width=6, height=5, relief="raised", command=lambda pos=i: self.select_goal(pos))
            btn.pack(side=tk.LEFT, padx=5)
            self.goal_buttons.append(btn)
        self.goal_status_label = tk.Label(ctrl_container, text="Waiting for target selection...", bg=COLOUR_LIGHT_GRAY, fg=COLOUR_BLACK, font=("Arial", 11, "italic"), wraplength=250, justify="center")
        self.goal_status_label.pack(pady=10)

        # --- NEW: ESTOP Section ---
        tk.Label(ctrl_container, text="ESTOP", bg=COLOUR_LIGHT_GRAY, font=("Arial", 14, "bold")).pack(pady=(20, 5))
        self.estop_button = tk.Button(ctrl_container, text="OFF", bg=COLOUR_BLACK, fg=COLOUR_WHITE, 
                                      font=("Arial", 12, "bold"), width=18, height=3, 
                                      command=self.toggle_estop)
        self.estop_button.pack(pady=5)

    def toggle_estop(self):
        """Toggles the ESTOP state, updates visuals, and publishes to ROS"""
        self.estop_active = not self.estop_active
        if self.estop_active:
            self.estop_button.config(text="ON", bg=COLOUR_RED)
        else:
            self.estop_button.config(text="OFF", bg=COLOUR_BLACK)
        
        self.ros_node.publish_estop(self.estop_active)

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

    def select_goal(self, pos):
        if not self.ros_node.top_layer_data:
            self.goal_status_label.config(text="No tower data received yet.", fg=COLOUR_RED)
            return
        data = self.ros_node.top_layer_data
        layer_idx = data.get("layer", "?")
        blocks = data.get("blocks", [])
        pos_names = ["left", "middle", "right"]
        if pos < len(blocks):
            block = blocks[pos]
            if block.get("present", False) and block.get("colour") != "unknown":
                pos_name = pos_names[pos]
                self.selected_goal_data = [layer_idx, pos_name]
                self.goal_status_label.config(text=f"The {pos_name} block in layer {layer_idx} will be the next goal.", fg="blue")
                self.ros_node.publish_goal(self.selected_goal_data)
            else:
                self.goal_status_label.config(text=f"Invalid: No block present at the {pos_names[pos]} position.", fg=COLOUR_RED)

    def refresh_buttons(self):
        for idx, active in enumerate(self.ee_override_array):
            color = COLOUR_RED if active else COLOUR_YELLOW
            text_color = COLOUR_WHITE if active else COLOUR_BLACK
            self.buttons[idx].config(bg=color, fg=text_color, activebackground=color)

    def update_gui_loop(self):
        if self.ros_node.new_image_flag:
            with self.ros_node.image_lock:
                frame = self.ros_node.cv_image.copy()
                self.ros_node.new_image_flag = False
            im_pil = PILImage.fromarray(frame)
            im_pil.thumbnail((800, 600), PILImage.Resampling.LANCZOS)
            img_tk = ImageTk.PhotoImage(image=im_pil)
            self.cam_label.config(image=img_tk)
            self.cam_label.image = img_tk
        if self.ros_node.robot_state_str:
            self.state_label.config(text=self.ros_node.robot_state_str, font=("Arial", 12, "bold"), fg=COLOUR_BLACK)
        if self.ros_node.top_layer_data:
            blocks = self.ros_node.top_layer_data.get("blocks", [])
            for i in range(3):
                target_color = COLOUR_WHITE
                if i < len(blocks):
                    block = blocks[i]
                    if block.get("present", False):
                        c_name = block.get("colour", "unknown")
                        target_color = BLOCK_COLOURS.get(c_name, COLOUR_WHITE)
                self.goal_buttons[i].config(bg=target_color, activebackground=target_color)
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