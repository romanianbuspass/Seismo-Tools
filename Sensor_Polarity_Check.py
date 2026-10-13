import os
import time
import threading
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
    "primary_dim":           "#0a3c3f",   # ~15% teal tint on background

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
}

FONT_SANS = ("Segoe UI", 10)
FONT_SANS_BOLD = ("Segoe UI", 10, "bold")
FONT_TITLE = ("Segoe UI", 13, "bold")
FONT_MONO = ("Consolas", 11, "bold")

LOGO_PATHS = [
    "/home/sysop/.hermes/Workspace/branding/Gaiacode.png",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "Gaiacode.png"),
]


def load_logo(target_height=40):
    """Load the GaiaCode logo with a graceful fallback chain.

    Returns a tk-compatible image object (PIL ImageTk.PhotoImage preferred,
    native tk.PhotoImage as fallback) or None if every path/method fails.
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
        # Native PhotoImage can only downscale by integer factors
        factor = max(1, round(img.height() / target_height))
        return img.subsample(factor, factor)
    except Exception:
        return None


class SensorPolarityTester:
    def __init__(self, root):
        self.root = root
        self.root.title("GaiaCode — Sensor Polarity Tester (HP/Agilent 34401A)")
        self.root.geometry("880x800")
        self.root.resizable(False, False)
        self.root.configure(bg=MD3["background"])

        self.rm = pyvisa.ResourceManager()
        self.instrument = None

        # Branding
        self.logo_img = load_logo(target_height=40)
        if self.logo_img is not None:
            try:
                self.root.iconphoto(False, self.logo_img)
            except Exception:
                pass

        # Test directions: (Display Name, Expected Sign, Short Code)
        self.directions = [
            ("North (N)", "+", "N"),
            ("South (S)", "-", "S"),
            ("East (E)", "+", "E"),
            ("West (W)", "-", "W"),
            ("Up (U)", "+", "U"),
            ("Down (D)", "-", "D")
        ]
        self.current_step_idx = 0
        self.is_sampling = False
        self.active_test_idx = None  # Tracks which direction is actively recording

        self._configure_ttk_style()
        self.create_widgets()

    # ------------------------------------------------------------------ style
    def _configure_ttk_style(self):
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure(
            "Gaia.Treeview",
            background=MD3["surface"],
            fieldbackground=MD3["surface"],
            foreground=MD3["on_surface"],
            bordercolor=MD3["outline"],
            rowheight=26,
            font=FONT_SANS,
        )
        style.configure(
            "Gaia.Treeview.Heading",
            background=MD3["surface_high"],
            foreground=MD3["on_primary_container"],
            bordercolor=MD3["outline"],
            relief="flat",
            font=FONT_SANS_BOLD,
        )
        style.map(
            "Gaia.Treeview",
            background=[("selected", MD3["primary_dim"])],
            foreground=[("selected", MD3["on_primary_container"])],
        )
        style.map(
            "Gaia.Treeview.Heading",
            background=[("active", MD3["surface_highest"])],
        )

    # ------------------------------------------------------------- factories
    def _card(self, parent, title):
        """MD3 card: surface-low body, outline border, variant label text."""
        frame = tk.LabelFrame(
            parent, text=f"  {title}  ",
            bg=MD3["surface_low"], fg=MD3["on_surface_variant"],
            font=FONT_SANS_BOLD,
            bd=1, relief="solid",
            highlightthickness=0,
            padx=10, pady=8,
        )
        frame.configure(highlightbackground=MD3["outline"])
        frame.pack(fill="x", padx=10, pady=(6, 0))
        return frame

    def _primary_button(self, parent, text, command, width=12):
        return tk.Button(
            parent, text=text, command=command, width=width,
            bg=MD3["primary"], fg=MD3["on_primary"],
            activebackground=MD3["primary_hover"],
            activeforeground=MD3["on_primary"],
            disabledforeground=MD3["on_surface_variant"],
            font=FONT_SANS_BOLD, relief="flat", bd=0,
            highlightthickness=0, cursor="hand2",
        )

    def _tonal_button(self, parent, text, command, width=10, font=FONT_SANS_BOLD):
        return tk.Button(
            parent, text=text, command=command, width=width,
            bg=MD3["surface_container"], fg=MD3["on_surface"],
            activebackground=MD3["surface_high"],
            activeforeground=MD3["on_surface"],
            disabledforeground=MD3["on_surface_variant"],
            font=font, relief="solid", bd=1,
            highlightthickness=0, cursor="hand2",
        )

    # ---------------------------------------------------------------- widgets
    def create_widgets(self):
        # 0. Header / Branding Bar
        header = tk.Frame(self.root, bg=MD3["surface"], height=64,
                          highlightthickness=1,
                          highlightbackground=MD3["outline"])
        header.pack(fill="x")
        header.pack_propagate(False)

        if self.logo_img is not None:
            tk.Label(header, image=self.logo_img,
                     bg=MD3["surface"], bd=0).pack(side="left", padx=(14, 10))

        title_box = tk.Frame(header, bg=MD3["surface"])
        title_box.pack(side="left", pady=10)
        tk.Label(title_box, text="Sensor Polarity Tester",
                 font=FONT_TITLE, bg=MD3["surface"],
                 fg=MD3["on_surface"]).pack(anchor="w")
        tk.Label(title_box, text="HP/Agilent 34401A  ·  GaiaCode Ltd",
                 font=("Segoe UI", 9), bg=MD3["surface"],
                 fg=MD3["on_primary_container"]).pack(anchor="w")

        # 1. Connection Frame
        conn_frame = self._card(self.root, "DMM Connection")

        tk.Label(conn_frame, text="Port:", bg=MD3["surface_low"],
                 fg=MD3["on_surface_variant"],
                 font=FONT_SANS).grid(row=0, column=0, sticky="w")
        self.port_entry = tk.Entry(
            conn_frame, width=12,
            bg=MD3["surface_lowest"], fg=MD3["on_surface"],
            insertbackground=MD3["on_surface"],
            relief="solid", bd=1,
            highlightthickness=1,
            highlightcolor=MD3["primary"],
            highlightbackground=MD3["outline"],
            font=FONT_SANS,
        )
        self.port_entry.insert(0, "COM4")
        self.port_entry.grid(row=0, column=1, padx=5)

        self.connect_btn = self._primary_button(
            conn_frame, "Connect", self.toggle_connection, width=12)
        self.connect_btn.grid(row=0, column=2, padx=5)

        self.live_voltage_lbl = tk.Label(
            conn_frame, text="Live: --- V",
            font=FONT_MONO, bg=MD3["surface_low"],
            fg=MD3["on_primary_container"])
        self.live_voltage_lbl.grid(row=0, column=3, padx=20)

        # 2. Individual Component Buttons Frame
        indiv_frame = self._card(
            self.root, "Individual Component Tests (Push & Click to Test Single Axis)")

        self.indiv_buttons = []
        for i, (name, exp, code) in enumerate(self.directions):
            btn = self._tonal_button(
                indiv_frame,
                text=f"Test {code} ({exp})",
                command=lambda idx=i: self.start_recording(idx),
                width=10, font=("Segoe UI", 9, "bold"),
            )
            btn.config(state="disabled")
            btn.grid(row=0, column=i, padx=4, pady=2)
            self.indiv_buttons.append(btn)

        # 3. Guided / Sequential Controls Frame
        seq_frame = self._card(self.root, "Guided Sequence")

        self.prompt_label = tk.Label(
            seq_frame,
            text="Connect DMM to start testing.",
            font=("Segoe UI", 11, "bold"),
            bg=MD3["surface_low"], fg=MD3["error"],
        )
        self.prompt_label.pack(pady=3)

        btn_box = tk.Frame(seq_frame, bg=MD3["surface_low"])
        btn_box.pack(pady=3)

        self.seq_btn = self._primary_button(
            btn_box, "Record Next Step", self.start_guided_step, width=20)
        self.seq_btn.config(state="disabled")
        self.seq_btn.grid(row=0, column=0, padx=6)

        self.reset_btn = self._tonal_button(
            btn_box, "Reset Table", self.reset_test_sequence, width=14)
        self.reset_btn.grid(row=0, column=1, padx=6)

        # 4. Results Table
        table_frame = self._card(self.root, "Polarity Results Table")
        table_frame.pack_configure(fill="both", expand=True)

        columns = ("direction", "expected", "min_v", "max_v", "polarity", "status")
        self.tree = ttk.Treeview(
            table_frame, columns=columns, show="headings",
            height=8, style="Gaia.Treeview")

        self.tree.heading("direction", text="Direction")
        self.tree.heading("expected", text="Expected")
        self.tree.heading("min_v", text="Min Voltage (V)")
        self.tree.heading("max_v", text="Max Voltage (V)")
        self.tree.heading("polarity", text="Measured")
        self.tree.heading("status", text="Status")

        self.tree.column("direction", width=140, anchor="center")
        self.tree.column("expected", width=90, anchor="center")
        self.tree.column("min_v", width=130, anchor="center")
        self.tree.column("max_v", width=130, anchor="center")
        self.tree.column("polarity", width=90, anchor="center")
        self.tree.column("status", width=110, anchor="center")

        self.tree.tag_configure("PASS", foreground=MD3["success"])
        self.tree.tag_configure("FAIL", foreground=MD3["error"])
        self.tree.tag_configure("evenrow", background=MD3["surface_container"])
        self.tree.pack(fill="both", expand=True)

        # 5. Overall Banner
        self.final_status_lbl = tk.Label(
            self.root, text="STATUS: PENDING",
            font=("Segoe UI", 13, "bold"),
            bg=MD3["background"], fg=MD3["on_surface_variant"])
        self.final_status_lbl.pack(pady=8)

        self.init_table()

    def init_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for i, (direction, expected, _) in enumerate(self.directions):
            tags = ("evenrow",) if i % 2 else ()
            self.tree.insert("", "end",
                             values=(direction, expected, "-", "-", "-", "PENDING"),
                             tags=tags)

    def toggle_connection(self):
        if self.instrument is None:
            raw_port = self.port_entry.get().strip().upper()
            visa_resource = f"ASRL{raw_port[3:]}::INSTR" if raw_port.startswith("COM") and raw_port[3:].isdigit() else raw_port

            try:
                self.connect_btn.config(text="Connecting...", state="disabled")
                self.root.update()

                self.instrument = self.rm.open_resource(
                    visa_resource,
                    baud_rate=9600,
                    data_bits=7,
                    parity=pyvisa.constants.Parity.even,
                    stop_bits=pyvisa.constants.StopBits.two,
                    flow_control=pyvisa.constants.VI_ASRL_FLOW_NONE,
                    read_termination='\n',
                    write_termination='\n',
                    timeout=5000
                )
                self.instrument.write("SYST:REM")
                time.sleep(0.1)
                self.instrument.write("*RST")
                time.sleep(0.3)
                self.instrument.write("CONF:VOLT:DC")
                time.sleep(0.1)

                self.connect_btn.config(text="Disconnect", state="normal",
                                        bg=MD3["error"], fg=MD3["on_error"],
                                        activebackground=MD3["error"],
                                        activeforeground=MD3["on_error"])
                self.port_entry.config(state="disabled")
                self.set_buttons_state("normal")
                self.update_step_prompt()

            except Exception as e:
                self._reset_connect_button()
                messagebox.showerror("Connection Error", f"Failed to connect:\n{str(e)}")
                self.instrument = None
        else:
            try:
                self.instrument.write("SYST:LOC")
                self.instrument.close()
            except Exception:
                pass
            finally:
                self.instrument = None
                self._reset_connect_button()
                self.port_entry.config(state="normal")
                self.set_buttons_state("disabled")
                self.prompt_label.config(text="Connect DMM to start testing.",
                                         fg=MD3["error"])
                self.live_voltage_lbl.config(text="Live: --- V")

    def _reset_connect_button(self):
        self.connect_btn.config(text="Connect", state="normal",
                                bg=MD3["primary"], fg=MD3["on_primary"],
                                activebackground=MD3["primary_hover"],
                                activeforeground=MD3["on_primary"])

    def set_buttons_state(self, state):
        self.seq_btn.config(state=state)
        for btn in self.indiv_buttons:
            btn.config(state=state)

    def update_step_prompt(self):
        if self.current_step_idx < len(self.directions):
            direction, expected, _ = self.directions[self.current_step_idx]
            self.prompt_label.config(
                text=f"Guided Step {self.current_step_idx + 1}/6: Push [{direction}] and record",
                fg=MD3["on_primary_container"]
            )
            self.seq_btn.config(state="normal", text=f"Record {direction}")
        else:
            self.seq_btn.config(state="disabled", text="Sequence Finished")
            self.prompt_label.config(
                text="Guided sequence complete. You can still test individual axes above.",
                fg=MD3["success"])

    def start_guided_step(self):
        if self.current_step_idx < len(self.directions):
            self.start_recording(self.current_step_idx, is_guided=True)

    def start_recording(self, target_idx, is_guided=False):
        if self.is_sampling or self.instrument is None:
            return

        self.is_sampling = True
        self.active_test_idx = target_idx
        self.set_buttons_state("disabled")

        dir_name = self.directions[target_idx][0]
        self.prompt_label.config(text=f"Sampling [{dir_name}] for 1.5s...",
                                 fg=MD3["warning"])

        threading.Thread(target=lambda: self._sample_worker(is_guided), daemon=True).start()

    def _sample_worker(self, is_guided):
        samples = []
        start_time = time.time()

        while time.time() - start_time < 1.5:
            try:
                val = float(self.instrument.query("READ?"))
                samples.append(val)
                self.root.after(0, self.live_voltage_lbl.config, {"text": f"Live: {val:+.4f} V"})
            except Exception:
                pass
            time.sleep(0.05)

        self.root.after(0, self._process_results, samples, is_guided)

    def _process_results(self, samples, is_guided):
        self.is_sampling = False
        self.set_buttons_state("normal")

        if not samples:
            messagebox.showerror("Read Error", "No voltage readings collected.")
            return

        min_v = min(samples)
        max_v = max(samples)

        peak = max_v if abs(max_v) >= abs(min_v) else min_v
        measured_pol = "+" if peak > 0.005 else ("-" if peak < -0.005 else "0")

        direction, expected, _ = self.directions[self.active_test_idx]
        status = "PASS" if measured_pol == expected else "FAIL"

        item_id = self.tree.get_children()[self.active_test_idx]
        row_tags = [status]
        if self.active_test_idx % 2:
            row_tags.append("evenrow")
        self.tree.item(
            item_id,
            values=(direction, expected, f"{min_v:+.4f}", f"{max_v:+.4f}", measured_pol, status),
            tags=tuple(row_tags)
        )

        if is_guided:
            self.current_step_idx += 1

        self.update_step_prompt()
        self.evaluate_overall_status()

    def evaluate_overall_status(self):
        statuses = [self.tree.item(item)["values"][5] for item in self.tree.get_children()]

        if any(s == "FAIL" for s in statuses):
            self.final_status_lbl.config(text="OVERALL: FAIL", fg=MD3["error"])
        elif all(s == "PASS" for s in statuses):
            self.final_status_lbl.config(text="OVERALL: PASS", fg=MD3["success"])
        else:
            self.final_status_lbl.config(text="STATUS: IN PROGRESS", fg=MD3["warning"])

    def reset_test_sequence(self):
        self.current_step_idx = 0
        self.init_table()
        self.final_status_lbl.config(text="STATUS: PENDING",
                                     fg=MD3["on_surface_variant"])
        if self.instrument:
            self.update_step_prompt()
            self.set_buttons_state("normal")
        else:
            self.prompt_label.config(text="Connect DMM to start testing.",
                                     fg=MD3["error"])


if __name__ == "__main__":
    root = tk.Tk()
    app = SensorPolarityTester(root)
    root.mainloop()
