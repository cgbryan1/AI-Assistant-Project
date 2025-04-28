from fastapi import APIRouter, Depends, HTTPException
from typing import Sequence
from datetime import datetime

from backend.models.user_details import UserDetails
from backend.services.coworking.students import ActiveUserService


__authors__ = ["Emma Coye, Manasi Chaudhary, Caroline Bryan, Kathryn Brown"]
__copyright__ = "Copyright 2025"
__license__ = "MIT"

api = APIRouter(prefix="/api/coworking")

# FLAG are both of these routes used?


@api.get(
    "/students/{field}",
    summary="Get active specified user",
    description=" Checking whether a specifed user is active and visible in the XL. Finding user by PID, onyen, email, or name.",
    responses={
        200: {
            "description": "User returned!",
        },
        307: {
            "description": "Redirected.",
        },
        404: {
            "description": "Users not found.",
        },
    },
    tags=["Coworking"],
)
def check_user_activity(field: str | int) -> bool:
    try:
        return ActiveUserService.check_if_active(field)
    except:
        raise HTTPException(status_code=404, detail="No active user could be found.")


# Route based on course
@api.get(
    "/student?course={course_input}",
    summary="Get active users in a specified course.",
    description=" TODO ",
    responses={
        200: {
            "description": "Classmates returned!",
        },
        307: {
            "description": "Redirected.",
        },
        404: {
            "description": "Classmates not found.",
        },
    },
    tags=["Coworking"],
)
def get_active_classmates(
    course_input: str,
) -> list[UserDetails]:
    try:
        return ActiveUserService.get_active_classmates(course_input)
    except:
        raise HTTPException(
            status_code=404, detail="No active classmates could be found."
        )
