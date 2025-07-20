from ultralytics import YOLO
import cv2
import time

# Load the trained YOLO model
model = YOLO('best.pt')  # Path to your trained weights file

# Path to the video file
video_path = 'videoplayback.mp4'  # Replace with the path to your video file
 # Path to save the output video

# Open the video file
cap = cv2.VideoCapture(video_path)

# Check if the video opened successfully
if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

# Get video properties
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))

# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'XVID')


# Process the video frame by frame
frame_count = 0
start_time = time.time()

while True:
    ret, frame = cap.read()
    if not ret:
        break  # Break the loop if no frames are left

    frame_count += 1

    # Perform YOLO inference on every nth frame (to improve speed)
    if frame_count % 2 == 0:  # Skip alternate frames for faster processing
        results = model(frame)
        result_frame = results[0].plot()
    else:
        result_frame = frame  # Use the original frame for skipped frames

    # Write the frame with detections to the output video


    # Display the frame (optional)
    cv2.imshow('YOLO Detection', result_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to quit
        break

# Release resources
cap.release()

cv2.destroyAllWindows()

end_time = time.time()

print(f"Processing time: {end_time - start_time:.2f} seconds")
