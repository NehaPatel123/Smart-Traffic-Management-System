import serial
import time

# Set the COM port and baud rate (adjust the COM port as needed)
arduino = serial.Serial(port='com10', baudrate=9600, timeout=1)

def control_led(color):
    if color in ['R', 'Y', 'G']:
        arduino.write(color.encode())  # Send the command to Arduino
        time.sleep(2.5)  # Wait for 2 seconds (LED on time + small buffer)
    else:
        print("Invalid color. Use 'R', 'Y', or 'G'.")

if __name__ == "__main__":
    try:
        while True:
            # Cycle through LEDs
            control_led('R')  # Red LED
            control_led('Y')  # Yellow LED
            control_led('G')  # Green LED
    except KeyboardInterrupt:
        print("Exiting program.")
    finally:
        arduino.close()
