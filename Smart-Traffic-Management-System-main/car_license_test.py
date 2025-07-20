import cv2
from ultralytics import YOLO
import pytesseract

# Configure pytesseract path (if not added to the PATH environment variable)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Update with your Tesseract path

# Load YOLO model
model = YOLO("license.pt")  # Replace 'license.pt' with the path to your YOLO model

def detect_license_plate(image_path):
    # Read the input image
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Unable to load image {image_path}")
        return

    # Perform inference
    results = model(img)

    license_plate_number = None  # To store the extracted text

    # Process the results
    for result in results:
        for box in result.boxes.xyxy:  # Bounding box coordinates (x_min, y_min, x_max, y_max)
            x_min, y_min, x_max, y_max = map(int, box)

            # Crop the detected license plate area
            cropped_plate = img[y_min:y_max, x_min:x_max]

            # Use pytesseract to extract text from the cropped image
            license_plate_number = pytesseract.image_to_string(cropped_plate, config='--psm 8')  # PSM 8 is for single line text

            # Draw bounding boxes and label
            cv2.rectangle(img, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
            cv2.putText(
                img,
                license_plate_number.strip(),
                (x_min, y_min - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 255),
                2,
            )

            print(f"Detected License Plate: {license_plate_number.strip()}")  # Print the detected license plate number

    # Display the output
    cv2.imshow("Detected License Plate", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    image_path = "car1 (2).jpg"  # Replace with your test image path
    detect_license_plate(image_path)
