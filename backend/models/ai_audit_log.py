# # models/ai_audit_log_model.py
# from pydantic import BaseModel
# from datetime import datetime


# class AIAuditLogModel(BaseModel):
#     id: int | None = None
#     user_prompt: str
#     json_response: str
#     created_at: datetime

#     # fixing for now
#     model_config = {"from_attributes": True}  # This replaces orm_mode in Pydantic v2
