# src/api/routes/stream.py
from fastapi import APIRouter
from starlette.responses import StreamingResponse
import cv2
from src.runtime.loader import ModelLoader
from src.runtime.utils import draw_boxes, format_results
from src.runtime.camera import CameraManager

router = APIRouter()
loader = ModelLoader()

def generate_frames():
    try:
        cap = CameraManager.get_camera()
        while True:
            success, frame = cap.read()
            if not success or frame is None:
                cv2.waitKey(10)
                continue

            # Run prediction
            results = loader.predict(frame)
            detections = format_results(results, loader.class_names)

            # Draw boxes
            draw_boxes(frame, detections, loader.class_names)

            _, buffer = cv2.imencode(".jpg", frame)
            frame_bytes = buffer.tobytes()

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" +
                frame_bytes +
                b"\r\n"
            )
    finally:
        CameraManager.release_camera()

@router.get("/stream")
def stream():
    """
    Stream live camera feed to multiple clients.
    Camera is released automatically when no clients are connected.
    """
    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )