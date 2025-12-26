def filter_boxes(results, min_area=100, conf_thresh=None):
    """
    Filters boxes by minimum area and optional confidence threshold.
    """
    filtered = []
    for box in results.boxes.data.tolist():
        x1, y1, x2, y2, conf, cls = map(float, box)
        area = (x2 - x1) * (y2 - y1)
        if area < min_area:
            continue
        if conf_thresh is not None and conf < conf_thresh:
            continue
        filtered.append([x1, y1, x2, y2, conf, cls])
    return filtered
