import cv2
import serial
import time
from ultralytics import YOLO  # Import YOLO from ultralytics
from pathlib import Path

# Set up serial communication with Arduino
ser = serial.Serial('COM10', 9600)  # Change to your Arduino's serial port

# Define thresholds and durations
LOW_DENSITY_THRESHOLD = 5
MEDIUM_DENSITY_THRESHOLD = 15
DURATIONS = {
    "LOW": {"green": 5, "yellow": 2, "red": 5},
    "MEDIUM": {"green": 10, "yellow": 2, "red": 5},
    "HIGH": {"green": 15, "yellow": 3, "red": 5}
}

# Load YOLO model
model = YOLO("yolov8n.pt")  # Use YOLOv8n model (nano) for vehicle detection

def get_vehicle_count(image_path):
    # Load the image
    image = cv2.imread(str(image_path))

    # Run YOLO model on the image
    results = model(image)

    # Count detected vehicles
    vehicle_count = 0
    for result in results:
        # You can use the `result.names` to check for specific classes if needed
        for class_id in result.boxes.cls:
            if class_id in [2, 3, 5, 7]:  # Classes for car, motorcycle, bus, and truck
                vehicle_count += 1

    return vehicle_count

def determine_duration(vehicle_count):
    if vehicle_count <= LOW_DENSITY_THRESHOLD:
        return DURATIONS["LOW"]
    elif vehicle_count <= MEDIUM_DENSITY_THRESHOLD:
        return DURATIONS["MEDIUM"]
    else:
        return DURATIONS["HIGH"]

def control_traffic_lights(duration):
    # Send duration data to Arduino
    ser.write(f"GREEN:{duration['green']} YELLOW:{duration['yellow']} RED:{duration['red']}\n".encode())
    time.sleep(1)  # Allow Arduino time to process the command

def process_traffic(images_folder):
    # Get a list of image files from the specified folder
    image_paths = list(Path(images_folder).glob("*.jpg"))  # Use *.jpg or other formats if needed

    for image_path in image_paths:
        # Detect vehicle count
        vehicle_count = get_vehicle_count(image_path)

        # Determine signal duration based on vehicle count
        duration = determine_duration(vehicle_count)

        # Control traffic lights
        control_traffic_lights(duration)

        # Display the processed image with detection (for verification)
        image = cv2.imread(str(image_path))
        results = model(image)
        annotated_image = results[0].plot()  # Plot detection boxes onto image

        cv2.imshow("Traffic Image", annotated_image)
        if cv2.waitKey(0) & 0xFF == ord('q'):  # Press 'q' to move to the next image
            continue

    cv2.destroyAllWindows()

# Specify the folder containing traffic images
images_folder = "images/car2.jpg"  # Replace with your folder path
process_traffic(images_folder)
