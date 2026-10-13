import os
import time
import tkinter as tk
from tkinter import ttk, messagebox
import pyvisa

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
    "success":               "#10b981",
    "warning":               "#f59e0b",
    "terminal_green":        "#4ade80",
}

FONT_SANS = ("Segoe UI", 10)
FONT_SANS_BOLD = ("Segoe UI", 10, "bold")
FONT_TITLE = ("Segoe UI", 13, "bold")
FONT_READOUT = ("Courier New", 32, "bold")

LOGO_PATHS = [
    "/home/sysop/.hermes/Workspace/branding/Gaiacode.png",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "Gaiacode.png"),
]


def load_logo(target_height=36):
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
        ratio = target_height / img.height
        img = img.resize((max(1, int(img.width * ratio)), target_height),
                         Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception:
        pass

    try:
        img = tk.PhotoImage(file=path)
        factor = max(1, round(img.height() / target_height))
        return img.subsample(factor, factor)
    except Exception:
        return None


class DMM34401A_Panel:
    def __init__(self, root):
        self.root = root
        self.root.title("GaiaCode — 34401A DMM Control Panel")
        self.root.geometry("480x500")
        self.root.resizable(False, False)
        self.root.configure(bg=MD3["background"])

        self.rm = pyvisa.ResourceManager()
        self.instrument = None

        # Branding
        self.logo_img = load_logo(target_height=36)
        if self.logo_img is not None:
            try:
                self.root.iconphoto(False, self.logo_img)
            except Exception:
                pass

        self.functions = {
            "DC Voltage": {"config_cmd": "CONF:VOLT:DC", "unit": "V DC"},
            "AC Voltage": {"config_cmd": "CONF:VOLT:AC", "unit": "V AC"},
            "DC Current": {"config_cmd": "CONF:CURR:DC", "unit": "A DC"},
            "AC Current": {"config_cmd": "CONF:CURR:AC", "unit": "A AC"},
            "2-Wire Ohms": {"config_cmd": "CONF:RES", "unit": "Ω"},
            "4-Wire Ohms": {"config_cmd": "CONF:FRES", "unit": "Ω"},
            "Frequency": {"config_cmd": "CONF:FREQ", "unit": "Hz"},
            "Period": {"config_cmd": "CONF:PER", "unit": "s"},
            "Continuity": {"config_cmd": "CONF:CONT", "unit": "Ω"},
            "Diode": {"config_cmd": "CONF:DIOD", "unit": "V"}
        }

        self._configure_ttk_style()
        self.create_widgets()

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

    def _card(self, title):
        frame = tk.LabelFrame(
            self.root, text=f"  {title}  ",
            bg=MD3["surface_low"], fg=MD3["on_surface_variant"],
            font=FONT_SANS_BOLD,
            bd=1, relief="solid", highlightthickness=0,
            padx=10, pady=10,
        )
        frame.configure(highlightbackground=MD3["outline"])
        frame.pack(fill="x", padx=10, pady=(6, 0))
        return frame

    def _reset_connect_button(self):
        self.connect_btn.config(text="Connect", state="normal",
                                bg=MD3["primary"], fg=MD3["on_primary"],
                                activebackground=MD3["primary_hover"],
                                activeforeground=MD3["on_primary"])

    def create_widgets(self):
        # Header / Branding Bar
        header = tk.Frame(self.root, bg=MD3["surface"], height=58,
                          highlightthickness=1,
                          highlightbackground=MD3["outline"])
        header.pack(fill="x")
        header.pack_propagate(False)

        if self.logo_img is not None:
            tk.Label(header, image=self.logo_img,
                     bg=MD3["surface"], bd=0).pack(side="left", padx=(14, 10))

        title_box = tk.Frame(header, bg=MD3["surface"])
        title_box.pack(side="left", pady=8)
        tk.Label(title_box, text="34401A Digital Multimeter",
                 font=FONT_TITLE, bg=MD3["surface"],
                 fg=MD3["on_surface"]).pack(anchor="w")
        tk.Label(title_box, text="Measurement Panel  ·  GaiaCode Ltd",
                 font=("Segoe UI", 9), bg=MD3["surface"],
                 fg=MD3["on_primary_container"]).pack(anchor="w")

        # Connection Frame
        conn_frame = self._card("Connection")

        tk.Label(conn_frame, text="Port/Address:", bg=MD3["surface_low"],
                 fg=MD3["on_surface_variant"],
                 font=FONT_SANS).grid(row=0, column=0, sticky="w")

        self.port_entry = tk.Entry(
            conn_frame, width=20,
            bg=MD3["surface_lowest"], fg=MD3["on_surface"],
            insertbackground=MD3["on_surface"],
            disabledbackground=MD3["surface_container"],
            disabledforeground=MD3["on_surface_variant"],
            relief="solid", bd=1,
            highlightthickness=1,
            highlightcolor=MD3["primary"],
            highlightbackground=MD3["outline"],
            font=FONT_SANS,
        )
        self.port_entry.insert(0, "COM4")
        self.port_entry.grid(row=0, column=1, padx=5)

        self.connect_btn = tk.Button(
            conn_frame, text="Connect", command=self.toggle_connection, width=10,
            bg=MD3["primary"], fg=MD3["on_primary"],
            activebackground=MD3["primary_hover"],
            activeforeground=MD3["on_primary"],
            disabledforeground=MD3["on_surface_variant"],
            font=FONT_SANS_BOLD, relief="flat", bd=0,
            highlightthickness=0, cursor="hand2",
        )
        self.connect_btn.grid(row=0, column=2, padx=5)

        # Measurement Function Frame
        set_frame = self._card("Measurement Function")

        tk.Label(set_frame, text="Function:", bg=MD3["surface_low"],
                 fg=MD3["on_surface_variant"],
                 font=FONT_SANS).grid(row=0, column=0, sticky="w")

        self.func_var = tk.StringVar()
        self.func_combo = ttk.Combobox(set_frame, textvariable=self.func_var,
                                       values=list(self.functions.keys()),
                                       state="readonly", width=25,
                                       font=FONT_SANS)
        self.func_combo.current(0)
        self.func_combo.grid(row=0, column=1, padx=10)

        # Readout Display — MD3 terminal surface with high-contrast green mono
        disp_frame = tk.Frame(self.root, bg=MD3["background"], padx=10, pady=10)
        disp_frame.pack(fill="both", expand=True)

        self.reading_label = tk.Label(
            disp_frame, text="---", font=FONT_READOUT,
            fg=MD3["terminal_green"], bg=MD3["surface_lowest"],
            width=12, anchor="e",
            highlightthickness=1,
            highlightbackground=MD3["outline"])
        self.reading_label.pack(pady=10)

        self.unit_label = tk.Label(disp_frame, text="V DC",
                                   font=("Segoe UI", 14, "bold"),
                                   bg=MD3["background"],
                                   fg=MD3["on_primary_container"])
        self.unit_label.pack()

        self.func_combo.bind("<<ComboboxSelected>>", self.update_unit_display)

        # Control Frame
        ctrl_frame = tk.Frame(self.root, bg=MD3["background"])
        ctrl_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.read_btn = tk.Button(
            ctrl_frame, text="TAKE READING", command=self.take_reading,
            font=("Segoe UI", 12, "bold"),
            bg=MD3["primary"], fg=MD3["on_primary"],
            activebackground=MD3["primary_hover"],
            activeforeground=MD3["on_primary"],
            disabledforeground=MD3["on_surface_variant"],
            relief="flat", bd=0, cursor="hand2",
            state="disabled", height=2)
        self.read_btn.pack(fill="x")

    def update_unit_display(self, event=None):
        selected_func_data = self.functions[self.func_var.get()]
        unit = selected_func_data["unit"]
        config_cmd = selected_func_data["config_cmd"]

        self.unit_label.config(text=unit)
        self.reading_label.config(text="---")

        if self.instrument:
            try:
                self.instrument.write(config_cmd)
                time.sleep(0.1) # Give instrument time to settle
            except Exception as e:
                messagebox.showerror("Configuration Error", f"Failed to configure DMM for {self.func_var.get()}.\n\nDetails: {str(e)}")
                # Optionally disable read_btn if config fails
                self.read_btn.config(state="disabled")

    def toggle_connection(self):
        if self.instrument is None:
            raw_port = self.port_entry.get().strip().upper()

            if raw_port.startswith("COM") and raw_port[3:].isdigit():
                visa_resource = f"ASRL{raw_port[3:]}::INSTR"
            else:
                visa_resource = raw_port

            try:
                self.connect_btn.config(text="Connecting...", state="disabled")
                self.root.update()

                # FORCE CORRECT SERIAL SETTINGS DURING OPEN
                # 34401A Defaults: 9600, 7 Data, Even Parity, 2 Stop Bits (critical!)
                self.instrument = self.rm.open_resource(
                    visa_resource,
                    baud_rate=9600,
                    data_bits=7,
                    parity=pyvisa.constants.Parity.even,
                    stop_bits=pyvisa.constants.StopBits.two,
                    flow_control=pyvisa.constants.VI_ASRL_FLOW_NONE,
                    read_termination='\n',
                    write_termination='\n',
                    timeout=10000 # Increased timeout further (10s) for robust initial connection
                )

                # Initialize like hardware.py does
                self.instrument.write("SYST:REM")
                time.sleep(0.2) # Increased sleep
                self.instrument.write("*RST")
                time.sleep(0.5) # Increased sleep significantly after reset
                self.instrument.write("*CLS")
                time.sleep(0.2) # Increased sleep

                idn = self.instrument.query("*IDN?")

                self.connect_btn.config(text="Disconnect", state="normal",
                                        bg=MD3["error"], fg=MD3["on_error"],
                                        activebackground=MD3["error"],
                                        activeforeground=MD3["on_error"])
                self.port_entry.config(state="disabled")
                self.read_btn.config(state="normal")
                messagebox.showinfo("Connected", f"Connected to:\n{idn}")

                # Initial configuration after connection
                self.update_unit_display()

            except Exception as e:
                self._reset_connect_button()
                messagebox.showerror("Connection Error", f"Failed to connect to {visa_resource}.\n\nDetails: {str(e)}")
                self.instrument = None
        else:
            try:
                # Fix: Check if self.instrument is not None before attempting to write/close
                if self.instrument:
                    self.instrument.write("SYST:LOC")
                    self.instrument.close()
            except Exception as e:
                # Log or display error if disconnect fails, but don't block finally
                print(f"Error during disconnect: {e}")
            finally:
                self.instrument = None
                self._reset_connect_button()
                self.port_entry.config(state="normal")
                self.read_btn.config(state="disabled")
                self.reading_label.config(text="---")

    def take_reading(self):
        if self.instrument is None: return

        self.read_btn.config(text="Reading...", state="disabled", bg=MD3["warning"])
        self.root.update()

        try:
            # Read the measurement (instrument should already be configured)
            raw_reading = self.instrument.query("READ?")
            try:
                float_val = float(raw_reading)
                formatted_val = f"{float_val:.6g}"
                self.reading_label.config(text=formatted_val)
            except ValueError:
                self.reading_label.config(text="OVERLOAD")

        except Exception as e:
            messagebox.showerror("Read Error", f"Failed to take reading.\n\n{str(e)}")
        finally:
            self.read_btn.config(text="TAKE READING", state="normal", bg=MD3["primary"])


if __name__ == "__main__":
    root = tk.Tk()
    app = DMM34401A_Panel(root)
    root.mainloop()
