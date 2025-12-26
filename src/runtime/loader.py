from ultralytics import YOLO

class ModelLoader:
    def __init__(self):
        self.model = YOLO("models/yolov8m.pt")
        self.class_names = self.model.names

    def predict(self, frame):
        return self.model(frame, verbose=False)
