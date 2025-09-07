import machine
import time
import struct

class FlightController:
    """
    A class to handle MSP communication with a Flight Controller.
    """
    # --- MSP Command Codes ---
    MSP_STATUS_EX = 150
    MSP_ANALOG = 110
    MSP_MOTOR = 104
    MSP_SET_RAW_RC = 200
    MSP_ACC_CALIBRATION = 205
    MSP_SET_SETTING = 218
    MSP_ARM = 151
    MSP_DISARM = 152
    MSP_SET_4WAY_IF = 245  # Assuming 200 is the correct command for setting RC channels

    def __init__(self, uart_id=1, tx_pin=18, rx_pin=17, baudrate=115200):
        """Initializes the UART connection."""
        self.uart = None
        print(f"Initializing UART{uart_id} on TX={tx_pin}, RX={rx_pin}...")
        try:
            self.uart = machine.UART(uart_id, baudrate=baudrate, tx=tx_pin, rx=rx_pin, timeout=100)
            print("UART connection successful.")
        except Exception as e:
            print(f"FATAL: Failed to initialize UART: {e}")
            raise

    def _send_msp_request(self, command, payload=b''):
        """Constructs and sends an MSP frame."""
        # Frame structure: $M<, size, command, payload, checksum
        size = len(payload)
        frame = [ord('$'), ord('M'), ord('<'), size, command] + list(payload)
        
        checksum = 0
        for byte in frame[3:]: # Checksum is calculated over size, command, and payload
            checksum ^= byte
        frame.append(checksum)
        
        self.uart.write(bytes(frame))

    def _read_msp_response(self):
        """
        Robust MSP response reader with proper timeout handling.
        """
        # Wait for data to arrive
        timeout_ms = 500
        start_time = time.ticks_ms()
        
        # Wait for at least the header to arrive
        while self.uart.any() < 3 and time.ticks_diff(time.ticks_ms(), start_time) < timeout_ms:
            time.sleep_ms(10)
        
        if self.uart.any() < 3:
            return None, None
        
        # Read header
        header = self.uart.read(3)
        if header != b'$M>':
            # Clear buffer and return
            while self.uart.any():
                self.uart.read(1)
            return None, None
        
        # Wait for size and command bytes
        while self.uart.any() < 2 and time.ticks_diff(time.ticks_ms(), start_time) < timeout_ms:
            time.sleep_ms(10)
        
        if self.uart.any() < 2:
            return None, None
        
        size = self.uart.read(1)[0]
        command = self.uart.read(1)[0]
        
        # Wait for payload + checksum
        total_needed = size + 1  # payload + checksum
        while self.uart.any() < total_needed and time.ticks_diff(time.ticks_ms(), start_time) < timeout_ms:
            time.sleep_ms(10)
        
        if self.uart.any() < total_needed:
            return None, None
        
        # Read payload and checksum
        payload = self.uart.read(size)
        checksum = self.uart.read(1)[0]
        
        # Verify checksum
        calculated = size ^ command
        for byte in payload:
            calculated ^= byte
        
        if calculated != checksum:
            return None, None
        
        return command, payload

    def get_status(self):
        """Requests and parses flight controller status."""
        self._send_msp_request(self.MSP_STATUS_EX)
        command, data = self._read_msp_response()

        if command != self.MSP_STATUS_EX or not data:
            return None

        try:
            # Parse the most common fields from MSP_STATUS_EX
            format_string = '<HHIIBH'
            if len(data) < struct.calcsize(format_string):
                print(f"ERROR: MSP_STATUS_EX data too short. Got {len(data)} bytes.")
                return None

            cycle_time, i2c_errors, sensors, flags, profile, cpuload = struct.unpack(format_string, data[:struct.calcsize(format_string)])
            
            # Get arming disable flags if available
            arming_disable_flags = 0
            if len(data) >= struct.calcsize(format_string) + 4:
                arming_disable_flags = struct.unpack('<I', data[struct.calcsize(format_string):struct.calcsize(format_string)+4])[0]
            
            is_armed = bool(flags & 1)
            
            # Decode arming disable flags
            disable_reasons = []
            if arming_disable_flags & (1 << 0): disable_reasons.append("NO_GYRO")
            if arming_disable_flags & (1 << 1): disable_reasons.append("FAILSAFE")
            if arming_disable_flags & (1 << 2): disable_reasons.append("RX_FAILSAFE")
            if arming_disable_flags & (1 << 3): disable_reasons.append("BAD_RX_RECOVERY")
            if arming_disable_flags & (1 << 4): disable_reasons.append("BOXFAILSAFE")
            if arming_disable_flags & (1 << 5): disable_reasons.append("RUNAWAY_TAKEOFF")
            if arming_disable_flags & (1 << 6): disable_reasons.append("CRASH_DETECTED")
            if arming_disable_flags & (1 << 7): disable_reasons.append("THROTTLE")
            if arming_disable_flags & (1 << 8): disable_reasons.append("ANGLE")
            if arming_disable_flags & (1 << 9): disable_reasons.append("BOOT_GRACE_TIME")
            if arming_disable_flags & (1 << 10): disable_reasons.append("NOPREARM")
            if arming_disable_flags & (1 << 11): disable_reasons.append("LOAD")
            if arming_disable_flags & (1 << 12): disable_reasons.append("CALIBRATING")
            if arming_disable_flags & (1 << 13): disable_reasons.append("CLI")
            if arming_disable_flags & (1 << 14): disable_reasons.append("CMS_MENU")
            if arming_disable_flags & (1 << 15): disable_reasons.append("OSD_MENU")
            if arming_disable_flags & (1 << 16): disable_reasons.append("BST")
            if arming_disable_flags & (1 << 17): disable_reasons.append("MSP")
            if arming_disable_flags & (1 << 18): disable_reasons.append("PARALYZE")
            if arming_disable_flags & (1 << 19): disable_reasons.append("GPS")
            if arming_disable_flags & (1 << 20): disable_reasons.append("RESC")
            if arming_disable_flags & (1 << 21): disable_reasons.append("RPMFILTER")
            if arming_disable_flags & (1 << 22): disable_reasons.append("REBOOT_REQD")
            if arming_disable_flags & (1 << 23): disable_reasons.append("DSHOT_BBANG")
            if arming_disable_flags & (1 << 24): disable_reasons.append("NO_ACC_CAL")
            if arming_disable_flags & (1 << 25): disable_reasons.append("MOTOR_PROTO")
            if arming_disable_flags & (1 << 26): disable_reasons.append("ARM_SWITCH")
            
            return {
                "cycle_time_us": cycle_time,
                "cpu_load_percent": cpuload,
                "i2c_errors": i2c_errors,
                "is_armed": is_armed,
                "arming_disable_flags": arming_disable_flags,
                "disable_reasons": disable_reasons
            }
        except Exception as e:
            print(f"ERROR: Failed to parse MSP_STATUS_EX: {e}")
            return None

    def get_analog(self):
        """Requests and parses battery and signal strength data."""
        self._send_msp_request(self.MSP_ANALOG)
        command, data = self._read_msp_response()

        if command != self.MSP_ANALOG or not data:
            return None
            
        try:
            # Format: vbat (uint8), intPowerMeterSum (uint16), rssi (uint16), amperage (uint16)
            vbat_raw, _, rssi, amperage = struct.unpack('<BHHH', data[:7])
            voltage = vbat_raw / 10.0  # vbat is typically scaled by 10
            
            return {
                "voltage": voltage,
                "rssi": rssi,
                "amperage": amperage
            }
        except Exception as e:
            print(f"ERROR: Failed to parse MSP_ANALOG: {e}")
            return None

    def get_motors(self):
        """Requests and parses motor output values."""
        self._send_msp_request(self.MSP_MOTOR)
        command, data = self._read_msp_response()

        if command != self.MSP_MOTOR or not data:
            return None

        try:
            # Each motor value is a uint16. The number of motors depends on the payload length.
            num_motors = len(data) // 2
            motor_values = struct.unpack(f'<{num_motors}H', data)
            
            return {"motors": motor_values}
        except Exception as e:
            print(f"ERROR: Failed to parse MSP_MOTOR: {e}")
            return None

    def set_rc_channels(self, channels):
        """
        Sends RC channel data and reads the echo response to clear the buffer.
        """
        if len(channels) > 18:
            print("WARN: Too many channels. MSP supports up to 18.")
            channels = channels[:18]
        
        format_string = f'<{len(channels)}H'
        payload = struct.pack(format_string, *channels)
        
        self._send_msp_request(self.MSP_SET_RAW_RC, payload)
        
        # Read the echo response from the FC to prevent buffer issues.
        # The FC will echo the command we just sent.
        self._read_msp_response()

    def calibrate_accelerometer(self):
        """Sends accelerometer calibration command."""
        print("Starting accelerometer calibration...")
        self._send_msp_request(self.MSP_ACC_CALIBRATION)
        
        # Clear any echo response
        self._read_msp_response()
        
        # Wait for calibration to complete and FC to stabilize
        print("Waiting for calibration to complete...")
        time.sleep(3)
        
        # Clear UART buffer completely
        while self.uart.any():
            self.uart.read(1)
            time.sleep_ms(10)
        
        print("Accelerometer calibration complete.")

    def configure_for_esp32(self):
        """Configure FC settings for ESP32 control."""
        print("Configuring FC for ESP32 control...")
        
        # Note: MSP_SET_SETTING is complex and firmware-specific
        # For now, we'll just print what needs to be done manually
        print("Please manually set these in Betaflight CLI:")
        print("set paralyze = OFF")
        print("set small_angle = 180") 
        print("set acc_calibration = 0")
        print("save")
        print("Then restart the FC.")

    def wait_for_boot_complete(self):
        """Wait for FC to complete boot sequence."""
        print("Waiting for FC boot to complete...")
        boot_complete = False
        timeout = 30  # 30 second timeout
        
        for i in range(timeout):
            status = self.get_status()
            if status and status['disable_reasons']:
                if 'BOOT_GRACE_TIME' not in status['disable_reasons']:
                    boot_complete = True
                    break
            time.sleep(1)
            if i % 5 == 0:
                print(f"Still waiting for boot... ({i}s)")
        
        if boot_complete:
            print("FC boot complete!")
        else:
            print("Warning: FC boot timeout - continuing anyway")
        
        return boot_complete

    def force_arm(self):
        """Force arm the FC using MSP command."""
        print("Attempting to force arm FC...")
        self._send_msp_request(self.MSP_ARM)
        self._read_msp_response()
        time.sleep_ms(500)

    def force_disarm(self):
        """Force disarm the FC using MSP command."""
        print("Attempting to force disarm FC...")
        self._send_msp_request(self.MSP_DISARM)
        self._read_msp_response()
        time.sleep_ms(500)

    def bypass_safety_checks(self):
        """Try to bypass safety checks by directly manipulating motor outputs."""
        print("Attempting to bypass safety checks...")
        
        # Try to set motors directly (this bypasses most safety checks)
        print("Testing direct motor control...")
        
        # Start with motors off
        print("1. Setting all motors to OFF (1000)...")
        stop_motor_values = [1000, 1000, 1000, 1000, 0, 0, 0, 0]
        payload = struct.pack('<8H', *stop_motor_values)
        MSP_SET_MOTOR = 214
        self._send_msp_request(MSP_SET_MOTOR, payload)
        self._read_msp_response()
        time.sleep(1)
        
        # Check motor status
        motor_status = self.get_motors()
        if motor_status:
            print(f"   Current motor values: {motor_status['motors']}")
        
        # Test each motor individually with low speed
        for i in range(4):
            print(f"2. Testing motor {i+1} at low speed...")
            test_values = [1000, 1000, 1000, 1000, 0, 0, 0, 0]
            test_values[i] = 1030  # Slightly higher for this motor
            
            payload = struct.pack('<8H', *test_values)
            self._send_msp_request(MSP_SET_MOTOR, payload)
            self._read_msp_response()
            time.sleep(1)
            
            # Check if FC reports the new motor value
            motor_status = self.get_motors()
            if motor_status:
                print(f"   Motor values: {motor_status['motors']}")
                if motor_status['motors'][i] > 1000:
                    print(f"   ✓ Motor {i+1} command accepted by FC!")
                else:
                    print(f"   ✗ Motor {i+1} command rejected by FC")
            
            # Stop this motor
            test_values[i] = 1000
            payload = struct.pack('<8H', *test_values)
            self._send_msp_request(MSP_SET_MOTOR, payload)
            self._read_msp_response()
        
        print("3. All motors stopped.")
        print("\nDid you hear/see any motor movement? (Check physically)")
        print("If motors moved, the control chain is working!")
        print("If no movement, check ESC connections and power.")
