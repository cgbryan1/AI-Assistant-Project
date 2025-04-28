from sqlalchemy.orm import Session
import json
from backend.entities.ai_audit_log_entity import AIAuditLogEntity


def log_ai_interaction(db_session: Session, prompt: str, ai_response: dict) -> None:
    # TODO do we need to have the timestamp?
    log_entry = AIAuditLogEntity(
        user_prompt=prompt, json_response=json.dumps(ai_response)
    )
    db_session.add(log_entry)
    db_session.commit()


# FLAG could delete this file??
