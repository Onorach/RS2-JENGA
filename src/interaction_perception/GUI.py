#!/usr/bin/env python3

import sys
import threading
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import tkinter as tk
from PIL import Image as PILImage, ImageTk

# --- Color Definitions ---
COLOUR_YELLOW = "#ffff00"  
COLOUR_BLACK = "#000000"
COLOUR_LIGHT_GRAY = "#D3D3D3"
COLOUR_WHITE = "#FFFFFF"
COLOUR_RED = "#FF0000" 

""" Conversion of ROS2 subscription """

class RealSenseCameraNode(Node):
    def __init__(self):
        super().__init__('realsense_gui_node')
        self.topic_name = '/camera/camera/color/image_raw'
        
        self.subscription = self.create_subscription(
            Image,
            self.topic_name,
            self.listener_callback,
            10
        )
        self.bridge = CvBridge()
        self.cv_image = None
        self.new_image_flag = False
        self.image_lock = threading.Lock()
        
        self.get_logger().info(f"Subscribed to: {self.topic_name}")

    def listener_callback(self, msg):
        try:
            # We use 'rgb8' because the D435i uses it
            cv_img = self.bridge.imgmsg_to_cv2(msg, desired_encoding='rgb8') # This returns a numpy array in RGB order
            
            with self.image_lock: #Ensuring thread safety when updating the image by locking the shared resource
                self.cv_image = cv_img
                self.new_image_flag = True
            
            # self.get_logger().info("Image received and converted.") #For debugging
            
        except Exception as e: #Catch any exceptions occuring during the conversion, process it and log it.
            self.get_logger().error(f"CvBridge Error: {e}")



class JengaInterfaceApp:
    def __init__(self, root, ros_node):
        self.root = root
        self.ros_node = ros_node
        self.root.title("JENGA Tower Interface")
        self.root.configure(bg=COLOUR_BLACK)

        self.states = {"override_close": False, "override_open": False, "release_override": False}
        self.buttons = {}
        self.cam_label = None
    
        self.setup_ui()
        self.update_camera_gui()

    def setup_ui(self):
        # Banner
        banner = tk.Frame(self.root, bg=COLOUR_YELLOW)
        banner.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        tk.Label(banner, text="JENGA Tower Interface", bg=COLOUR_YELLOW, fg=COLOUR_BLACK, 
                 font=("Arial", 28, "bold")).pack(anchor="w", padx=20)

        # Main Layout
        main_frame = tk.Frame(self.root, bg=COLOUR_BLACK)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Camera Panel (Left)
        cam_container = tk.Frame(main_frame, bg=COLOUR_WHITE)
        cam_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.cam_label = tk.Label(cam_container, bg=COLOUR_WHITE, text="Waiting for RealSense...")
        self.cam_label.pack(fill=tk.BOTH, expand=True)

        # Controls Panel (Right)
        ctrl_container = tk.Frame(main_frame, bg=COLOUR_LIGHT_GRAY, width=250)
        ctrl_container.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        ctrl_container.pack_propagate(False) # Keep width constant
        
        tk.Label(ctrl_container, text="Gripper Override", bg=COLOUR_LIGHT_GRAY, 
                 font=("Arial", 14, "bold")).pack(pady=10)

        # Buttons
        btns = [("override_close", "Override to\nclosed"), 
                ("override_open", "Override to\nopened"), 
                ("release_override", "Release\nOverride")]

        for var, txt in btns:
            b = tk.Button(ctrl_container, text=txt, bg=COLOUR_YELLOW, fg=COLOUR_BLACK,
                          font=("Arial", 11), width=18, height=5,
                          command=lambda v=var: self.handle_press(v))
            b.pack(pady=15)
            self.buttons[var] = b

    def handle_press(self, name):
        self.states[name] = not self.states[name]
        
        # Gripper Override Logic Rules
        if name == "override_close" and self.states[name]:
            self.states["override_open"] = False
            self.states["release_override"] = False
        elif name == "override_open" and self.states[name]:
            self.states["override_close"] = False
            self.states["release_override"] = False
        elif name == "release_override" and self.states[name]:
            self.states["override_close"] = False
            self.states["override_open"] = False
        
        if self.states["override_close"] or self.states["override_open"]:
            self.states["release_override"] = False
            
        self.refresh_buttons()

    def refresh_buttons(self):
        print("Override Closed:", self.states["override_close"], "Override Open:", self.states["override_open"], "Release Override:", self.states["release_override"])
        for name, active in self.states.items():
            color = COLOUR_RED if active else COLOUR_YELLOW
            text_color = COLOUR_WHITE if active else COLOUR_BLACK
            self.buttons[name].config(bg=color, fg=text_color, activebackground=color)

    def update_camera_gui(self):
        if self.ros_node.new_image_flag:
            with self.ros_node.image_lock:
                frame = self.ros_node.cv_image.copy()
                self.ros_node.new_image_flag = False
            
            # Since cv_bridge gave us RGB, we skip cvtColor and go straight to PIL
            im_pil = PILImage.fromarray(frame)
            
            # Scale to fit (adjust if your screen is small)
            im_pil.thumbnail((800, 600), PILImage.Resampling.LANCZOS)
            
            img_tk = ImageTk.PhotoImage(image=im_pil)
            self.cam_label.config(image=img_tk)
            self.cam_label.image = img_tk
            
        self.root.after(30, self.update_camera_gui)

def main():
    rclpy.init()
    node = RealSenseCameraNode()
    
    root = tk.Tk()
    app = JengaInterfaceApp(root, node)

    # Run ROS in a background thread
    threading.Thread(target=lambda: rclpy.spin(node), daemon=True).start()

    try:
        root.mainloop()
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()