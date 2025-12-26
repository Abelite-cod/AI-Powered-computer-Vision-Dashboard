from ultralytics import YOLO
import cv2

model = YOLO("C:/Users/user/OneDrive/Documents/Phase2_modelRuntime_Tracking/models/yolov8m.pt")

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("Camera not accessible")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame, conf=0.15, verbose=False)

    annotated = results[0].plot()
    cv2.imshow("YOLO11 Test", annotated)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
