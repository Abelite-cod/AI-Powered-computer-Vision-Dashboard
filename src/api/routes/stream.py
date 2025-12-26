from fastapi import APIRouter
from starlette.responses import StreamingResponse
import cv2

from src.runtime.loader import ModelLoader
from src.runtime.utils import draw_boxes, format_results

router = APIRouter()
loader = ModelLoader()

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

def generate_frames():
    while True:
        success, frame = cap.read()
        if not success or frame is None:
            cv2.waitKey(10)
            continue

       
        results = loader.predict(frame)
        detections = format_results(results, loader.class_names)

       
        draw_boxes(frame, detections, loader.class_names)

        _, buffer = cv2.imencode(".jpg", frame)
        frame_bytes = buffer.tobytes()

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" +
            frame_bytes +
            b"\r\n"
        )

@router.get("/stream")
def stream():
    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )
