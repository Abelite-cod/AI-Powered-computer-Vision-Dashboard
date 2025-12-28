# src/runtime/camera.py
import cv2
import threading

class CameraManager:
    _camera = None
    _lock = threading.Lock()
    _ref_count = 0  # number of clients currently streaming

    @classmethod
    def get_camera(cls):
        with cls._lock:
            if cls._camera is None:
                cls._camera = cv2.VideoCapture(0)
                if not cls._camera.isOpened():
                    raise RuntimeError("Failed to open camera")
            cls._ref_count += 1
            return cls._camera

    @classmethod
    def release_camera(cls):
        with cls._lock:
            cls._ref_count -= 1
            if cls._ref_count <= 0 and cls._camera is not None:
                cls._camera.release()
                cls._camera = None
                cls._ref_count = 0