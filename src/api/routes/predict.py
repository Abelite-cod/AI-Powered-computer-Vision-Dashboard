from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from src.runtime.loader import ModelLoader
from src.runtime.utils import format_results
from src.middleware.jwt import verify_token
import cv2
import numpy as np
import time

router = APIRouter(tags=["Prediction"])
loader = ModelLoader()


# CONFIG

MAX_FILE_SIZE = 5 * 1024 * 1024
ALLOWED_TYPES = ["image/jpeg", "image/png", "image/jpg"]


# PREDICT ENDPOINT

@router.post("/predict", status_code=status.HTTP_200_OK)
async def predict_image(
    file: UploadFile = File(...),
    user=Depends(verify_token)
):
  
    
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=415,
            detail="Unsupported file type. Use JPG or PNG."
        )

    contents = await file.read()

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File too large. Max size is 5MB."
        )

    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        raise HTTPException(
            status_code=400,
            detail="Invalid image file."
        )


    start_time = time.time()
    results = loader.predict(img)
    inference_time = round(time.time() - start_time, 3)

    detections = format_results(results, loader.class_names)

 
    return {
        "count": len(detections),
        "inference_time": inference_time,
        "detections": detections
    }
