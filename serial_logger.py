import serial
import time
import datetime
from colorama import init, Fore, Style

# === Initialize colorama ===
init(autoreset=True)

# === Configuration ===
SERIAL_PORT = 'COM4'
BAUD_RATE = 115200
SERIAL_TIMEOUT_S = 10
LOG_FILE_NAME = 'serial_log.txt'  # Set to None if you don't want to save

# === Open serial port ===
try:
    serial_port = serial.Serial(
        SERIAL_PORT, 
        BAUD_RATE, 
        timeout=SERIAL_TIMEOUT_S,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE
    )
    serial_port.reset_input_buffer()
    print(f"{Fore.CYAN}Listening on {SERIAL_PORT} at {BAUD_RATE} baud...\n")
except serial.SerialException as e:
    print(f"{Fore.RED}Error opening serial port: {e}")
    exit(1)

# === Open log file if needed ===
log_file = None
if LOG_FILE_NAME:
    log_file = open(LOG_FILE_NAME, 'w', buffering=1)

# === Buffer to hold incomplete line ===
line_buffer = ""

# === Start reading loop ===
try:
    while True:
        if serial_port.in_waiting > 0:
            data = serial_port.read(serial_port.in_waiting)
            text = data.decode(errors='ignore')

            for char in text:
                if char in ['\n', '\r']:  # End of line detected
                    if line_buffer.strip():
                        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        line_clean = line_buffer.strip()

                        # Choose color based on content
                        if any(word in line_clean.lower() for word in ["error", "fail", "critical"]):
                            color = Fore.RED
                        elif any(word in line_clean.lower() for word in ["warning", "warn"]):
                            color = Fore.YELLOW
                        elif any(word in line_clean.lower() for word in ["ok", "ready", "success", "Update"]):
                            color = Fore.GREEN
                        else:
                            color = Fore.GREEN

                        pretty_line = f"[{timestamp}] {line_clean}"

                        print(color + pretty_line)

                        if log_file:
                            log_file.write(pretty_line + '\n')

                    line_buffer = ""  # Clear buffer for next line
                else:
                    line_buffer += char  # Keep adding chars to the current line

        time.sleep(0.005)

except KeyboardInterrupt:
    print(f"{Fore.MAGENTA}\nExiting...")

finally:
    if log_file:
        log_file.close()
    serial_port.close()
