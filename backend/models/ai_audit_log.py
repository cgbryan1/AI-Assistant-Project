# models/ai_audit_log_model.py
from pydantic import BaseModel
from datetime import datetime


class AIAuditLogModel(BaseModel):
    id: int | None = None
    user_prompt: str
    json_response: str
    created_at: datetime

    # TODO not sure if we need this part, got it from ChatGPT
    class Config:
        orm_mode = True  # This allows Pydantic to work seamlessly with ORM objects
