from fastapi import APIRouter, Depends, HTTPException
from typing import Sequence
from datetime import datetime

from backend.models.user_details import UserDetails
from backend.services.coworking.students import ActiveUserService


__authors__ = ["Emma Coye, Manasi Chaudhary, Caroline Bryan, Kathryn Brown"]
__copyright__ = "Copyright 2025"
__license__ = "MIT"

# separate router file for B1's user story 1 (sally student checking friends)

api = APIRouter(prefix="/api/coworking")


@api.get(
    "/students/{field}",  # TODO: search by more general terms
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
def check_user_activity(field: str | int) -> bool:  # appearing in /docs yay! # TODO
    try:
        return ActiveUserService.check_if_active(field)
    # TODO maybe this is where we call ai to format and look pretty? idk
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
) -> list[UserDetails]:  # TODO check course_id right way to access?
    try:
        return ActiveUserService.get_active_classmates(
            course_input
        )  # search by general info (course, section, etc)
    except:
        raise HTTPException(
            status_code=404, detail="No active classmates could be found."
        )

# not relevant to goal of user story so removing for now
"""
@api.get(
    "/students/active",
    summary="Get all active users in CSXL",
    description=" TODO ",
    responses={
        200: {
            "description": "Users returned!",
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
def get_active_users() -> list[UserDetails]:  # TODO
    try:
        # use get_active_reservations and filter here?
        return None  # call service here
        # todo create fake data to test with

    except:
        raise HTTPException(status_code=404, detail="No active users could be found")

"""