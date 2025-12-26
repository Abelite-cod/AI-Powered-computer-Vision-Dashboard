from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DetectionEvent(BaseModel):
    event_type: str           
    class_name: str
    confidence: float
    source: str              
    timestamp: Optional[datetime] = None
    user_id: Optional[str] = None
