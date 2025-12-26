import cv2

def format_results(results, class_names):
    output = []

    for r in results:
        if r.boxes is None:
            continue

        for det in r.boxes.data.tolist():
            x1, y1, x2, y2, conf, cls = det
            output.append({
                "bbox": [float(x1), float(y1), float(x2), float(y2)],
                "confidence": float(conf),
                "class_id": int(cls),
                "class_name": class_names[int(cls)]
            })

    return output


def draw_boxes(frame, detections, class_names):
    for det in detections:
        x1, y1, x2, y2 = map(int, det["bbox"])
        label = f"{det['class_name']} {det['confidence']:.2f}"

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(
            frame,
            label,
            (x1, y1 - 8),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2
        )
