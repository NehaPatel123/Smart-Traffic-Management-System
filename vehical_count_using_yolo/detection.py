
from ultralytics import YOLO
import cv2

# Load the trained YOLO model
model = YOLO('best.pt')  # Path to your trained weights file

# Path to the new image for testing
image_path = 'WhatsApp Image 2024-12-03 at 1.49.15 PM.jpeg'  # Replace with the actual path to your image

# Perform inference
results = model(image_path)

# Extract detected objects
detected_objects = results[0].boxes.data  # Contains bounding boxes and class information

# Filter for vehicle classes (update these based on your model's class names)
vehicle_classes = ['Ambulance','Car','Fire Brigade','Police','Bike']  # Modify as per your training dataset
vehicle_count = 0

for box in results[0].boxes:
    cls_id = int(box.cls[0])  # Get class index
    class_name = model.names[cls_id]  # Get class name
    print(class_name)
    if class_name in vehicle_classes:
        vehicle_count += 1

# Get the result image
result_image = results[0].plot()

# Add vehicle count text to the image
text = f"Vehicle Count: {vehicle_count}"
font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 1
color = (0, 255, 0)  # Green
thickness = 2
text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
text_x = 10
text_y = 30
cv2.putText(result_image, text, (text_x, text_y), font, font_scale, color, thickness)
print(vehicle_count)

# Display the image with the vehicle count
cv2.imshow("Detection Result", result_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
