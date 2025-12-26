#Testing Runtime

import cv2
from runtime.loader import ModelLoader
from runtime.utils import draw_boxes, print_summary

# Load model
loader = ModelLoader(model_path="models/yolo11s.pt", imgsz=640, conf=0.15)

# Open webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("Could not open webcam")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # YOLO inference
    results = loader.predict(frame)

    # Draw boxes
    draw_boxes(frame, results)

    # Show frame
    cv2.imshow("YOLO11s Live Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()

# Print summary of detected objects in last frame
print_summary(results)
