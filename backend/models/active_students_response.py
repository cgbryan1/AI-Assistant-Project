from typing import List, Optional
from pydantic import BaseModel

from backend.models.user import User

__authors__ = ["Caroline Bryan, Emma Coye, Manasi Chaudhary, Kathryn Brown"]
__copyright__ = "Copyright 2025"
__license__ = "MIT"


class ActiveStudentResponse(BaseModel):
    """Response model for OpenAI request to find active students. Modeled in context of check_if_active().
    Returns corresponding User and reservation (as string), multiple if multiple hits.
    """

    active_users: Optional[dict[str, str]] = None
    # message: str


class ClassSearchResponse(BaseModel):
    """Used for AI integration point of get_active_classmates().
    @ Index 1: course abbreviation
    @ Index 2: course number
    @ Index 3: course section

    Empty: not searching for a specific class.
    """

    course_details: Optional[List[str]] = None
