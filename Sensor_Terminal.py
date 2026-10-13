import tkinter as tk
from tkinter import ttk, messagebox
import serial
import serial.tools.list_ports
import threading
import queue
import time
import os
import sys

# ============================================================================
# GaiaCode MD3 Design Tokens (Dark Mode — Slate & Teal)
# Source: GaiaCode Material Design 3 (MD3) Design System v1.0
# ============================================================================
MD3 = {
    # Primary accents (teal)
    "primary":               "#0EADB2",
    "on_primary":            "#0f172a",
    "on_primary_container":  "#80eeef",
    "primary_hover":         "#0d9da2",
    "primary_dim":           "#0a3c3f",

    # Surface & background hierarchy
    "background":            "#0f172a",
    "on_background":         "#e2e8f0",
    "surface_lowest":        "#020a14",
    "surface":               "#1e293b",
    "surface_low":           "#1e293b",
    "surface_container":     "#263245",
    "surface_high":          "#2d3b52",
    "surface_highest":       "#334155",

    # Text & outlines
    "on_surface":            "#e2e8f0",
    "on_surface_variant":    "#94a3b8",
    "outline":               "#334155",
    "outline_variant":       "#1e293b",

    # Semantic feedback
    "error":                 "#ef4444",
    "on_error":              "#ffffff",
    "on_error_container":    "#fca5a5",
    "success":               "#10b981",
    "on_success_container":  "#6ee7b7",
    "warning":               "#f59e0b",
    "on_warning_container":  "#fbbf24",
    "info":                  "#38bdf8",
}

FONT_SANS = ("Segoe UI", 10)
FONT_SANS_BOLD = ("Segoe UI", 10, "bold")
FONT_MONO = ("Courier New", 10)

LOGO_PATHS = [
    "/home/sysop/.hermes/Workspace/branding/Gaiacode.png",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "Gaiacode.png"),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png"),
]


def load_logo(max_height=None, max_width=None):
    """Load the GaiaCode logo with a graceful fallback chain.

    Returns a tk-compatible image (PIL ImageTk.PhotoImage preferred,
    native tk.PhotoImage as fallback) or None if all paths/methods fail.
    """
    path = next((p for p in LOGO_PATHS if os.path.isfile(p)), None)
    if path is None:
        return None

    try:
        from PIL import Image, ImageTk
        img = Image.open(path)
        if max_height:
            ratio = max_height / img.height
            img = img.resize((max(1, int(img.width * ratio)), max_height),
                             Image.LANCZOS)
        elif max_width:
            ratio = max_width / img.width
            img = img.resize((max_width, max(1, int(img.height * ratio))),
                             Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception:
        pass

    try:
        img = tk.PhotoImage(file=path)
        if max_height and img.height() > max_height:
            factor = max(1, round(img.height() / max_height))
            img = img.subsample(factor, factor)
        return img
    except Exception:
        return None


# =========================================================
# BUTTON ICON MAP — Unicode symbols for instrument-panel feel
# =========================================================
BUTTON_ICONS = {
    # Axis selection
    'All Axes':       '✦',    # Four-pointed star — all directions
    'North/South':    '↕',    # Vertical arrow — N/S axis
    'East/West':      '↔',    # Horizontal arrow — E/W axis
    'Vertical':       '⬍',    # Up/down — Z axis
    # Mass & Calibration
    'Centre Mass':    '⊕',    # Crosshair circle — centering
    'Show Mass':      '⚖',    # Scale — mass position
    'Motor (-)':      '◀',    # Left triangle — decrease
    'Motor (+)':      '▶',    # Right triangle — increase
    'Zero Mass Pos':  '⊘',    # Circle with slash — zero/reset
    'Cal Enable ON':  '◉',    # Filled target — calibration active
    'Cal Enable OFF': '○',    # Empty circle — calibration off
    'All Cal ON':     '⬤',    # Filled circle — all on
    'All Cal OFF':    '◯',    # Large empty circle — all off
    # Gain
    'Vel * 1':        '①',
    'Vel * 2':        '②',
    'Vel * 4':        '④',
    'Vel * 10':       '⑩',
    'Acc * 1':        '❶',
    'Acc * 5':        '❺',
    'Acc * 10':       '❿',
    'Acc * 50':       '㊿',
    'Low Gain':       '▽',    # Down triangle — low
    'High Gain':      '△',    # Up triangle — high
    '0.5g Gain':      '▫',    # Small square — smallest
    '1g Gain':        '◻',    # Medium square
    '2g Gain':        '◼',    # Filled square
    '4g Gain':        '⬛',    # Large filled — max
    # Advanced
    'Sign-On Msg':    'ℹ',    # Info
    'Short (30s)':    '⏱',    # Stopwatch — short period
    'Short Period':   '⏱',
    'Mid (60s)':      '⏲',    # Timer — medium period
    'Long (120s)':    '⏳',    # Hourglass — long period
    'Long Period':    '⏳',
    'Show Params':    '☰',    # Menu/list — display parameters
    'Store Params':   '💾',   # Floppy — save
    'Save ADC Zero':  '📌',   # Pin — save reference
    'Read ADC Zero':  '📋',   # Clipboard — read back
    'Print Title':    '🏷',    # Label tag
    'Lock Axes':      '🔒',   # Locked
    'Unlock Axes':    '🔓',   # Unlocked
}

# =========================================================
# SENSOR COMMAND PROFILES
# =========================================================
SENSOR_PROFILES = {
    'pico': {
        'name': 'θ Theta Pico',
        'groups': [
            {'title': '1. Target Axis Select', 'type': 'axis', 'buttons': [
                {'label': 'All Axes', 'cmd': 'A'}, {'label': 'North/South', 'cmd': 'N'},
                {'label': 'East/West', 'cmd': 'E'}, {'label': 'Vertical', 'cmd': 'Z'}
            ]},
            {'title': '2. Mass & Calibration Control', 'type': 'mass', 'buttons': [
                {'label': 'Centre Mass', 'cmd': 'C'}, {'label': 'Show Mass', 'cmd': 'M'},
                {'label': 'Motor (-)', 'cmd': '<'}, {'label': 'Motor (+)', 'cmd': '>'},
                {'label': 'Cal Enable ON', 'cmd': 'I'}, {'label': 'Cal Enable OFF', 'cmd': 'K'},
                {'label': 'All Cal ON', 'cmd': 'T'}, {'label': 'All Cal OFF', 'cmd': 'R'}
            ]},
            {'title': '3. Gain Control', 'type': 'gain', 'buttons': [
                {'label': 'Vel * 1', 'cmd': '1V'}, {'label': 'Vel * 2', 'cmd': '2V'},
                {'label': 'Vel * 4', 'cmd': '4V'}, {'label': 'Vel * 10', 'cmd': '10V'},
                {'label': 'Acc * 1', 'cmd': '1A'}, {'label': 'Acc * 5', 'cmd': '5A'},
                {'label': 'Acc * 10', 'cmd': '10A'}, {'label': 'Acc * 50', 'cmd': '50A'}
            ]},
            {'title': '4. Advanced System', 'type': 'adv', 'buttons': [
                {'label': 'Short (30s)', 'cmd': 'S'}, {'label': 'Mid (60s)', 'cmd': 'L'},
                {'label': 'Long (120s)', 'cmd': 'B'}, {'label': 'Show Params', 'cmd': 'D'},
                {'label': 'Store Params', 'cmd': 'Q'}, {'label': 'Save ADC Zero', 'cmd': '9'},
                {'label': 'Read ADC Zero', 'cmd': '%'}
            ]}
        ]
    },
    'theta': {
        'name': 'θ Theta Standard',
        'groups': [
            {'title': '1. Target Axis Select', 'type': 'axis', 'buttons': [
                {'label': 'All Axes', 'cmd': 'A'}, {'label': 'North/South', 'cmd': 'N'},
                {'label': 'East/West', 'cmd': 'E'}, {'label': 'Vertical', 'cmd': 'Z'}
            ]},
            {'title': '2. Mass & Calibration Control', 'type': 'mass', 'buttons': [
                {'label': 'Centre Mass', 'cmd': 'C'}, {'label': 'Show Mass', 'cmd': 'M'},
                {'label': 'Motor (-)', 'cmd': '<'}, {'label': 'Motor (+)', 'cmd': '>'},
                {'label': 'Zero Mass Pos', 'cmd': '='}, {'label': 'Cal Enable ON', 'cmd': 'I'},
                {'label': 'Cal Enable OFF', 'cmd': 'K'}
            ]},
            {'title': '3. Gain Control', 'type': 'gain', 'buttons': [
                {'label': 'Low Gain', 'cmd': 'G'}, {'label': 'High Gain', 'cmd': 'H'}
            ]},
            {'title': '4. Advanced System', 'type': 'adv', 'buttons': [
                {'label': 'Sign-On Msg', 'cmd': '?'}, {'label': 'Short Period', 'cmd': 'S'},
                {'label': 'Long Period', 'cmd': 'B'}, {'label': 'Show Params', 'cmd': 'D'}
            ]}
        ]
    },
    'sigma': {
        'name': 'Σ Sigma',
        'groups': [
            {'title': '1. Target Axis Select', 'type': 'axis', 'buttons': [
                {'label': 'All Axes', 'cmd': 'A'}, {'label': 'North/South', 'cmd': 'N'},
                {'label': 'East/West', 'cmd': 'E'}, {'label': 'Vertical', 'cmd': 'Z'}
            ]},
            {'title': '2. Mass & Calibration Control', 'type': 'mass', 'buttons': [
                {'label': 'Centre Mass', 'cmd': 'C'}, {'label': 'Show Mass', 'cmd': 'M'},
                {'label': 'Motor (-)', 'cmd': '<'}, {'label': 'Motor (+)', 'cmd': '>'},
                {'label': 'Zero Mass Pos', 'cmd': '='}
            ]},
            {'title': '3. Gain Control', 'type': 'gain', 'buttons': [
                {'label': '0.5g Gain', 'cmd': '1G'}, {'label': '1g Gain', 'cmd': '2G'},
                {'label': '2g Gain', 'cmd': '3G'}, {'label': '4g Gain', 'cmd': '4G'}
            ]},
            {'title': '4. Advanced System', 'type': 'adv', 'buttons': [
                {'label': 'Sign-On Msg', 'cmd': '?'}, {'label': 'Show Params', 'cmd': 'D'}
            ]}
        ]
    },
    'alpha': {
        'name': 'α Alpha',
        'groups': [
            {'title': '1. Target Axis Select', 'type': 'axis', 'buttons': [
                {'label': 'All Axes', 'cmd': 'A'}, {'label': 'North/South', 'cmd': 'N'},
                {'label': 'East/West', 'cmd': 'E'}, {'label': 'Vertical', 'cmd': 'Z'}
            ]},
            {'title': '2. Mass & Calibration Control', 'type': 'mass', 'buttons': [
                {'label': 'Centre Mass', 'cmd': 'C'}, {'label': 'Show Mass', 'cmd': 'M'},
                {'label': 'Motor (-)', 'cmd': '<'}, {'label': 'Motor (+)', 'cmd': '>'},
                {'label': 'Zero Mass Pos', 'cmd': '='}, {'label': 'Cal Enable ON', 'cmd': 'I'},
                {'label': 'Cal Enable OFF', 'cmd': 'K'}
            ]},
            {'title': '3. Advanced System', 'type': 'adv', 'buttons': [
                {'label': 'Sign-On Msg', 'cmd': '?'}, {'label': 'Short Period', 'cmd': 'S'},
                {'label': 'Long Period', 'cmd': 'B'}, {'label': 'Show Params', 'cmd': 'D'},
                {'label': 'Store Params', 'cmd': 'Q'},
                {'label': 'Lock Axes', 'cmd': 'L'}, {'label': 'Unlock Axes', 'cmd': 'U'}
            ]}
        ]
    }
}

# Group accent tints derived from the MD3 palette — dim variants keep the
# operator's color grouping while remaining inside the GaiaCode dark scheme.
THEMES = {
    'axis': {'bg': MD3['primary_dim'],       'fg': MD3['on_primary_container'], 'active_bg': MD3['primary_hover']},
    'mass': {'bg': '#3a2e12',                'fg': MD3['on_warning_container'], 'active_bg': '#54431c'},
    'gain': {'bg': '#12293a',                'fg': MD3['info'],                 'active_bg': '#1c3a52'},
    'adv':  {'bg': MD3['surface_container'], 'fg': MD3['on_surface'],           'active_bg': MD3['surface_high']},
}


class SensorTerminalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GaiaCode — Universal Sensor Terminal")
        self.root.geometry("1100x700")
        self.root.configure(bg=MD3["background"])

        # Set window icon (works for title bar, taskbar, alt-tab)
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            ico_path = os.path.join(script_dir, "Gaiacode.ico")

            if sys.platform == 'win32' and os.path.exists(ico_path):
                # Windows: use iconbitmap for .ico files (best taskbar support)
                self.root.iconbitmap(ico_path)
            else:
                # Linux/Mac: PNG with iconphoto (branding dir first, then local)
                icon_img = load_logo()
                if icon_img is not None:
                    self.root.iconphoto(True, icon_img)
                    self._icon_ref = icon_img  # Keep reference to prevent GC
        except Exception:
            pass  # Icon is non-critical

        self.serial_port = None
        self.read_thread = None
        self.keep_reading = False
        self.msg_queue = queue.Queue()
        self.command_history = [] # For storing custom commands
        self.history_index = -1   # For navigating command history

        # For command acknowledgment feedback
        self._pending_cmd = None
        self._pending_cmd_label = None
        self._terminal_line_count = 0
        self._max_terminal_lines = 5000  # Limit to prevent memory issues

        self._configure_ttk_style()
        self.setup_ui()
        self.root.after(100, self.process_queue)

        # Load initial profile after UI is set up (also attaches branding)
        self.switch_profile(None)

    def _configure_ttk_style(self):
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure(
            "TCombobox",
            fieldbackground=MD3["surface_lowest"],
            background=MD3["surface_container"],
            foreground=MD3["on_surface"],
            bordercolor=MD3["outline"],
            arrowcolor=MD3["on_primary_container"],
            insertcolor=MD3["on_surface"],
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", MD3["surface_lowest"])],
            foreground=[("readonly", MD3["on_surface"])],
            bordercolor=[("focus", MD3["primary"])],
        )
        # Combobox dropdown listbox colors
        self.root.option_add("*TCombobox*Listbox.background", MD3["surface_container"])
        self.root.option_add("*TCombobox*Listbox.foreground", MD3["on_surface"])
        self.root.option_add("*TCombobox*Listbox.selectBackground", MD3["primary_dim"])
        self.root.option_add("*TCombobox*Listbox.selectForeground", MD3["on_primary_container"])

    def _get_label_for_cmd(self, cmd):
        """Look up human-readable label for a command."""
        profile_key = self.profile_map.get(self.profile_var.get(), 'pico')
        profile_data = SENSOR_PROFILES[profile_key]
        for group in profile_data['groups']:
            for btn in group['buttons']:
                if btn['cmd'] == cmd:
                    return btn['label']
        return cmd  # Fallback to raw command

    def _try_auto_detect_sensor(self, line):
        """Auto-detect sensor profile from GAIA sign-on message."""
        if not line.startswith('GAIA'):
            return

        sensor_detect_map = {
            'ALPHA': 'alpha',
            'Theta': 'theta',
            'SIGMA': 'sigma',
        }

        for keyword, profile_key in sensor_detect_map.items():
            if keyword in line:
                # Check for Pico variant
                if profile_key == 'theta' and 'Pico' in line:
                    profile_key = 'pico'

                # Get current profile
                current_key = self.profile_map.get(self.profile_var.get(), 'pico')
                if current_key != profile_key:
                    # Find the display name for this profile
                    profile_data = SENSOR_PROFILES[profile_key]
                    new_name = profile_data['name']
                    self.profile_var.set(new_name)
                    self.switch_profile(None)
                    self.msg_queue.put(('sys', f"\n⚙ Auto-detected: {new_name}\n"))
                return

    def _get_ack_feedback(self, cmd, response):
        """Generate acknowledgment feedback for a command response."""
        feedback_map = {
            'A': 'All Axes selected',
            'N': 'North/South axis selected',
            'E': 'East/West axis selected',
            'Z': 'Vertical axis selected',
            'I': 'Calibration enabled',
            'K': 'Calibration disabled',
            'G': 'Low Gain set',
            'H': 'High Gain set',
            '1G': '0.5g Gain set',
            '2G': '1g Gain set',
            '3G': '2g Gain set',
            '4G': '4g Gain set',
            'S': 'Short Period mode',
            'B': 'Long Period mode',
            'Q': 'Parameters stored',
            'L': 'Axes locked',
            'U': 'Axes unlocked',
        }
        if cmd in feedback_map:
            return feedback_map[cmd]
        elif cmd in ['C', 'M', '<', '>']:
            # Mass commands — use the response
            return response.strip() if response.strip() else f"{self._pending_cmd_label} executed"
        else:
            return f"{self._pending_cmd_label}: {response.strip()}" if self._pending_cmd_label else response.strip()

    def setup_ui(self):
        # --- HEADER & CONNECTION BAR ---
        header_frame = tk.Frame(self.root, bg=MD3["surface"], pady=15, padx=20,
                                highlightthickness=1,
                                highlightbackground=MD3["outline"])
        header_frame.pack(fill=tk.X)

        # Header logo
        self._header_logo = load_logo(max_height=36)
        if self._header_logo is not None:
            tk.Label(header_frame, image=self._header_logo,
                     bg=MD3["surface"], bd=0).pack(side=tk.LEFT, padx=(0, 12))

        self.main_title_lbl = tk.Label(
            header_frame, text="GaiaCode Universal Terminal",
            bg=MD3["surface"], fg=MD3["on_surface"],
            font=("Segoe UI", 16, "bold"))
        self.main_title_lbl.pack(side=tk.LEFT)

        # Profile Selector
        self.profile_var = tk.StringVar(value='pico') # Initialize to 'pico' key
        profile_names = [v['name'] for v in SENSOR_PROFILES.values()]

        self.profile_map = {v['name']: k for k, v in SENSOR_PROFILES.items()} # Map name to key

        profile_combo = ttk.Combobox(header_frame, values=profile_names, state="readonly", font=("Segoe UI", 12),
                                     textvariable=self.profile_var) # Bind to self.profile_var
        profile_combo.set(SENSOR_PROFILES['pico']['name']) # Set initial display value
        profile_combo.bind('<<ComboboxSelected>>', self.switch_profile)
        profile_combo.pack(side=tk.RIGHT, padx=10)

        tk.Label(header_frame, text="Sensor Profile:", bg=MD3["surface"],
                 fg=MD3["on_surface_variant"],
                 font=("Segoe UI", 10)).pack(side=tk.RIGHT)

        # Connection Bar
        conn_frame = tk.Frame(self.root, bg=MD3["surface_low"], pady=10, padx=20,
                              highlightbackground=MD3["outline"], highlightthickness=1)
        conn_frame.pack(fill=tk.X)

        tk.Label(conn_frame, text="COM Port:", bg=MD3["surface_low"],
                 fg=MD3["on_surface_variant"], font=FONT_SANS).pack(side=tk.LEFT, padx=(0, 5))
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(conn_frame, textvariable=self.port_var, width=20, font=("Segoe UI", 9)) # Wider for descriptions
        self.port_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.refresh_ports()

        btn_refresh = tk.Button(conn_frame, text="↻", width=3, command=self.refresh_ports,
                                bg=MD3["primary"], fg=MD3["on_primary"],
                                activebackground=MD3["primary_hover"],
                                activeforeground=MD3["on_primary"],
                                relief="flat", bd=0, cursor="hand2",
                                font=("Segoe UI", 9, "bold"))
        btn_refresh.pack(side=tk.LEFT, padx=(0, 15))

        tk.Label(conn_frame, text="Baud:", bg=MD3["surface_low"],
                 fg=MD3["on_surface_variant"], font=FONT_SANS).pack(side=tk.LEFT, padx=(0, 5))
        self.baud_var = tk.StringVar(value="9600")
        baud_combo = ttk.Combobox(conn_frame, textvariable=self.baud_var, values=["9600", "19200", "38400", "57600", "115200"], width=10, font=("Segoe UI", 9))
        baud_combo.pack(side=tk.LEFT, padx=(0, 15))

        self.crlf_var = tk.BooleanVar(value=True)
        tk.Checkbutton(conn_frame, text="Send CR+LF (\\r\\n)", variable=self.crlf_var,
                       bg=MD3["surface_low"], fg=MD3["on_surface"],
                       activebackground=MD3["surface_low"],
                       activeforeground=MD3["on_surface"],
                       selectcolor=MD3["surface_lowest"],
                       font=FONT_SANS).pack(side=tk.LEFT, padx=(0, 15))

        self.timestamp_var = tk.BooleanVar(value=False) # For timestamping terminal output
        tk.Checkbutton(conn_frame, text="Timestamps", variable=self.timestamp_var,
                       bg=MD3["surface_low"], fg=MD3["on_surface"],
                       activebackground=MD3["surface_low"],
                       activeforeground=MD3["on_surface"],
                       selectcolor=MD3["surface_lowest"],
                       font=FONT_SANS).pack(side=tk.LEFT, padx=(0, 15))

        self.btn_connect = tk.Button(conn_frame, text="CONNECT",
                                     bg=MD3["primary"], fg=MD3["on_primary"],
                                     activebackground=MD3["primary_hover"],
                                     activeforeground=MD3["on_primary"],
                                     disabledforeground=MD3["on_surface_variant"],
                                     font=("Segoe UI", 9, "bold"), relief="flat", bd=0,
                                     cursor="hand2",
                                     command=self.connect_serial, width=12)
        self.btn_connect.pack(side=tk.LEFT)

        self.btn_disconnect = tk.Button(conn_frame, text="DISCONNECT",
                                        bg=MD3["error"], fg=MD3["on_error"],
                                        activebackground=MD3["error"],
                                        activeforeground=MD3["on_error"],
                                        disabledforeground=MD3["on_surface_variant"],
                                        font=("Segoe UI", 9, "bold"), relief="flat", bd=0,
                                        cursor="hand2",
                                        command=self.disconnect_serial, width=12,
                                        state=tk.DISABLED)
        self.btn_disconnect.pack(side=tk.LEFT, padx=5)

        # Visual LED Status Indicator
        self.status_led = tk.Canvas(conn_frame, width=14, height=14,
                                    bg=MD3["surface_low"], highlightthickness=0)
        self.status_led.pack(side=tk.RIGHT, padx=(0, 10))
        self.led_oval = self.status_led.create_oval(2, 2, 12, 12, fill=MD3["error"], outline="") # Start red (Offline)

        self.status_label = tk.Label(conn_frame, text="OFFLINE", bg=MD3["surface_low"],
                                     fg=MD3["on_surface_variant"],
                                     font=("Courier New", 9, "bold"),
                                     padx=5, pady=5, relief=tk.FLAT)
        self.status_label.pack(side=tk.RIGHT)

        # --- MAIN SPLIT WINDOW ---
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10) # Reduced padding

        # LEFT: Dynamic Buttons Area
        self.buttons_container = tk.Frame(main_paned, bg=MD3["surface_low"], padx=10, pady=10,
                                          highlightbackground=MD3["outline"], highlightthickness=1)
        main_paned.add(self.buttons_container, weight=1)

        # RIGHT: Terminal Area
        term_frame = tk.Frame(main_paned, bg=MD3["surface_lowest"],
                              highlightbackground=MD3["outline"], highlightthickness=1)
        main_paned.add(term_frame, weight=1)

        # Terminal Header
        term_header = tk.Frame(term_frame, bg=MD3["surface"], pady=5, padx=10)
        term_header.pack(fill=tk.X)
        tk.Label(term_header, text="SERIAL MONITOR", bg=MD3["surface"],
                 fg=MD3["on_surface_variant"],
                 font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT)
        tk.Button(term_header, text="CLEAR", bg=MD3["surface_container"],
                  fg=MD3["on_surface"], activebackground=MD3["surface_high"],
                  activeforeground=MD3["on_surface"], relief="flat", bd=0,
                  cursor="hand2",
                  font=("Segoe UI", 8, "bold"),
                  command=self.clear_terminal).pack(side=tk.RIGHT, padx=(0, 5))
        tk.Button(term_header, text="SAVE LOG", bg=MD3["primary"],
                  fg=MD3["on_primary"], activebackground=MD3["primary_hover"],
                  activeforeground=MD3["on_primary"], relief="flat", bd=0,
                  cursor="hand2",
                  font=("Segoe UI", 8, "bold"),
                  command=self.save_terminal_log).pack(side=tk.RIGHT)

        # Terminal Text Box — MD3 lowest surface with high-contrast green mono
        self.txt_term = tk.Text(term_frame, bg=MD3["surface_lowest"], fg="#4ade80",
                                font=("Courier New", 10), wrap=tk.WORD,
                                insertbackground=MD3["on_surface"],
                                selectbackground=MD3["primary_dim"],
                                selectforeground=MD3["on_primary_container"],
                                relief="flat", bd=0)
        self.txt_term.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Terminal Tags for coloring
        self.txt_term.tag_configure("tx", foreground=MD3["info"], font=("Courier New", 10, "bold"))
        self.txt_term.tag_configure("rx", foreground="#4ade80")
        self.txt_term.tag_configure("sys", foreground=MD3["on_warning_container"], font=("Courier New", 10, "italic"))
        self.txt_term.tag_configure("timestamp", foreground="#64748b", font=("Courier New", 9, "italic"))

        # Terminal Input
        input_frame = tk.Frame(term_frame, bg=MD3["surface"], pady=10, padx=10)
        input_frame.pack(fill=tk.X)
        self.cmd_entry = tk.Entry(input_frame, font=("Courier New", 11),
                                  bg=MD3["surface_lowest"], fg="#4ade80",
                                  insertbackground=MD3["on_surface"],
                                  relief="solid", bd=1,
                                  highlightthickness=1,
                                  highlightcolor=MD3["primary"],
                                  highlightbackground=MD3["outline"])
        self.cmd_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.cmd_entry.bind("<Return>", lambda e: self.send_custom_cmd())
        self.cmd_entry.bind("<Up>", self.navigate_history)
        self.cmd_entry.bind("<Down>", self.navigate_history)

        tk.Button(input_frame, text="SEND", bg=MD3["primary"], fg=MD3["on_primary"],
                  activebackground=MD3["primary_hover"],
                  activeforeground=MD3["on_primary"], relief="flat", bd=0,
                  cursor="hand2",
                  font=("Segoe UI", 9, "bold"),
                  command=self.send_custom_cmd).pack(side=tk.RIGHT)

    def refresh_ports(self):
        ports = serial.tools.list_ports.comports()
        display_ports = ["{} - {}".format(p.device, p.description) for p in ports]
        self.port_combo['values'] = display_ports
        if display_ports:
            self.port_combo.set(display_ports[0])
        else:
            self.port_combo.set("No ports found")
            self.port_combo.config(state=tk.DISABLED) # Disable if no ports

    def load_branding(self):
        """Load and display GaiaCode logo at the bottom of the buttons panel."""
        img = load_logo(max_width=180)

        self.branding_frame = tk.Frame(self.buttons_container, bg=MD3["surface_low"])
        self.branding_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))

        if img is not None:
            self.branding_img = img
            tk.Label(self.branding_frame, image=self.branding_img,
                     bg=MD3["surface_low"], bd=0).pack(pady=(5, 2))
        else:
            tk.Label(self.branding_frame, text="GaiaCode", bg=MD3["surface_low"],
                     fg=MD3["primary"],
                     font=("Segoe UI", 12, "bold")).pack(pady=(5, 0))
        tk.Label(self.branding_frame, text="www.gaiacode.com", bg=MD3["surface_low"],
                 fg="#64748b",
                 font=("Segoe UI", 8), cursor="hand2").pack(pady=(0, 5))

    def switch_profile(self, event):
        selected_name = self.profile_var.get() # Get from StringVar
        profile_key = self.profile_map.get(selected_name, 'pico')

        profile_data = SENSOR_PROFILES[profile_key]

        # Update main title with symbol and name
        self.main_title_lbl.config(text=f"{profile_data['name']} Terminal")

        # Clear existing buttons (branding frame is re-added afterwards)
        for widget in self.buttons_container.winfo_children():
            widget.destroy()

        # Attach branding FIRST: pack(side=BOTTOM) claims its slice up front,
        # otherwise pack squeezes it to nothing when the groups fill the panel.
        self.load_branding()

        # Generate new buttons
        for group in profile_data['groups']:
            group_frame = tk.LabelFrame(self.buttons_container, text=group['title'],
                                        font=("Segoe UI", 10, "bold"),
                                        bg=MD3["surface_low"],
                                        fg=MD3["on_primary_container"],
                                        bd=1, relief="solid",
                                        highlightthickness=0,
                                        padx=5, pady=5)
            group_frame.configure(highlightbackground=MD3["outline"])
            group_frame.pack(fill=tk.X, pady=(0, 10))

            # Grid layout inside group
            btn_grid_frame = tk.Frame(group_frame, bg=MD3["surface_low"]) # Frame for button grid
            btn_grid_frame.pack(fill=tk.BOTH, expand=True)

            col = 0
            row = 0
            for btn_data in group['buttons']:
                theme = THEMES.get(group['type'], {'bg': MD3['surface_container'],
                                                   'fg': MD3['on_surface'],
                                                   'active_bg': MD3['surface_high']})

                # Build button text with icon
                icon = BUTTON_ICONS.get(btn_data['label'], '•')
                btn_text = f"{icon}\n{btn_data['label']}\n\"{btn_data['cmd']}\""

                btn = tk.Button(btn_grid_frame,
                                text=btn_text,
                                command=lambda c=btn_data['cmd']: self.send_cmd(c),
                                font=("Segoe UI", 8, "bold"),
                                bg=theme['bg'],
                                fg=theme['fg'],
                                relief="flat",
                                bd=1,
                                highlightbackground=MD3['outline'],
                                highlightthickness=1,
                                activebackground=theme['active_bg'],
                                activeforeground=theme['fg'],
                                cursor="hand2",
                                padx=5, pady=6,
                                wraplength=90,
                                justify=tk.CENTER)

                btn.grid(row=row, column=col, padx=3, pady=3, sticky="nsew")
                btn_grid_frame.columnconfigure(col, weight=1)

                col += 1
                if col > 3:  # 4 buttons per row
                    col = 0
                    row += 1

        self.msg_queue.put(('sys', f"\n--- Switched to {profile_data['name']} Commands ---\n"))

    # =========================================================
    # SERIAL LOGIC
    # =========================================================
    def connect_serial(self):
        port_full_name = self.port_var.get()
        if " - " in port_full_name:
            port = port_full_name.split(" - ")[0] # Extract COM port only
        else:
            port = port_full_name

        baud = self.baud_var.get()
        if not port or port == "No ports found":
            messagebox.showwarning("Warning", "Please select a valid COM port.")
            return

        self.btn_connect.config(state=tk.DISABLED, text="CONNECTING...")
        self.status_label.config(text="CONNECTING...", fg=MD3["warning"])
        self.status_led.itemconfig(self.led_oval, fill=MD3["warning"]) # LED Amber
        self.root.update_idletasks() # Force UI update

        try:
            self.serial_port = serial.Serial(port, int(baud), timeout=0.05)
            self.keep_reading = True

            self.read_thread = threading.Thread(target=self.read_serial_loop, daemon=True)
            self.read_thread.start()

            self.btn_connect.config(state=tk.DISABLED, text="CONNECT",
                                    bg=MD3["success"], fg=MD3["on_primary"])
            self.btn_disconnect.config(state=tk.NORMAL)
            self.port_combo.config(state=tk.DISABLED)

            self.status_label.config(text=f"CONNECTED @ {port} ({baud})", fg=MD3["success"])
            self.status_led.itemconfig(self.led_oval, fill=MD3["success"]) # LED Green

            self.msg_queue.put(('sys', f"\n--- Connected to {port} @ {baud} baud ---\n"))
        except Exception as e:
            self.btn_connect.config(state=tk.NORMAL, text="CONNECT",
                                    bg=MD3["primary"], fg=MD3["on_primary"]) # Revert on error
            self.btn_disconnect.config(state=tk.DISABLED)
            self.port_combo.config(state=tk.NORMAL)

            self.status_label.config(text="OFFLINE", fg=MD3["on_surface_variant"])
            self.status_led.itemconfig(self.led_oval, fill=MD3["error"]) # LED Red on error
            messagebox.showerror("Connection Error", f"Failed to connect to {port}:\n{str(e)}")

    def disconnect_serial(self):
        self.keep_reading = False
        if self.read_thread and self.read_thread.is_alive():
            # Attempt to join thread gracefully
            self.read_thread.join(timeout=0.5)

        if self.serial_port and self.serial_port.is_open:
            try:
                self.serial_port.close()
            except Exception as e:
                self.msg_queue.put(('sys', f"\nError closing port: {str(e)}\n"))

        self.btn_connect.config(state=tk.NORMAL, text="CONNECT",
                                bg=MD3["primary"], fg=MD3["on_primary"])
        self.btn_disconnect.config(state=tk.DISABLED)
        self.port_combo.config(state=tk.NORMAL)

        self.status_label.config(text="OFFLINE", fg=MD3["on_surface_variant"])
        self.status_led.itemconfig(self.led_oval, fill=MD3["error"]) # LED Red

        self.msg_queue.put(('sys', f"\n--- Port Closed ---\n"))

    def read_serial_loop(self):
        while self.keep_reading and self.serial_port and self.serial_port.is_open:
            try:
                if self.serial_port.in_waiting > 0:
                    data = self.serial_port.read(self.serial_port.in_waiting).decode('utf-8', errors='replace')
                    self.msg_queue.put(('rx', data))
                else:
                    time.sleep(0.01)
            except serial.SerialException as e: # Catch specific serial exceptions for robustness
                self.msg_queue.put(('sys', f"\nSerial Read Error: {str(e)}\n"))
                self.root.after(0, self.disconnect_serial) # Disconnect and update UI on critical error
                break
            except Exception as e:
                self.msg_queue.put(('sys', f"\nUnhandled Read Error: {str(e)}\n"))
                self.root.after(0, self.disconnect_serial)
                break

    def send_cmd(self, cmd):
        if not self.serial_port or not self.serial_port.is_open:
            messagebox.showwarning("Warning", "Not connected to a COM port!")
            return

        # Wake the sensor first — send blank line to exit sleep mode
        try:
            self.serial_port.write(b"\r\n")
            time.sleep(0.15)  # Brief pause to let sensor wake
        except Exception:
            pass

        final_cmd = cmd
        if self.crlf_var.get():
            final_cmd += "\r\n"

        try:
            self.serial_port.write(final_cmd.encode('utf-8'))
            self.msg_queue.put(('tx', f"\n→ {cmd}\n"))
            # Store pending command for acknowledgment feedback
            self._pending_cmd = cmd
            self._pending_cmd_label = self._get_label_for_cmd(cmd)
        except Exception as e:
            self.msg_queue.put(('sys', f"\nWrite Error: {str(e)}\n"))

    def send_custom_cmd(self):
        cmd = self.cmd_entry.get()
        if cmd:
            self.send_cmd(cmd)
            # Add to history if not empty and not a duplicate of the last command
            if not self.command_history or (self.command_history and self.command_history[-1] != cmd):
                self.command_history.append(cmd)
            self.history_index = -1 # Reset index after new command is sent
            self.cmd_entry.delete(0, tk.END)
            self.flash_widget_background(self.cmd_entry,
                                         original_bg=MD3["surface_lowest"],
                                         flash_color=MD3["success"]) # Flash green

    def navigate_history(self, event):
        if not self.command_history: return

        if event.keysym == "Up":
            if self.history_index == -1: # First time pressing Up
                self.history_index = len(self.command_history) - 1
            else:
                self.history_index = max(0, self.history_index - 1)
        elif event.keysym == "Down":
            if self.history_index == -1 or self.history_index == len(self.command_history) - 1: # At latest command or beyond
                self.history_index = -1 # Clear entry or show next empty
                self.cmd_entry.delete(0, tk.END)
                return
            else:
                self.history_index = min(len(self.command_history) - 1, self.history_index + 1)

        if self.history_index != -1:
            self.cmd_entry.delete(0, tk.END)
            self.cmd_entry.insert(0, self.command_history[self.history_index])

    def flash_widget_background(self, widget, original_bg, flash_color=MD3["success"], duration_ms=200):
        widget.config(bg=flash_color)
        self.root.after(duration_ms, lambda: widget.config(bg=original_bg))

    # =========================================================
    # TERMINAL UI UPDATES
    # =========================================================
    def process_queue(self):
        # Process all pending messages from the serial thread
        while not self.msg_queue.empty():
            msg_type, msg_text = self.msg_queue.get()

            # Auto-detect sensor from RX data
            if msg_type == 'rx':
                for line in msg_text.split('\n'):
                    self._try_auto_detect_sensor(line.strip())

            if msg_type == 'rx' and self.timestamp_var.get():
                timestamp = time.strftime("[%H:%M:%S] ", time.localtime())
                self.txt_term.insert(tk.END, timestamp, "timestamp")

            self.txt_term.insert(tk.END, msg_text, msg_type)
            self.txt_term.see(tk.END) # Auto-scroll

            # Track line count and trim if needed
            self._terminal_line_count += msg_text.count('\n') + 1
            if self._terminal_line_count > self._max_terminal_lines:
                # Delete first 500 lines to free memory
                self.txt_term.delete("1.0", "501.0")
                self._terminal_line_count -= 500

            # Show acknowledgment feedback for RX responses
            if msg_type == 'rx' and self._pending_cmd:
                # Skip Wake/Sleep status messages
                trimmed = msg_text.strip()
                if trimmed and trimmed not in ['Wake', 'Sleep']:
                    feedback = self._get_ack_feedback(self._pending_cmd, trimmed)
                    # Show brief feedback in status
                    self.status_label.config(text=f"✓ {feedback}", fg=MD3["success"])
                    # Reset pending after a moment
                    self.root.after(3000, self._reset_status)
                    self._pending_cmd = None
                    self._pending_cmd_label = None

        # Reschedule the queue check
        self.root.after(50, self.process_queue)

    def _reset_status(self):
        """Reset status label to show connection state."""
        if self.serial_port and self.serial_port.is_open:
            port = self.serial_port.port
            baud = self.serial_port.baudrate
            self.status_label.config(text=f"CONNECTED @ {port} ({baud})", fg=MD3["success"])
        else:
            self.status_label.config(text="OFFLINE", fg=MD3["on_surface_variant"])

    def clear_terminal(self):
        self.txt_term.delete(1.0, tk.END)
        self._terminal_line_count = 0

    def save_terminal_log(self):
        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(self.txt_term.get("1.0", tk.END))
                messagebox.showinfo("Save Log", "Terminal log saved successfully!")
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save log: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = SensorTerminalApp(root)
    root.mainloop()
