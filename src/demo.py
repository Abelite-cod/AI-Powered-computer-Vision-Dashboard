import cv2
from runtime.loader import ModelLoader
from runtime.utils import draw_boxes, format_results

# ---------------------
# CONFIG
# ---------------------
MODEL_PATH = "C:/Users/user/OneDrive/Documents/Phase2_modelRuntime_Tracking/models/yolov8x.pt"
IMG_SIZE = 640
CONF_THRESH = 0.15
source = "webcam"  # webcam/video/image

# ---------------------
# INIT MODEL
# ---------------------
loader = ModelLoader(model_path=MODEL_PATH, imgsz=IMG_SIZE, conf=CONF_THRESH)

# ---------------------
# HELPER FUNCTION
# ---------------------
def process_frame(frame):
    results = loader.predict(frame)
    detections = format_results([results], loader.class_names)
    draw_boxes(frame, detections, loader.class_names)
    cv2.imshow("YOLO8x Detection", frame)

# ---------------------
# PROCESS VIDEO/WEBCAM
# ---------------------
if isinstance(source, str) and source.lower() in ["webcam"] or source.lower().endswith((".mp4", ".avi", ".mov")):
    cap = cv2.VideoCapture(0 if source.lower() == "webcam" else source)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open {source}")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            process_frame(frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        cap.release()
        cv2.destroyAllWindows()

# ---------------------
# PROCESS SINGLE IMAGE
# ---------------------
elif isinstance(source, str):
    frame = cv2.imread(source)
    if frame is None:
        raise RuntimeError(f"Image not found: {source}")
    process_frame(frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
