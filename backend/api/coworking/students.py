from fastapi import APIRouter, Depends, HTTPException
from typing import Sequence
from datetime import datetime

from backend.models.user_details import UserDetails


__authors__ = ["Emma Coye, Manasi Chaudhary, Caroline Bryan, Kathryn Brown"]
__copyright__ = "Copyright 2025"
__license__ = "MIT"

# separate router file for B1's user story 1 (sally student checking friends)

api = APIRouter(prefix="/api/coworking")


@api.get(
    "/students/{pid}",  # TODO: double check pid vs onyen
    summary="Get active specified user",
    description=" Checking whether a specifed user is active and visible in the XL. ",
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
)  # TODO add in response model, fix response codes
def check_user_activity(pid: int) -> bool:  # appearing in /docs yay! # TODO
    try:
        # existing method to get a user's active reservations: _get_active_reservations_for_user()
        return True  # call service here
    except:
        raise HTTPException(status_code=404, detail="No active user could be found.")


# Route based on course
@api.get(
    "/student?course={course_id}",
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
    course_id: str,
) -> list[UserDetails]:  # TODO check course_id right way to access?
    try:
        # course_id is input, route for
        # todo create fake data to test with
        return []  # call service here
    except:
        raise HTTPException(
            status_code=404, detail="No active classmates could be found."
        )


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