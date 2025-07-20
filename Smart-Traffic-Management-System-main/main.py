import cv2
from ultralytics import YOLO
import serial
import time

# Set up serial communication (update COM port and baud rate as per your setup)
arduino = serial.Serial(port='COM5', baudrate=9600, timeout=1)
time.sleep(2)  # Wait for the connection to establish

# Load the YOLOv8 pre-trained model
model = YOLO("best.pt")

# COCO classes related to vehicles and ambulance
vehicle_classes = ['Car','Fire Brigade','Police','Bike']
ambulance_class = 'Ambulance'

# Define thresholds and durations
LOW_DENSITY_THRESHOLD = 20
MEDIUM_DENSITY_THRESHOLD = 31
DURATIONS = {
    "LOW": {"green": 10, "yellow": 1, "red": 5},
    "MEDIUM": {"green": 15, "yellow": 1, "red": 5},
    "HIGH": {"green": 20, "yellow": 1, "red": 5}
}

def determine_duration(vehicle_count):
    """Determine traffic light durations based on vehicle count."""
    if vehicle_count <= LOW_DENSITY_THRESHOLD:
        return DURATIONS["LOW"]
    elif vehicle_count <= MEDIUM_DENSITY_THRESHOLD:
        return DURATIONS["MEDIUM"]
    else:
        return DURATIONS["HIGH"]

def control_traffic_lights(duration):
    """Send duration data to Arduino."""
    arduino.write(f"GREEN:{duration['green']} YELLOW:{duration['yellow']} RED:{duration['red']}\n".encode())
    time.sleep(1)  # Allow Arduino time to process the command

def send_buzzer_signal():
    """Send buzzer signal to Arduino when an ambulance is detected."""
    arduino.write("BUZZER:ON\n".encode())
    time.sleep(1)
    arduino.write("BUZZER:OFF\n".encode())

def process_image(image_path):
    frame = cv2.imread(image_path)
    if frame is None:
        print(f"Error: Could not read the image at {image_path}.")
        return 0  # Return 0 if the image couldn't be read

    # Resize the image for better visibility
    frame = cv2.resize(frame, (1020, 500))

    # Run YOLOv8 inference on the image
    results = model.predict(source=frame, conf=0.25)  # Set a confidence threshold

    # Keep track of vehicle count
    vehicle_count = 0
    ambulance_detected = False

    # Draw bounding boxes for detected vehicles
    for box in results[0].boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])  # Bounding box coordinates
        class_id = int(box.cls[0])  # Class ID
        conf = float(box.conf[0])  # Confidence score

        # Check if the detected object is a vehicle or an ambulance
        class_name = model.names[class_id]
        if class_name in vehicle_classes:
            vehicle_count += 1  # Increment vehicle count

            # Draw the bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Add label and confidence score
            label = f"{class_name}: {conf:.2f}"
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        elif class_name == ambulance_class:
            ambulance_detected = True
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)  # Red for ambulance
            label = f"Ambulance: {conf:.2f}"
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    # Trigger buzzer if an ambulance is detected
    if ambulance_detected:
        print("Ambulance detected! Triggering buzzer.")
        send_buzzer_signal()

    # Display vehicle count
    count_label = f"Vehicle Count: {vehicle_count}"
    cv2.putText(frame, count_label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    print(count_label)

    # Determine duration based on vehicle count
    duration = determine_duration(vehicle_count)
    control_traffic_lights(duration)  # Send duration data to Arduino

    # Display the image
    cv2.imshow("Vehicle Detection and Count", frame)

    # Set delay based on traffic signal
    delay_time = duration["green"] * 1000  # Wait for the green light duration in milliseconds
    cv2.waitKey(delay_time)  # Wait for the duration of the green light
    cv2.destroyAllWindows()

    return vehicle_count  # Return vehicle count for debugging/logging if needed


# Main program
if __name__ == "__main__":
    image_path = "images/download - Copy.jpg"  # Update this path to your image location
    process_image(image_path)
