import sys
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from pynput import mouse, keyboard

# Detect Operating System
IS_MAC = sys.platform == "darwin"
IS_WIN = sys.platform == "win32"
IS_LINUX = sys.platform.startswith("linux")

# Platform-specific font selections
if IS_WIN:
    SYS_FONT = "Segoe UI"
    MONO_FONT = "Consolas"
elif IS_MAC:
    SYS_FONT = "Helvetica Neue"
    MONO_FONT = "Menlo"
else:
    SYS_FONT = "DejaVu Sans"
    MONO_FONT = "Monospace"

class UniversalMouseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Universal Mouse Macro & AutoClicker Suite")
        self.root.geometry("460x780")
        self.root.resizable(False, False)

        # Styling Colors
        self.bg_dark = "#181818"
        self.bg_card = "#242424"
        self.accent_blue = "#007acc"
        self.accent_green = "#28a745"
        self.accent_red = "#dc3545"
        self.fg_white = "#ffffff"

        self.root.configure(bg=self.bg_dark)

        # Input Controllers
        self.mouse_ctrl = mouse.Controller()
        self.kb_ctrl = keyboard.Controller()
        
        # State
        self.is_clicking = False
        self.target_x = 0
        self.target_y = 0

        # UI Setup
        self.setup_styles()
        self.build_ui()
        
        # Global Event Listeners
        self.start_listeners()

        # AutoClicker Thread
        self.click_thread = threading.Thread(target=self.autoclicker_loop, daemon=True)
        self.click_thread.start()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background=self.bg_dark, borderwidth=0)
        style.configure("TNotebook.Tab", background=self.bg_card, foreground=self.fg_white, padding=[12, 6], font=(SYS_FONT, 9))
        style.map("TNotebook.Tab", background=[("selected", self.accent_blue)])
        style.configure("Card.TFrame", background=self.bg_card)
        style.configure("TLabel", background=self.bg_card, foreground=self.fg_white, font=(SYS_FONT, 9))
        style.configure("Header.TLabel", background=self.bg_card, foreground=self.fg_white, font=(SYS_FONT, 10, "bold"))
        style.configure("TRadiobutton", background=self.bg_card, foreground=self.fg_white, font=(SYS_FONT, 9))
        style.configure("TCombobox", fieldbackground=self.bg_dark, background=self.bg_card, foreground=self.fg_white)

    def build_ui(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=8, pady=8)

        self.tab_mapping = ttk.Frame(notebook)
        self.tab_clicker = ttk.Frame(notebook)
        self.tab_guide = ttk.Frame(notebook)

        notebook.add(self.tab_mapping, text="Button Remapper")
        notebook.add(self.tab_clicker, text="Auto Clicker")
        notebook.add(self.tab_guide, text="Scripting Guide")

        self.build_mapping_tab()
        self.build_clicker_tab()
        self.build_guide_tab()

    # --- TAB 1: VISUAL BUTTON REMAPPER ---
    def build_mapping_tab(self):
        self.canvas = tk.Canvas(self.tab_mapping, width=440, height=210, bg=self.bg_dark, highlightthickness=0)
        self.canvas.pack(pady=5)

        self.draw_interactive_mouse()

        input_container = ttk.Frame(self.tab_mapping, style="Card.TFrame")
        input_container.pack(fill="both", expand=True, padx=10, pady=5)

        # X1 Box
        ttk.Label(input_container, text="Side Button 1 (X1 / Back / Mouse 4) Macro Script:", style="Header.TLabel").pack(anchor="w", padx=10, pady=(8, 2))
        self.script_x1 = tk.Text(input_container, height=4, bg="#101010", fg="#00ffcc", insertbackground="white", font=(MONO_FONT, 9), relief="flat")
        self.script_x1.pack(fill="x", padx=10, pady=2)
        self.script_x1.insert("1.0", "TOGGLE_AUTOCLICK")

        # X2 Box (Default copy/paste adjusted for OS)
        default_paste = "PRESS(cmd+c)\nWAIT(50)\nPRESS(cmd+v)" if IS_MAC else "PRESS(ctrl+c)\nWAIT(50)\nPRESS(ctrl+v)"
        ttk.Label(input_container, text="Side Button 2 (X2 / Forward / Mouse 5) Macro Script:", style="Header.TLabel").pack(anchor="w", padx=10, pady=(12, 2))
        self.script_x2 = tk.Text(input_container, height=4, bg="#101010", fg="#00ffcc", insertbackground="white", font=(MONO_FONT, 9), relief="flat")
        self.script_x2.pack(fill="x", padx=10, pady=2)
        self.script_x2.insert("1.0", default_paste)

    def draw_interactive_mouse(self):
        c = self.canvas
        # Mouse Body Silhouette
        c.create_oval(160, 15, 280, 185, fill="#0a0a0a", outline="#333333", width=2)
        c.create_line(220, 15, 220, 85, fill="#222222", width=2)
        c.create_rectangle(214, 30, 226, 60, fill="#444444", outline="#666666")

        # Side Buttons
        c.create_rectangle(157, 95, 163, 125, fill="#007acc", outline="#00ffcc")
        c.create_rectangle(157, 60, 163, 90, fill="#007acc", outline="#00ffcc")

        # Connecting Callout Lines
        c.create_line(157, 75, 50, 75, 50, 190, fill="#00ffcc", width=1, dash=(4, 2))
        c.create_text(60, 60, text="X2 Line", fill="#00ffcc", font=(SYS_FONT, 8))

        c.create_line(157, 110, 20, 110, 20, 200, fill="#007acc", width=1, dash=(4, 2))
        c.create_text(30, 125, text="X1 Line", fill="#007acc", font=(SYS_FONT, 8))

    # --- TAB 2: AUTO CLICKER CONFIG ---
    def build_clicker_tab(self):
        card_int = ttk.LabelFrame(self.tab_clicker, text=" Click Interval ", style="Card.TFrame")
        card_int.pack(fill="x", padx=10, pady=8, ipady=5)

        f_grid = ttk.Frame(card_int, style="Card.TFrame")
        f_grid.pack()

        self.var_ms = tk.StringVar(value="100")
        self.var_sec = tk.StringVar(value="0")

        ttk.Label(f_grid, text="Seconds:").grid(row=0, column=0, padx=5)
        tk.Entry(f_grid, textvariable=self.var_sec, width=6, bg="#101010", fg="white", justify="center").grid(row=0, column=1, padx=5)

        ttk.Label(f_grid, text="Milliseconds:").grid(row=0, column=2, padx=5)
        tk.Entry(f_grid, textvariable=self.var_ms, width=6, bg="#101010", fg="white", justify="center").grid(row=0, column=3, padx=5)

        card_opt = ttk.LabelFrame(self.tab_clicker, text=" Click Settings ", style="Card.TFrame")
        card_opt.pack(fill="x", padx=10, pady=8, ipady=5)

        ttk.Label(card_opt, text="Target Button:").grid(row=0, column=0, sticky="w", padx=10, pady=4)
        self.var_btn = tk.StringVar(value="Left")
        ttk.Combobox(card_opt, textvariable=self.var_btn, values=["Left", "Right", "Middle"], state="readonly", width=10).grid(row=0, column=1)

        ttk.Label(card_opt, text="Click Type:").grid(row=1, column=0, sticky="w", padx=10, pady=4)
        self.var_type = tk.StringVar(value="Single")
        ttk.Combobox(card_opt, textvariable=self.var_type, values=["Single", "Double"], state="readonly", width=10).grid(row=1, column=1)

        card_pos = ttk.LabelFrame(self.tab_clicker, text=" Position Mode ", style="Card.TFrame")
        card_pos.pack(fill="x", padx=10, pady=8, ipady=5)

        self.var_pos_mode = tk.StringVar(value="current")
        ttk.Radiobutton(card_pos, text="Current Cursor Location", variable=self.var_pos_mode, value="current").pack(anchor="w", padx=10)
        
        pos_pick_frame = ttk.Frame(card_pos, style="Card.TFrame")
        pos_pick_frame.pack(fill="x", padx=10, pady=2)
        ttk.Radiobutton(pos_pick_frame, text="Fixed Location:", variable=self.var_pos_mode, value="fixed").pack(side="left")
        
        tk.Button(pos_pick_frame, text="Pick Point", command=self.pick_location, bg="#333", fg="white", relief="flat", font=(SYS_FONT, 8)).pack(side="left", padx=10)
        self.lbl_coord = ttk.Label(card_pos, text="X: 0 | Y: 0", font=(SYS_FONT, 8, "italic"))
        self.lbl_coord.pack(anchor="w", padx=25)

        self.lbl_status = tk.Label(self.tab_clicker, text="STATUS: INACTIVE", bg=self.bg_dark, fg=self.accent_red, font=(SYS_FONT, 10, "bold"))
        self.lbl_status.pack(pady=10)

        self.btn_toggle = tk.Button(self.tab_clicker, text="TOGGLE CLICKER (F6)", command=self.toggle_autoclicker, bg=self.accent_green, fg="white", font=(SYS_FONT, 11, "bold"), relief="flat", height=2)
        self.btn_toggle.pack(fill="x", padx=15)

    # --- TAB 3: SCRIPTING GUIDE ---
    def build_guide_tab(self):
        guide_card = ttk.Frame(self.tab_guide, style="Card.TFrame")
        guide_card.pack(fill="both", expand=True, padx=10, pady=10)

        guide_text = (
            "UNIVERSAL MOUSE MACRO GUIDE\n"
            "------------------------------------\n"
            "Works with ANY USB/Bluetooth mouse!\n"
            "Write commands into the X1 / X2 boxes:\n\n"
            "1. CLICK(button)\n"
            "   Left, right, or middle click.\n"
            "   Example: CLICK(left)\n\n"
            "2. DOUBLE_CLICK(button)\n"
            "   Example: DOUBLE_CLICK(left)\n\n"
            "3. PRESS(combination)\n"
            "   Simulates key combos across OSes.\n"
            "   Windows/Linux: PRESS(ctrl+c)\n"
            "   macOS: PRESS(cmd+c) or PRESS(command+c)\n\n"
            "4. TYPE(text)\n"
            "   Types text directly.\n"
            "   Example: TYPE(Hello World)\n\n"
            "5. WAIT(ms)\n"
            "   Pauses macro execution.\n"
            "   Example: WAIT(250)\n\n"
            "6. TOGGLE_AUTOCLICK\n"
            "   Starts/stops the clicker engine.\n\n"
            "OPERATING SYSTEM NOTES:\n"
            "• macOS: Grant Accessibility permissions in\n"
            "  System Settings > Privacy & Security.\n"
            "• Linux: Ensure 'python3-tk' is installed."
        )

        txt = tk.Text(guide_card, bg="#101010", fg="#dddddd", font=(MONO_FONT, 9), relief="flat", wrap="word")
        txt.pack(fill="both", expand=True, padx=8, pady=8)
        txt.insert("1.0", guide_text)
        txt.config(state="disabled")

    # --- MACRO ENGINE & INTERPRETER ---
    def execute_script(self, script_text):
        def run():
            lines = script_text.strip().split("\n")
            
            # Cross-platform Key Mapping Dictionary
            key_map = {
                "ctrl": keyboard.Key.ctrl_l if IS_MAC else keyboard.Key.ctrl,
                "cmd": keyboard.Key.cmd,
                "command": keyboard.Key.cmd,
                "alt": keyboard.Key.alt,
                "option": keyboard.Key.alt,
                "shift": keyboard.Key.shift,
                "tab": keyboard.Key.tab,
                "enter": keyboard.Key.enter,
                "space": keyboard.Key.space
            }

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                if line == "TOGGLE_AUTOCLICK":
                    self.root.after(0, self.toggle_autoclicker)

                elif line.startswith("CLICK(") and line.endswith(")"):
                    target = line[6:-1].lower()
                    btn = mouse.Button.right if target == "right" else mouse.Button.left
                    self.mouse_ctrl.click(btn, 1)

                elif line.startswith("DOUBLE_CLICK(") and line.endswith(")"):
                    target = line[13:-1].lower()
                    btn = mouse.Button.right if target == "right" else mouse.Button.left
                    self.mouse_ctrl.click(btn, 2)

                elif line.startswith("WAIT(") and line.endswith(")"):
                    try:
                        ms = float(line[5:-1])
                        time.sleep(ms / 1000.0)
                    except ValueError:
                        pass

                elif line.startswith("TYPE(") and line.endswith(")"):
                    payload = line[5:-1]
                    self.kb_ctrl.type(payload)

                elif line.startswith("PRESS(") and line.endswith(")"):
                    keys = line[6:-1].lower().split("+")
                    parsed_keys = [key_map.get(k, k) for k in keys]
                    
                    for k in parsed_keys:
                        self.kb_ctrl.press(k)
                    for k in reversed(parsed_keys):
                        self.kb_ctrl.release(k)

        threading.Thread(target=run, daemon=True).start()

    # --- AUTOCLICKER LOGIC ---
    def toggle_autoclicker(self):
        self.is_clicking = not self.is_clicking
        if self.is_clicking:
            self.lbl_status.config(text="STATUS: RUNNING", fg="#55ff55")
            self.btn_toggle.config(text="STOP CLICKER (F6)", bg=self.accent_red)
        else:
            self.lbl_status.config(text="STATUS: INACTIVE", fg=self.accent_red)
            self.btn_toggle.config(text="START CLICKER (F6)", bg=self.accent_green)

    def pick_location(self):
        self.root.iconify()
        time.sleep(0.3)
        def on_click(x, y, button, pressed):
            if pressed and button == mouse.Button.left:
                self.target_x, self.target_y = x, y
                self.lbl_coord.config(text=f"X: {int(x)} | Y: {int(y)}")
                self.var_pos_mode.set("fixed")
                self.root.deiconify()
                return False
        mouse.Listener(on_click=on_click).start()

    def autoclicker_loop(self):
        btn_map = {"Left": mouse.Button.left, "Right": mouse.Button.right, "Middle": mouse.Button.middle}
        while True:
            if self.is_clicking:
                if self.var_pos_mode.get() == "fixed":
                    self.mouse_ctrl.position = (self.target_x, self.target_y)
                
                btn = btn_map.get(self.var_btn.get(), mouse.Button.left)
                cnt = 2 if self.var_type.get() == "Double" else 1
                self.mouse_ctrl.click(btn, cnt)
                
                try:
                    s = float(self.var_sec.get() or 0)
                    ms = float(self.var_ms.get() or 0)
                    delay = max(0.001, s + (ms / 1000.0))
                except ValueError:
                    delay = 0.1
                
                time.sleep(delay)
            else:
                time.sleep(0.1)

    # --- INPUT LISTENERS ---
    def start_listeners(self):
        def on_key(key):
            if key == keyboard.Key.f6:
                self.root.after(0, self.toggle_autoclicker)
        keyboard.Listener(on_press=on_key).start()

        def on_mouse(x, y, button, pressed):
            if pressed:
                if button == mouse.Button.x1:
                    code = self.script_x1.get("1.0", tk.END)
                    self.execute_script(code)
                elif button == mouse.Button.x2:
                    code = self.script_x2.get("1.0", tk.END)
                    self.execute_script(code)
        mouse.Listener(on_click=on_mouse).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = UniversalMouseApp(root)
    root.mainloop()
