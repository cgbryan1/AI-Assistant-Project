# """Entity for AI Audit Log"""

# from sqlalchemy import Boolean, DateTime, Integer, String, Text
# from sqlalchemy.orm import Mapped, mapped_column, relationship
# from typing import Self
# from datetime import datetime, timezone
# from .entity_base import EntityBase
# from backend.models.ai_audit_log import AIAuditLogModel

# __authors__ = ["Manasi Chaudhary", "Emma Coye", "Caroline Bryan", "Kathryn Brown"]
# __copyright__ = "Copyright 2023 - 2024"
# __license__ = "MIT"


# class AIAuditLogEntity(EntityBase):
#     """Entity for logging user prompts/every AI interaction for auditing purposes"""

#     __tablename__ = "ai_audit_log"

#     id: Mapped[int] = mapped_column(Integer, primary_key=True)

#     # User prompt, stored as text (Text instead of String in case of lengthy response)
#     user_prompt: Mapped[str] = mapped_column(Text, nullable=False)

#     # JSON encoded response
#     json_response: Mapped[str] = mapped_column(Text, nullable=False)

#     # Time stamp when log entry was created
#     created_at: Mapped[datetime] = mapped_column(
#         DateTime, default=datetime.now(timezone.utc), nullable=False
#     )

#     def to_model(Self) -> AIAuditLogModel:
#         """Convert Entity to Model"""
#         return AIAuditLogModel(
#             id=Self.id,
#             user_prompt=Self.user_prompt,
#             json_response=Self.json_response,
#             created_at=Self.created_at,
#         )

#     @classmethod
#     def from_model(cls, model: AIAuditLogModel) -> Self:
#         """Convert model to Entity"""

#         return cls(
#             id=model.id,
#             user_prompt=model.user_prompt,
#             json_response=model.json_response,
#             created_at=model.created_at,
#         )
