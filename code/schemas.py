from pydantic import BaseModel
from typing import List

class ClaimExtraction(BaseModel):
    issue_type: str
    object_part: str
    claimed_severity: str
    confidence: float

class VisionResult(BaseModel):
    visible_damage: bool
    issue_type: str
    object_part: str
    image_quality: str
    severity: str
    supporting_image_ids: List[str]

class FinalDecision(BaseModel):
    claim_status: str
    severity: str
    risk_flags: List[str]
