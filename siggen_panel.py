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
}

FONT_SANS = ("Segoe UI", 10)
FONT_SANS_BOLD = ("Segoe UI", 10, "bold")
FONT_TITLE = ("Segoe UI", 13, "bold")

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


class SigGen33120A_Panel:
    def __init__(self, root):
        self.root = root
        self.root.title("GaiaCode — 33120A Signal Generator Control")
        self.root.geometry("580x560")
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

        self.shapes = {
            "Sine": "SIN",
            "Square": "SQU",
            "Triangle": "TRI",
            "Ramp": "RAMP",
            "Noise": "NOIS",
            "DC": "DC"
        }
        self.shape_buttons = {} # To store references to waveform buttons
        self.active_shape_button = None # To keep track of the currently active button

        self.create_widgets()
        self.update_ui_state() # Call initially to set correct states based on default selection

    # ------------------------------------------------------------- factories
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

    def _dark_entry(self, parent, width, initial):
        entry = tk.Entry(
            parent, width=width,
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
        entry.insert(0, initial)
        return entry

    def _primary_button(self, parent, text, command, width=10, font=FONT_SANS_BOLD):
        return tk.Button(
            parent, text=text, command=command, width=width,
            bg=MD3["primary"], fg=MD3["on_primary"],
            activebackground=MD3["primary_hover"],
            activeforeground=MD3["on_primary"],
            disabledforeground=MD3["on_surface_variant"],
            font=font, relief="flat", bd=0,
            highlightthickness=0, cursor="hand2",
        )

    def _tonal_button(self, parent, text, command, width=8, font=("Segoe UI", 9, "bold")):
        return tk.Button(
            parent, text=text, command=command, width=width,
            bg=MD3["surface_container"], fg=MD3["on_surface"],
            activebackground=MD3["surface_high"],
            activeforeground=MD3["on_surface"],
            disabledforeground=MD3["on_surface_variant"],
            font=font, relief="solid", bd=1,
            highlightthickness=0, cursor="hand2",
        )

    def _set_tonal_active(self, button, active):
        if active:
            button.config(relief="sunken", bg=MD3["primary"],
                          fg=MD3["on_primary"])
        else:
            button.config(relief="raised", bg=MD3["surface_container"],
                          fg=MD3["on_surface"])

    # ---------------------------------------------------------------- widgets
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
        tk.Label(title_box, text="33120A Signal Generator",
                 font=FONT_TITLE, bg=MD3["surface"],
                 fg=MD3["on_surface"]).pack(anchor="w")
        tk.Label(title_box, text="Waveform Control  ·  GaiaCode Ltd",
                 font=("Segoe UI", 9), bg=MD3["surface"],
                 fg=MD3["on_primary_container"]).pack(anchor="w")

        # Connection Frame
        conn_frame = self._card("Connection")

        tk.Label(conn_frame, text="Port/Address:", bg=MD3["surface_low"],
                 fg=MD3["on_surface_variant"],
                 font=FONT_SANS).grid(row=0, column=0, sticky="w", pady=2)

        self.port_entry = self._dark_entry(conn_frame, 20, "COM5")
        self.port_entry.grid(row=0, column=1, padx=5, pady=2)

        self.connect_btn = self._primary_button(conn_frame, "Connect",
                                                self.toggle_connection, width=10)
        self.connect_btn.grid(row=0, column=2, padx=5, pady=2)

        # Waveform Settings Frame
        set_frame = self._card("Waveform Settings")

        # Waveform Selection Buttons
        tk.Label(set_frame, text="Waveform:", bg=MD3["surface_low"],
                 fg=MD3["on_surface_variant"],
                 font=FONT_SANS).grid(row=0, column=0, sticky="e", pady=5, padx=5)

        waveform_button_frame = tk.Frame(set_frame, bg=MD3["surface_low"])
        waveform_button_frame.grid(row=0, column=1, columnspan=2, sticky="w", pady=5)

        self.shape_var = tk.StringVar(value=list(self.shapes.keys())[0]) # Set initial value

        for i, shape_name in enumerate(self.shapes.keys()):
            button = self._tonal_button(
                waveform_button_frame, text=shape_name,
                command=lambda s=shape_name: self.select_waveform(s),
                width=8)
            button.pack(side="left", padx=2, pady=2)
            self.shape_buttons[shape_name] = button # Store button reference

        # Frequency
        tk.Label(set_frame, text="Frequency:", bg=MD3["surface_low"],
                 fg=MD3["on_surface_variant"],
                 font=FONT_SANS).grid(row=1, column=0, sticky="e", pady=5)
        self.freq_entry = self._dark_entry(set_frame, 12, "1")
        self.freq_entry.grid(row=1, column=1, padx=5, sticky="w")

        # Frequency Unit Buttons
        freq_unit_frame = tk.Frame(set_frame, bg=MD3["surface_low"])
        freq_unit_frame.grid(row=1, column=2, sticky="w")
        self.freq_unit_var = tk.StringVar(value="kHz") # Set initial value
        self.freq_unit_buttons = {}
        for unit_name in ["Hz", "kHz", "MHz"]:
            button = self._tonal_button(
                freq_unit_frame, text=unit_name,
                command=lambda u=unit_name: self.select_unit(self.freq_unit_var, u, self.freq_unit_buttons),
                width=4, font=("Segoe UI", 8))
            button.pack(side="left", padx=1, pady=1)
            self.freq_unit_buttons[unit_name] = button

        # Amplitude
        tk.Label(set_frame, text="Amplitude:", bg=MD3["surface_low"],
                 fg=MD3["on_surface_variant"],
                 font=FONT_SANS).grid(row=2, column=0, sticky="e", pady=5)
        self.amp_entry = self._dark_entry(set_frame, 12, "1.0")
        self.amp_entry.grid(row=2, column=1, padx=5, sticky="w")

        # Amplitude Unit Buttons
        amp_unit_frame = tk.Frame(set_frame, bg=MD3["surface_low"])
        amp_unit_frame.grid(row=2, column=2, sticky="w")
        self.amp_unit_var = tk.StringVar(value="VPP") # Set initial value
        self.amp_unit_buttons = {}
        for unit_name in ["VPP", "VRMS", "DBM"]:
            button = self._tonal_button(
                amp_unit_frame, text=unit_name,
                command=lambda u=unit_name: self.select_unit(self.amp_unit_var, u, self.amp_unit_buttons),
                width=4, font=("Segoe UI", 8))
            button.pack(side="left", padx=1, pady=1)
            self.amp_unit_buttons[unit_name] = button

        # DC Offset
        tk.Label(set_frame, text="DC Offset:", bg=MD3["surface_low"],
                 fg=MD3["on_surface_variant"],
                 font=FONT_SANS).grid(row=3, column=0, sticky="e", pady=5)
        self.offs_entry = self._dark_entry(set_frame, 12, "0.0")
        self.offs_entry.grid(row=3, column=1, padx=5, sticky="w")

        # DC Offset Unit Buttons
        offs_unit_frame = tk.Frame(set_frame, bg=MD3["surface_low"])
        offs_unit_frame.grid(row=3, column=2, sticky="w")
        self.offs_unit_var = tk.StringVar(value="V") # Set initial value
        self.offs_unit_buttons = {}
        for unit_name in ["V", "mV"]:
            button = self._tonal_button(
                offs_unit_frame, text=unit_name,
                command=lambda u=unit_name: self.select_unit(self.offs_unit_var, u, self.offs_unit_buttons),
                width=4, font=("Segoe UI", 8))
            button.pack(side="left", padx=1, pady=1)
            self.offs_unit_buttons[unit_name] = button

        # Control Frame
        ctrl_frame = tk.Frame(self.root, bg=MD3["background"])
        ctrl_frame.pack(fill="x", padx=10, pady=10)

        self.apply_btn = tk.Button(
            ctrl_frame, text="APPLY SETTINGS", command=self.apply_settings,
            font=("Segoe UI", 12, "bold"),
            bg=MD3["primary"], fg=MD3["on_primary"],
            activebackground=MD3["primary_hover"],
            activeforeground=MD3["on_primary"],
            disabledforeground=MD3["on_surface_variant"],
            relief="flat", bd=0, cursor="hand2",
            state="disabled", height=2)
        self.apply_btn.pack(fill="x")

    def select_waveform(self, shape_name):
        self.shape_var.set(shape_name)
        self.update_ui_state()

    def select_unit(self, var, unit_name, button_dict):
        var.set(unit_name)
        # Highlight the selected unit button
        for name, button in button_dict.items():
            self._set_tonal_active(button, name == unit_name)

    def _set_row_enabled(self, entry, unit_buttons, enabled):
        entry.config(state="normal" if enabled else "disabled")
        for btn in unit_buttons.values():
            btn.config(state="normal" if enabled else "disabled")
        if enabled:
            # Re-apply active highlight so state isn't lost on re-enable
            var = {id(self.freq_unit_buttons): self.freq_unit_var,
                   id(self.amp_unit_buttons): self.amp_unit_var,
                   id(self.offs_unit_buttons): self.offs_unit_var}[id(unit_buttons)]
            self.select_unit(var, var.get(), unit_buttons)

    def update_ui_state(self, event=None):
        shape = self.shape_var.get()

        # Highlight selected waveform button
        for shape_name, button in self.shape_buttons.items():
            self._set_tonal_active(button, shape_name == shape)

        # Initialize unit button highlights (now that self.select_unit exists)
        self.select_unit(self.freq_unit_var, self.freq_unit_var.get(), self.freq_unit_buttons)
        self.select_unit(self.amp_unit_var, self.amp_unit_var.get(), self.amp_unit_buttons)
        self.select_unit(self.offs_unit_var, self.offs_unit_var.get(), self.offs_unit_buttons)

        # Existing logic for enabling/disabling entry fields
        if shape == "DC":
            self._set_row_enabled(self.freq_entry, self.freq_unit_buttons, False)
            self._set_row_enabled(self.amp_entry, self.amp_unit_buttons, False)
            # DC Offset remains enabled for DC
            self._set_row_enabled(self.offs_entry, self.offs_unit_buttons, True)
        elif shape == "Noise":
            self._set_row_enabled(self.freq_entry, self.freq_unit_buttons, False)
            self._set_row_enabled(self.amp_entry, self.amp_unit_buttons, True)
            self._set_row_enabled(self.offs_entry, self.offs_unit_buttons, True)
        else:
            self._set_row_enabled(self.freq_entry, self.freq_unit_buttons, True)
            self._set_row_enabled(self.amp_entry, self.amp_unit_buttons, True)
            self._set_row_enabled(self.offs_entry, self.offs_unit_buttons, True)

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
                # 33120A Defaults: 9600, 8 Data, None Parity, 1 Stop Bit, XON/XOFF Flow (critical!)
                self.instrument = self.rm.open_resource(
                    visa_resource,
                    baud_rate=9600,
                    data_bits=8,
                    parity=pyvisa.constants.Parity.none,
                    stop_bits=pyvisa.constants.StopBits.one,
                    flow_control=pyvisa.constants.VI_ASRL_FLOW_XON_XOFF, # Changed to XON/XOFF
                    read_termination='\n',
                    write_termination='\n',
                    timeout=10000 # Increased timeout to 10s for robust initial connection
                )

                # Initialize like hardware.py does, with increased delays
                self.instrument.write("*RST")
                time.sleep(0.5) # Increased sleep after reset
                self.instrument.write("OUTP:LOAD INF")
                time.sleep(0.2) # Increased sleep

                idn = self.instrument.query("*IDN?")

                self.connect_btn.config(text="Disconnect", state="normal",
                                        bg=MD3["error"], fg=MD3["on_error"],
                                        activebackground=MD3["error"],
                                        activeforeground=MD3["on_error"])
                self.port_entry.config(state="disabled")
                self.apply_btn.config(state="normal")
                messagebox.showinfo("Connected", f"Connected to:\n{idn}")

            except Exception as e:
                self._reset_connect_button()
                messagebox.showerror("Connection Error", f"Failed to connect to {visa_resource}.\n\nDetails: {str(e)}")
                self.instrument = None
        else:
            try:
                # Fix: Check if self.instrument is not None before attempting to close
                if self.instrument:
                    self.instrument.close()
            except Exception as e:
                # Log or display error if disconnect fails, but don't block finally
                print(f"Error during disconnect: {e}")
            finally:
                self.instrument = None
                self._reset_connect_button()
                self.port_entry.config(state="normal")
                self.apply_btn.config(state="disabled")

    def _reset_connect_button(self):
        self.connect_btn.config(text="Connect", state="normal",
                                bg=MD3["primary"], fg=MD3["on_primary"],
                                activebackground=MD3["primary_hover"],
                                activeforeground=MD3["on_primary"])

    def apply_settings(self):
        if self.instrument is None: return

        shape_str = self.shapes[self.shape_var.get()]
        freq_str = f"{self.freq_entry.get()} {self.freq_unit_var.get()}"
        amp_str = f"{self.amp_entry.get()} {self.amp_unit_var.get()}"
        offs_str = f"{self.offs_entry.get()} {self.offs_unit_var.get()}"

        try:
            self.instrument.write(f"FUNC:SHAP {shape_str}")
            if shape_str not in ["DC", "NOIS"]:
                self.instrument.write(f"FREQ {freq_str}")
            if shape_str != "DC":
                self.instrument.write(f"VOLT {amp_str}")
            self.instrument.write(f"VOLT:OFFS {offs_str}")

            self.apply_btn.config(text="SETTINGS APPLIED!", bg=MD3["success"])
            self.root.after(1000, lambda: self.apply_btn.config(
                text="APPLY SETTINGS", bg=MD3["primary"]))

        except Exception as e:
            messagebox.showerror("Command Error", f"Failed to send settings.\n\n{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = SigGen33120A_Panel(root)
    root.mainloop()
