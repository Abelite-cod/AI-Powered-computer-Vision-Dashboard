from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import numpy as np
import cv2
import base64
import asyncio
from collections import defaultdict
from src.runtime.loader import ModelLoader
from src.runtime.utils import format_results
from motpy import Detection, MultiObjectTracker

router = APIRouter()
loader = ModelLoader()
tracker = MultiObjectTracker(dt=1.0, tracker_kwargs={"max_staleness": 5})
smoothed_boxes = defaultdict(lambda: None)
SMOOTHING_ALPHA = 0.9
DEADZONE = 2
LOCK_SIZE = True

def deadzone(prev, curr, threshold=DEADZONE):
    return prev if abs(curr - prev) < threshold else curr

@router.websocket("/ws/detections")
async def websocket_detections(ws: WebSocket):
    await ws.accept()
    print("WebSocket connected")
    try:
        while True:
            msg = await ws.receive()
            if msg["type"] == "websocket.disconnect":
                print("Client disconnected")
                break

            img_bytes = msg.get("bytes") or base64.b64decode(msg.get("text", ""))
            if not img_bytes:
                continue

            np_arr = np.frombuffer(img_bytes, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            if frame is None:
                await ws.send_json({"error": "Invalid frame"})
                continue
            h, w = frame.shape[:2]
            results = loader.predict(frame)
            detections = format_results([results], loader.class_names)
            mot_detections = [Detection(box=det["bbox"], score=det["confidence"], class_id=det["class_id"])
                              for det in detections]

            tracks = tracker.step(detections=mot_detections)
            tracked_objects = []

            for track in tracks:
                x1, y1, x2, y2 = track.box
                tid = track.id
                cx, cy = (x1+x2)/2, (y1+y2)/2
                w, h = x2-x1, y2-y1

                prev = smoothed_boxes[tid]
                if prev is None:
                    smooth = [cx, cy, w, h]
                else:
                    smooth_cx = deadzone(prev[0], SMOOTHING_ALPHA*prev[0] + (1-SMOOTHING_ALPHA)*cx)
                    smooth_cy = deadzone(prev[1], SMOOTHING_ALPHA*prev[1] + (1-SMOOTHING_ALPHA)*cy)
                    smooth_w = prev[2] if LOCK_SIZE else SMOOTHING_ALPHA*prev[2] + (1-SMOOTHING_ALPHA)*w
                    smooth_h = prev[3] if LOCK_SIZE else SMOOTHING_ALPHA*prev[3] + (1-SMOOTHING_ALPHA)*h
                    smooth = [smooth_cx, smooth_cy, smooth_w, smooth_h]

                smoothed_boxes[tid] = smooth
                cx, cy, w, h = smooth
                tracked_objects.append({
                    "bbox": [cx-w/2, cy-h/2, cx+w/2, cy+h/2],
                    "class_name": loader.class_names.get(track.class_id, "unknown"),
                    "confidence": float(track.score),
                    "track_id": tid
                })

            await ws.send_json({"detections": tracked_objects, "count": len(tracked_objects), 'frame_width': w, 'frame_height': h})
            await asyncio.sleep(0.03)
    except WebSocketDisconnect:
        print("WebSocket disconnected")
