from flask import Flask, render_template, request, redirect, url_for
import cv2
from ultralytics import YOLO
import serial
import time
import os

# Set up Flask
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Set up serial communication (update COM port and baud rate as per your setup)
arduino = serial.Serial(port='COM5', baudrate=9600, timeout=1)
time.sleep(2)  # Wait for the connection to establish

# Load the YOLOv8 pre-trained model
model = YOLO("best.pt")

# COCO classes related to vehicles and ambulance
vehicle_classes = ['Car', 'Fire Brigade', 'Police', 'Bike']
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
    if vehicle_count <= LOW_DENSITY_THRESHOLD:
        return DURATIONS["LOW"]
    elif vehicle_count <= MEDIUM_DENSITY_THRESHOLD:
        return DURATIONS["MEDIUM"]
    else:
        return DURATIONS["HIGH"]

def control_traffic_lights(duration):
    arduino.write(f"GREEN:{duration['green']} YELLOW:{duration['yellow']} RED:{duration['red']}\n".encode())
    time.sleep(1)

def send_buzzer_signal():
    arduino.write("BUZZER:ON\n".encode())
    time.sleep(1)
    arduino.write("BUZZER:OFF\n".encode())

def process_image(image_path):
    frame = cv2.imread(image_path)
    if frame is None:
        return "Error: Could not read the image."

    frame = cv2.resize(frame, (1020, 500))
    results = model.predict(source=frame, conf=0.25)

    vehicle_count = 0
    ambulance_detected = False

    for box in results[0].boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        class_id = int(box.cls[0])
        conf = float(box.conf[0])

        class_name = model.names[class_id]
        if class_name in vehicle_classes:
            vehicle_count += 1
        elif class_name == ambulance_class:
            ambulance_detected = True

    if ambulance_detected:
        send_buzzer_signal()

    duration = determine_duration(vehicle_count)
    control_traffic_lights(duration)

    return f"Vehicle Count: {vehicle_count}"

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            result = process_image(file_path)
            return render_template('index.html', result=result, uploaded_file=file.filename)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
