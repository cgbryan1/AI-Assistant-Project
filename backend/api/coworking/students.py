from fastapi import APIRouter, Depends, HTTPException
from typing import Sequence
from datetime import datetime

__authors__ = ["Emma Coye, Manasi Chaudhary, Caroline Bryan, Kathryn Brown"]
__copyright__ = "Copyright 2025"
__license__ = "MIT"

#  separate router file for B1's user story 1 (sally student checking friends)

api = APIRouter(prefix="/api/coworking")


@api.get(
    "/students?name={name-id}",  # TODO: double check
    summary="Get active specified user",
    description=" Checking whether a specifed user is active and visible in the XL. ",
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
)  # TODO add in response model, fix response codes, add description
def get_active_users():  # appearing in /docs yay!
    try:
        return 0  # call service here
    except:
        raise HTTPException(status_code=404, detail="Active users not found")


# Route based on course

# Route based on course section
