import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
from ultralytics import YOLO
import serial
import time


try:
    arduino = serial.Serial(port='COM10', baudrate=9600, timeout=1)
    time.sleep(2)
except serial.SerialException as e:
    messagebox.showerror("Serial Connection Error", f"Could not open serial port: {e}")
    arduino = None


model = YOLO("best.pt")


vehicle_classes = ['Car', 'Fire Brigade', 'Police', 'Bike']
ambulance_class = 'Ambulance'


LOW_DENSITY_THRESHOLD = 20
MEDIUM_DENSITY_THRESHOLD = 31
DURATIONS = {
    "LOW": {"green": 10, "yellow": 1, "red": 5},
    "MEDIUM": {"green": 15, "yellow": 1, "red": 5},
    "HIGH": {"green": 20, "yellow": 1, "red": 5}
}


uploaded_image_path = None

def determine_duration(vehicle_count):
    if vehicle_count <= LOW_DENSITY_THRESHOLD:
        return DURATIONS["LOW"]
    elif vehicle_count <= MEDIUM_DENSITY_THRESHOLD:
        return DURATIONS["MEDIUM"]
    else:
        return DURATIONS["HIGH"]

def control_traffic_lights(duration):
    if arduino:
        arduino.write(f"GREEN:{duration['green']} YELLOW:{duration['yellow']} RED:{duration['red']}\n".encode())
        time.sleep(1)

def send_buzzer_signal():

    if arduino:
        arduino.write("BUZZER:ON\n".encode())
        time.sleep(1)
        arduino.write("BUZZER:OFF\n".encode())

def process_and_display_image():

    global uploaded_image_path
    if not uploaded_image_path:
        messagebox.showwarning("No Image", "Please upload an image first.")
        return

    frame = cv2.imread(uploaded_image_path)
    if frame is None:
        messagebox.showerror("Image Error", f"Could not read the image at {uploaded_image_path}.")
        return

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
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Green for vehicles
            label = f"{class_name}: {conf:.2f}"
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        elif class_name == ambulance_class:
            ambulance_detected = True
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)  # Red for ambulance
            label = f"Ambulance: {conf:.2f}"
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    if ambulance_detected:
        send_buzzer_signal()

    duration = determine_duration(vehicle_count)
    control_traffic_lights(duration)

    messagebox.showinfo("Processing Complete", f"Vehicle Count: {vehicle_count}")


    cv2.imshow("Processed Image", frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def upload_image():

    global uploaded_image_path
    uploaded_image_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png")])
    if uploaded_image_path:
        messagebox.showinfo("Image Uploaded", f"Image uploaded successfully: {uploaded_image_path}")


app = tk.Tk()
app.title("Smart Traffic Management System")
app.geometry("600x400")

title_label = tk.Label(app, text="Smart Traffic Management System", font=("Arial", 16))
title_label.pack(pady=10)

upload_button = tk.Button(app, text="Upload Image", command=upload_image, font=("Arial", 14), bg="blue", fg="white")
upload_button.pack(pady=10)

submit_button = tk.Button(app, text="Submit", command=process_and_display_image, font=("Arial", 14), bg="green", fg="white")
submit_button.pack(pady=10)

app.mainloop()
