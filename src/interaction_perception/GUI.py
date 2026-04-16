#!/usr/bin/env python3

#How to run the GUI and Perception Currently:
#ros2 launch realsense2_camera rs_launch.py
#python3 src/interaction_perception/GUI.py
#python3 src/perception/play2.py --subscribe

import threading
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import Image
from std_msgs.msg import String, Int8MultiArray 
from cv_bridge import CvBridge
import tkinter as tk
from PIL import Image as PILImage, ImageTk

# --- Color Definitions ---
COLOUR_YELLOW = "#ffff00"  
COLOUR_BLACK = "#000000"   
COLOUR_LIGHT_GRAY = "#D3D3D3" 
COLOUR_WHITE = "#FFFFFF"   
COLOUR_RED = "#FF0000"     

class RealSenseCameraNode(Node):
    def __init__(self):
        super().__init__('realsense_gui_node')
        self.topic_name = '/camera/camera/color/image_raw'
        self.state_topic = '/robot_state'
        self.override_topic = '/ee_override_array'

        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )
        
        self.subscription = self.create_subscription(Image, self.topic_name, self.listener_callback, qos_profile)
        self.state_subscription = self.create_subscription(String, self.state_topic, self.state_callback, 10)
        
        # Publisher using Int8MultiArray (0 for False, 1 for True)
        self.override_pub = self.create_publisher(Int8MultiArray, self.override_topic, 10)

        self.bridge = CvBridge()
        self.cv_image = None
        self.new_image_flag = False
        self.robot_state_str = None
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

    def publish_override(self, boolean_array):
        msg = Int8MultiArray()
        msg.data = [int(val) for val in boolean_array]
        self.override_pub.publish(msg)

class JengaInterfaceApp:
    def __init__(self, root, ros_node):
        self.root = root
        self.ros_node = ros_node
        self.root.title("JENGA Tower Interface")
        self.root.configure(bg=COLOUR_BLACK)

        # UPDATED: Index 2 (Release) now starts as True
        self.ee_override_array = [False, False, True] 
        
        self.buttons = {}
        self.cam_label = None
        self.state_label = None
    
        self.setup_ui()
        
        # Initial UI Refresh and Publish to sync the robot with the starting state
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
        self.state_label = tk.Label(state_container, text="No Robot State received. Waiting for information...", 
                                    bg=COLOUR_LIGHT_GRAY, fg="blue", font=("Arial", 12, "italic"))
        self.state_label.pack(side=tk.LEFT, padx=5)

        ctrl_container = tk.Frame(main_frame, bg=COLOUR_LIGHT_GRAY, width=250)
        ctrl_container.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        ctrl_container.pack_propagate(False)
        
        tk.Label(ctrl_container, text="Gripper Override", bg=COLOUR_LIGHT_GRAY, font=("Arial", 14, "bold")).pack(pady=10)

        btns = [("close", "Override to\nclosed", 0), 
                ("open", "Override to\nopened", 1), 
                ("release", "Release\nOverride", 2)]

        for key, txt, idx in btns:
            b = tk.Button(ctrl_container, text=txt, bg=COLOUR_YELLOW, fg=COLOUR_BLACK,
                          font=("Arial", 11), width=18, height=5,
                          command=lambda i=idx: self.handle_press(i))
            b.pack(pady=15)
            self.buttons[idx] = b

    def handle_press(self, index):
        self.ee_override_array[index] = not self.ee_override_array[index]
        
        if index == 0 and self.ee_override_array[0]:
            self.ee_override_array[1] = False
            self.ee_override_array[2] = False
        elif index == 1 and self.ee_override_array[1]:
            self.ee_override_array[0] = False
            self.ee_override_array[2] = False
        elif index == 2 and self.ee_override_array[2]:
            self.ee_override_array[0] = False
            self.ee_override_array[1] = False
        
        if self.ee_override_array[0] or self.ee_override_array[1]:
            self.ee_override_array[2] = False
            
        print(f"States -> Closed: {self.ee_override_array[0]}, Open: {self.ee_override_array[1]}, Release: {self.ee_override_array[2]}")
            
        self.refresh_buttons()
        self.ros_node.publish_override(self.ee_override_array)

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