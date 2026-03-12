import tkinter as tk

class OverrideGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Override Controls")
        self.root.configure(bg="#1e1e1e")

        # Variables
        self.states = {
            "override_close": False,
            "override_open": False,
            "release_override": False
        }

        # Colors
        self.YELLOW = "#ffe600"  # (255, 230, 0)
        self.RED = "#ff0000"     # (255, 0, 0)
        self.BLACK = "#000000"
        self.WHITE = "#ffffff"

        self.buttons = {}
        self.setup_ui()

    def setup_ui(self):
        frame = tk.Frame(self.root, bg="#1e1e1e")
        frame.pack(padx=20, pady=20)

        button_names = ["override_close", "override_open", "release_override"]

        for name in button_names:
            btn = tk.Button(
                frame,
                text=name,
                bg=self.YELLOW,
                fg=self.BLACK,
                font=("Arial", 10, "bold"),
                width=16,
                height=8,
                relief="raised",
                command=lambda n=name: self.handle_press(n)
            )
            btn.pack(side=tk.LEFT, padx=10)
            self.buttons[name] = btn

    def handle_press(self, name):
        # 1. Toggle the clicked button
        self.states[name] = not self.states[name]

        # 2. Apply Logic Rules
        if name == "override_close" and self.states["override_close"]:
            self.states["override_open"] = False
            self.states["release_override"] = False
            
        elif name == "override_open" and self.states["override_open"]:
            self.states["override_close"] = False
            self.states["release_override"] = False
            
        elif name == "release_override" and self.states["release_override"]:
            self.states["override_close"] = False
            self.states["override_open"] = False

        # 3. Update all button visuals to reflect new states
        self.refresh_buttons()

    def refresh_buttons(self):
        for name, is_active in self.states.items():
            if is_active:
                self.buttons[name].config(bg=self.RED, fg=self.WHITE, activebackground=self.RED)
            else:
                self.buttons[name].config(bg=self.YELLOW, fg=self.BLACK, activebackground=self.YELLOW)
        
        # Print states for verification
        print(f"Current States: {self.states}")

if __name__ == "__main__":
    root = tk.Tk()
    app = OverrideGUI(root)
    root.mainloop()