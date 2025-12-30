# src/api/routes/stream.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.responses import StreamingResponse
import cv2
import jwt

from src.runtime.loader import ModelLoader
from src.runtime.utils import draw_boxes, format_results
from src.runtime.camera import CameraManager
from src.api.routes.auth import SECRET_KEY  # your existing secret
from fastapi import Query

router = APIRouter()
loader = ModelLoader()
security = HTTPBearer(auto_error=False)




def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    token: str | None = Query(default=None),
):
    # Prefer Authorization header
    if credentials:
        token_str = credentials.credentials
    # Fallback to query param
    elif token:
        token_str = token
    else:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(token_str, SECRET_KEY, algorithms=["HS256"])
        return payload["sub"]

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")




def generate_frames():
    """
    Generator function to read frames from camera, run predictions, 
    and yield them as JPEGs for streaming.
    Camera is released automatically when generator exits.
    """
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
def stream(user: str = Depends(get_current_user)):
    """
    Stream live camera feed to authenticated clients.
    Multi-client-safe; camera is released automatically.
    """
    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )