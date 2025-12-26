import json
from datetime import datetime

def serialize_event(event: dict):
    clean = {}
    for k, v in event.items():
        if isinstance(v, datetime):
            clean[k] = v.isoformat()
        else:
            clean[k] = v
    return clean


def log_event(event: dict):
    event = serialize_event(event)

    with open("logs/events.log", "a") as f:
        f.write(json.dumps(event) + "\n")