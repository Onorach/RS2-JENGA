#!/usr/bin/env python3

import threading
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String, Int8MultiArray, MultiArrayDimension, MultiArrayLayout
from std_srvs.srv import SetBool
from cv_bridge import CvBridge
import tkinter as tk
from PIL import Image as PILImage, ImageTk
import subprocess
import os

# Import custom message types
from jenga_interfaces.msg import JengaBlockStates

try:
    _PIL_RESAMPLE = PILImage.Resampling.LANCZOS
except AttributeError:
    _PIL_RESAMPLE = PILImage.LANCZOS

# --- UI Theme & Color Configurations ---
COLOUR_YELLOW = "#FFFF00"  
COLOUR_BLACK = "#121212"   
COLOUR_LIGHT_GRAY = "#E0E0E0" 
COLOUR_DARK_GRAY = "#1E1E1E"
COLOUR_WHITE = "#FFFFFF"   
COLOUR_RED = "#FF3333"     
COLOUR_GREEN = "#33CC33"

BLOCK_COLOURS = {
    "red": "#FF3333",
    "green": "#33CC33",
    "blue": "#3333FF",
    "yellow": "#FFFF33",
    "black": "#2A2A2A",
    "natural": "#DEB887",
    "purple": "#9933FF",
    "none": "#FFFFFF",
    "unknown": "#FFFFFF",
}

class JengaTowerModel:
    """
    Thread-safe Central Data Model.
    Stores and calculates the physical state of the tower using 0-2 positioning.
    """
    def __init__(self):
        self._lock = threading.Lock()
        self._block_data = {}  # Map: (layer, position) -> {"id": str, "colour": str}
        self._robot_state = "Unknown"

    def update_blocks(self, msg_blocks):
        with self._lock:
            self._block_data.clear()
            for block in msg_blocks:
                # Map incoming layer position to 0-indexed if it comes from a 1-indexed publisher,
                # or pass it through if your perception pipeline is updated to 0-2.
                # Assuming the ROS topic provides 0, 1, or 2:
                pos = block.layer_position
                self._block_data[(block.layer, pos)] = {
                    "id": str(block.block_id),
                    "colour": block.colour.lower().strip()
                }

    def update_robot_state(self, state_str):
        with self._lock:
            self._robot_state = state_str

    def get_robot_state(self):
        with self._lock:
            return self._robot_state

    def get_block(self, layer, position):
        with self._lock:
            return self._block_data.get((layer, position), None)

    def block_id_in_layers(self, block_id):
        """Returns True if a block with the given ID exists anywhere in layers 0-5."""
        with self._lock:
            return any(b["id"] == str(block_id) for b in self._block_data.values())

    def calculate_valid_placement_layer(self):
        """Dynamically finds the topmost layer that is incomplete (has 2 or fewer blocks)."""
        with self._lock:
            counts = {}
            max_occupied_layer = -1
            
            for (layer, _) in self._block_data.keys():
                counts[layer] = counts.get(layer, 0) + 1
                if layer > max_occupied_layer:
                    max_occupied_layer = layer
            
            if max_occupied_layer == -1:
                return 0
            
            if counts.get(max_occupied_layer, 0) < 3:
                return max_occupied_layer
            
            return max_occupied_layer + 1


class RealSenseCameraNode(Node):
    """
    ROS 2 Communication Hub.
    Handles data routing and change-driven terminal tracking.
    """
    def __init__(self, model: JengaTowerModel):
        super().__init__('realsense_gui_node')
        self.model = model
        self.bridge = CvBridge()
        
        self.cv_image = None
        self.image_lock = threading.Lock()
        self.has_new_frame = False

        # State tracking cache variables to ensure terminal outputs only print on updates
        self._last_override_state = None
        self._last_goal_state = None
        self._last_estop_state = None

        # Subscriptions
        self.create_subscription(Image, '/camera/camera/color/image_raw', self.image_callback, 10)
        self.create_subscription(String, '/robot_state', self.robot_state_callback, 10)
        self.create_subscription(JengaBlockStates, '/jenga/block_states', self.block_states_callback, 10)

        # Publishers
        self.override_pub = self.create_publisher(Int8MultiArray, '/ee_override_array', 10)
        self.goal_pub = self.create_publisher(Int8MultiArray, '/selected_goal', 10)
        
        # Services
        self.estop_client = self.create_client(SetBool, '/estop')

    def image_callback(self, msg):
        try:
            with self.image_lock:
                self.cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='rgb8')
                self.has_new_frame = True
        except Exception as e:
            self.get_logger().error(f"Image Conversion Error: {e}")

    def robot_state_callback(self, msg):
        self.model.update_robot_state(msg.data)

    def block_states_callback(self, msg):
        self.model.update_blocks(msg.blocks)

    def publish_override(self, array):
        current_override = tuple(array)
        if current_override != self._last_override_state:
            self._last_override_state = current_override
            state_labels = ["CLOSE", "OPEN", "RELEASE"]
            active_action = "UNKNOWN"
            for idx, val in enumerate(array):
                if val == 1:
                    active_action = state_labels[idx]
            print(f"[TERMINAL LOG] Gripper Override Changed -> State Array: {array} ({active_action})")
            
        self.override_pub.publish(Int8MultiArray(data=array))

    def publish_goal_sequence(self, pick_layer, pick_pos, pick_block_id, place_layer, place_pos):
        # 2x3 matrix layout:
        # [ pick_layer,  pick_pos,  pick_block_id ]
        # [ place_layer, place_pos, 0             ]  (place slot is empty, no block ID)
        flat_data = [pick_layer, pick_pos, pick_block_id, place_layer, place_pos, 0]

        if flat_data != self._last_goal_state:
            self._last_goal_state = flat_data
            print(f"[TERMINAL LOG] Goal Matrix Coordinates Updated -> "
                  f"[[{pick_layer}, {pick_pos}, {pick_block_id}], [{place_layer}, {place_pos}, 0]]")

        layout = MultiArrayLayout(
            dim=[
                MultiArrayDimension(label="rows", size=2, stride=6),
                MultiArrayDimension(label="cols", size=3, stride=3),
            ],
            data_offset=0
        )
        self.goal_pub.publish(Int8MultiArray(layout=layout, data=flat_data))

    def call_estop(self, state: bool):
        if state != self._last_estop_state:
            self._last_estop_state = state
            status_text = "TRIPPED / ACTIVE" if state else "DISENGAGED / READY"
            print(f"[TERMINAL LOG] Software ESTOP State Changed -> {status_text}")

        if self.estop_client.wait_for_service(timeout_sec=0.5):
            self.estop_client.call_async(SetBool.Request(data=state))


class JengaInterfaceApp:
    """
    Graphic User Interface and State Machine.
    """
    def __init__(self, root, ros_node, model):
        self.root = root
        self.ros_node = ros_node
        self.model = model
        
        self.goal_buttons = {}
        self.override_buttons = {}
        
        self.current_state = "WAITING_PICK"  
        self.selected_pick_coords = None
        self.selected_pick_block_id = 0
        self.selected_pick_colour = "unknown"
        self.transit_block = None  # {"id": str, "colour": str, "place_pos": int}
        self.is_estop_active = False

        self.setup_ui()
        self.update_loop()

    def launch_rviz_simulation(self):
        """Launches RViz as an independent process with proper ROS environment sourcing."""
        try:
            # 1. Get the current environment
            my_env = os.environ.copy()
            
            # 2. Define the path to your workspace setup file
            # Update this path if your workspace is located elsewhere
            ws_setup = os.path.join(os.path.expanduser("~"), "ros2_ws", "src", "RS2-JENGA", "install", "setup.bash")
            
            # 3. Create a command string that sources the setup and then launches
            # This is the most robust way to ensure the environment is loaded for the subprocess
            cmd = f"source {ws_setup} && ros2 launch ur_onrobot_moveit_config ur_onrobot_moveit.launch.py ur_type:=ur3e onrobot_type:=rg2 launch_rviz:=true launch_servo:=false"
            
            # 4. Use shell=True to allow the 'source' command to execute
            subprocess.Popen(cmd, shell=True, executable="/bin/bash", preexec_fn=os.setsid)
            
            print("[TERMINAL LOG] Simulation visualization launched in external window.")
        except Exception as e:
            print(f"[ERROR] Failed to launch RViz: {e}")

    def setup_ui(self):
        self.root.title("Autonomous Jenga Controller")
        self.root.configure(bg=COLOUR_BLACK)

        # Top Title Banner
        banner = tk.Frame(self.root, bg=COLOUR_YELLOW)
        banner.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        tk.Label(banner, text="JENGA Control Station", bg=COLOUR_YELLOW, fg=COLOUR_BLACK, 
                 font=("Arial", 24, "bold")).pack(anchor="w", padx=20, pady=5)

        # Core Split Container
        main_frame = tk.Frame(self.root, bg=COLOUR_BLACK)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Left Column - Visual Feeds
        left_column = tk.Frame(main_frame, bg=COLOUR_BLACK)
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.cam_label = tk.Label(left_column, bg=COLOUR_DARK_GRAY, text="Awaiting Video Feed...", fg=COLOUR_WHITE)
        self.cam_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Live Telemetry Subpanel
        state_container = tk.Frame(left_column, bg=COLOUR_DARK_GRAY, height=45)
        state_container.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        state_container.pack_propagate(False)
        tk.Label(state_container, text="Robot Status:", bg=COLOUR_DARK_GRAY, fg=COLOUR_YELLOW, font=("Arial", 11, "bold")).pack(side=tk.LEFT, padx=15)
        self.state_label = tk.Label(state_container, text="Offline", bg=COLOUR_DARK_GRAY, fg=COLOUR_WHITE, font=("Arial", 11, "italic"))
        self.state_label.pack(side=tk.LEFT, padx=5)

        # Right Column - Command Controls
        ctrl_container = tk.Frame(main_frame, bg=COLOUR_DARK_GRAY, width=340)
        ctrl_container.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        ctrl_container.pack_propagate(False)

        # Section A: End Effector Controls
        tk.Label(ctrl_container, text="Gripper Overrides", bg=COLOUR_DARK_GRAY, fg=COLOUR_WHITE, font=("Arial", 12, "bold")).pack(pady=5)
        gripper_actions = [("Close", 0), ("Open", 1), ("Release", 2)]
        for label, index in gripper_actions:
            btn = tk.Button(ctrl_container, text=label, bg=COLOUR_YELLOW, fg=COLOUR_BLACK, activebackground=COLOUR_WHITE,
                            font=("Arial", 10, "bold"), width=24, command=lambda idx=index: self.ros_node.publish_override([1 if i == idx else 0 for i in range(3)]))
            btn.pack(pady=3)
            self.override_buttons[index] = btn

        # Section B: Physical Tower Intermediary Layout Grid
        tk.Label(ctrl_container, text="Jenga Matrix Grid", bg=COLOUR_DARK_GRAY, fg=COLOUR_WHITE, font=("Arial", 12, "bold")).pack(pady=(15, 2))
        grid_wrapper = tk.Frame(ctrl_container, bg=COLOUR_DARK_GRAY)
        grid_wrapper.pack(pady=5)

        for layer in range(6, -1, -1):
            row_frame = tk.Frame(grid_wrapper, bg=COLOUR_DARK_GRAY)
            row_frame.pack(pady=1)

            if layer == 6:
                label_text = "TOP"
                label_fg = COLOUR_YELLOW
            else:
                label_text = f"L{layer}"
                label_fg = COLOUR_LIGHT_GRAY

            tk.Label(row_frame, text=label_text, bg=COLOUR_DARK_GRAY, fg=label_fg, font=("Arial", 9, "bold"), width=4).pack(side=tk.LEFT)

            # Positions are now 0-indexed: 0 = left, 1 = middle, 2 = right
            for pos_idx in range(3):
                btn = tk.Button(row_frame, text="---" if layer == 6 else "000",
                                bg=COLOUR_DARK_GRAY if layer == 6 else COLOUR_WHITE,
                                fg="#666666" if layer == 6 else COLOUR_BLACK,
                                font=("Arial", 9, "bold"), width=7, height=2, relief="flat",
                                command=lambda l=layer, p=pos_idx: self.handle_matrix_click(l, p))
                btn.pack(side=tk.LEFT, padx=2)
                self.goal_buttons[(layer, pos_idx)] = btn

        # Section C: Simulation Utilities
        tk.Label(ctrl_container, text="Simulation Utilities", bg=COLOUR_DARK_GRAY, fg=COLOUR_WHITE, font=("Arial", 12, "bold")).pack(pady=(15, 2))
        tk.Button(ctrl_container, text="Launch RViz Simulation", bg=COLOUR_WHITE, fg=COLOUR_BLACK, 
                  font=("Arial", 10, "bold"), width=24, height=2, command=self.launch_rviz_simulation).pack(pady=5)

        # Section D: Safety Utilities
        tk.Label(ctrl_container, text="Safety Utilities", bg=COLOUR_DARK_GRAY, fg=COLOUR_WHITE, font=("Arial", 12, "bold")).pack(pady=(10, 2))
        self.estop_button = tk.Button(ctrl_container, text="SYSTEM ENGAGED", bg=COLOUR_GREEN, fg=COLOUR_WHITE, 
                                      font=("Arial", 11, "bold"), width=24, height=2, command=self.handle_estop_toggle)
        self.estop_button.pack(pady=5)

        # Status Label
        self.goal_status_label = tk.Label(ctrl_container, text="Step 1: Click a block to Pick Up.", 
                                          bg=COLOUR_DARK_GRAY, fg=COLOUR_YELLOW, font=("Arial", 10, "bold"), wraplength=300)
        self.goal_status_label.pack(pady=10)

    def handle_matrix_click(self, layer, position):
        block = self.model.get_block(layer, position)
        target_place_layer = self.model.calculate_valid_placement_layer()

        if self.current_state == "WAITING_PICK":
            if block is not None:
                self.selected_pick_coords = (layer, position)
                self.selected_pick_block_id = int(block["id"])
                self.selected_pick_colour = block["colour"]
                self.current_state = "WAITING_PLACE"
                self.goal_status_label.config(
                    text=f"Pick selected: L{layer} P{position}.\nStep 2: Choose empty slot on Layer {target_place_layer}.",
                    fg=COLOUR_WHITE
                )
            else:
                self.goal_status_label.config(text="Invalid action: Empty spot selected! Choose an actual block.", fg=COLOUR_RED)

        elif self.current_state == "WAITING_PLACE":
            if block is not None:
                self.selected_pick_coords = (layer, position)
                self.selected_pick_block_id = int(block["id"])
                self.selected_pick_colour = block["colour"]
                self.goal_status_label.config(
                    text=f"Pick updated: L{layer} P{position}.\nStep 2: Choose empty slot on Layer {target_place_layer}.",
                    fg=COLOUR_WHITE
                )
                return

            if layer != target_place_layer:
                self.goal_status_label.config(
                    text=f"Rule Infraction! Placements are restricted strictly to Layer {target_place_layer}.", 
                    fg=COLOUR_RED
                )
                return

            pick_l, pick_p = self.selected_pick_coords

            self.ros_node.publish_goal_sequence(pick_l, pick_p, self.selected_pick_block_id, layer, position)

            # Record the in-transit block so layer 6 (TOP) can display it once it leaves layers 0-5
            self.transit_block = {
                "id": str(self.selected_pick_block_id),
                "colour": self.selected_pick_colour,
                "place_pos": position,
                "lifted": False   # becomes True once block_states stops reporting this block
            }

            self.current_state = "WAITING_PICK"
            self.selected_pick_coords = None
            self.selected_pick_block_id = 0
            self.selected_pick_colour = "unknown"
            self.goal_status_label.config(text="Execution target sent. Step 1: Select next block to Pick Up.", fg=COLOUR_YELLOW)

    def handle_estop_toggle(self):
        self.is_estop_active = not self.is_estop_active
        self.ros_node.call_estop(self.is_estop_active)
        
        if self.is_estop_active:
            self.estop_button.config(text="ESTOP TRIPPED", bg=COLOUR_RED)
        else:
            self.estop_button.config(text="SYSTEM ENGAGED", bg=COLOUR_GREEN)

    def update_loop(self):
        if self.ros_node.has_new_frame:
            with self.ros_node.image_lock:
                cv_img = self.ros_node.cv_image.copy()
                self.ros_node.has_new_frame = False
            
            h, w, _ = cv_img.shape
            scale = min(640 / w, 480 / h)
            img_pil = PILImage.fromarray(cv_img).resize((int(w * scale), int(h * scale)), _PIL_RESAMPLE)
            img_tk = ImageTk.PhotoImage(image=img_pil)
            self.cam_label.config(image=img_tk, text="")
            self.cam_label.image = img_tk

        self.state_label.config(text=self.model.get_robot_state())
        target_place_layer = self.model.calculate_valid_placement_layer()
        
        for layer in range(6):
            # Layers 0-5 driven by block_states
            for pos_idx in range(3):
                btn = self.goal_buttons.get((layer, pos_idx))
                if not btn:
                    continue

                block = self.model.get_block(layer, pos_idx)

                if block:
                    btn_text = block["id"]
                    bg_color = BLOCK_COLOURS.get(block["colour"], COLOUR_WHITE)
                    fg_color = COLOUR_WHITE if block["colour"] in ["black", "blue"] else COLOUR_BLACK
                    relief_type = "raised"
                else:
                    btn_text = "---"
                    fg_color = "#666666"
                    relief_type = "flat"
                    bg_color = "#334433" if (layer == target_place_layer and self.current_state == "WAITING_PLACE") else COLOUR_DARK_GRAY

                if btn.cget("text") != btn_text or btn.cget("bg") != bg_color:
                    btn.config(text=btn_text, bg=bg_color, fg=fg_color, activebackground=bg_color, relief=relief_type)

        # --- Layer 6 (TOP): merges in-transit display with normal placement highlight ---
        # Resolve transit state once before the position loop
        in_transit = False
        if self.transit_block is not None:
            block_gone = not self.model.block_id_in_layers(self.transit_block["id"])
            if block_gone:
                # Block has left layers 0-5 — mark as lifted and show on layer 6
                self.transit_block["lifted"] = True
                in_transit = True
            elif self.transit_block["lifted"]:
                # Block was gone and has now reappeared — placement confirmed by perception
                self.transit_block = None
            # else: goal published but robot hasn't lifted yet — wait, don't show yet

        for pos_idx in range(3):
            btn = self.goal_buttons.get((6, pos_idx))
            if not btn:
                continue

            if in_transit and pos_idx == self.transit_block["place_pos"]:
                # Show the in-transit block with its colour and ID
                colour = self.transit_block["colour"]
                bg_color = BLOCK_COLOURS.get(colour, COLOUR_WHITE)
                fg_color = COLOUR_WHITE if colour in ["black", "blue"] else COLOUR_BLACK
                btn.config(text=self.transit_block["id"], bg=bg_color, fg=fg_color,
                           activebackground=bg_color, relief="raised")
            else:
                # Empty slot — highlight green if layer 6 is the valid placement target
                bg_color = "#334433" if (target_place_layer == 6 and self.current_state == "WAITING_PLACE") else COLOUR_DARK_GRAY
                btn.config(text="---", bg=bg_color, fg="#666666",
                           activebackground=bg_color, relief="flat")

        self.root.after(30, self.update_loop)


def main():
    rclpy.init()
    model = JengaTowerModel()
    node = RealSenseCameraNode(model)
    
    root = tk.Tk()
    app = JengaInterfaceApp(root, node, model)
    
    ros_thread = threading.Thread(target=lambda: rclpy.spin(node), daemon=True)
    ros_thread.start()
    
    try:
        root.mainloop()
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()