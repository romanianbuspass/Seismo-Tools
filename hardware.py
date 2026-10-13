import serial
import time
import re

# DEFAULT CONFIGURATION
CONFIG = {
    'SIG_GEN': {'port': 'COM5', 'baud': 9600},
    'DMM':     {'port': 'COM4', 'baud': 9600},
    'AUX':     {'port': 'COM6', 'baud': 9600}
}

class InstrumentController:
    def __init__(self):
        self.sig = None
        self.dmm = None

    def connect(self, config_override=None):
        """Open connections with optional dynamic config."""
        self.close()
        
        if config_override:
            for key in ['SIG_GEN', 'DMM']:
                if key in config_override:
                    CONFIG[key].update(config_override[key])

        try:
            # --- 1. CONNECT SIG GEN ---
            print(f"Connecting to Sig Gen on {CONFIG['SIG_GEN']['port']}...")
            self.sig = serial.Serial(
                CONFIG['SIG_GEN']['port'], 
                int(CONFIG['SIG_GEN']['baud']), 
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1
            )
            
            # --- 2. CONNECT DMM ---
            print(f"Connecting to DMM on {CONFIG['DMM']['port']}...")
            self.dmm = serial.Serial(
                CONFIG['DMM']['port'], 
                int(CONFIG['DMM']['baud']), 
                bytesize=serial.SEVENBITS,   
                parity=serial.PARITY_EVEN,   
                stopbits=serial.STOPBITS_ONE, 
                xonxoff=False,
                timeout=1.5 # Adjusted timeout
            )
            
            # --- INIT INSTRUMENTS ---
            self.sig.write(b"*RST\n")
            time.sleep(0.1)
            self.sig.write(b"OUTP:LOAD INF\n")

            self.dmm.write(b"SYST:REM\n") 
            time.sleep(0.1)
            self.dmm.write(b"*RST\n") 
            time.sleep(0.15)
            self.dmm.write(b"*CLS\n") 
            time.sleep(0.15)
            
            return True, "Connected"
        except Exception as e:
            self.close()
            return False, f"Connection Error: {str(e)}"

    def close(self):
        try:
            if self.dmm and self.dmm.is_open:
                self.dmm.write(b"SYST:LOC\n")
                self.dmm.close()
            if self.sig and self.sig.is_open: 
                self.sig.close()
        except: pass
        self.sig = None
        self.dmm = None

    def set_voltage(self, volts):
        if not self.sig: return False
        try:
            cmd = f"APPLY:DC DEF, DEF, {volts}\n"
            self.sig.write(cmd.encode())
            return True
        except: return False

    def read_voltage(self):
        """Robust DMM reading using MEAS:VOLT:DC? and Regex cleaning."""
        if not self.dmm: return None
        try:
            self.dmm.reset_input_buffer()
            self.dmm.write(b"MEAS:VOLT:DC?\n")
            
            raw_response = self.dmm.readline()
            decoded_response = raw_response.decode('utf-8', errors='ignore').strip()
            
            if not decoded_response:
                return None
                
            try:
                return float(decoded_response)
            except ValueError:
                clean_str = re.sub(r'[^\d\.\-\+eE]', '', decoded_response)
                if clean_str:
                    return float(clean_str)
                return None
                    
        except Exception:
            return None

    # --- NEW FUNCTION FOR SERIAL PORT TEST ---
    def send_serial_test(self, port, baud):
        """Opens the specified COM port, sends a test string, and closes it."""
        try:
            # We use 'with' so it automatically closes the port when done
            with serial.Serial(port, int(baud), timeout=1) as ser:
                ser.write(b"GaiaCode Serial Port Test\r\n")
            return True, f"Sent test string successfully to {port}"
        except Exception as e:
            return False, f"Failed to send on {port}: {str(e)}"

# --- INITIALIZE MANAGER SO TRAVELLER_SERVER.PY CAN IMPORT IT ---
manager = InstrumentController()
