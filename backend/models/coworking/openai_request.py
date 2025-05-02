# Request model
from pydantic import BaseModel
from backend.models.coworking.reservation import ReservationRequest
from datetime import datetime
from typing import Union

__authors__ = ["Emma Coye", "Manasi Chaudhary", "Caroline Bryan", "Kathryn Brown"]
__copyright__ = "Copyright 2025"
__license__ = "MIT"


class GeneralAIResponse(BaseModel):
    method: str
    expected_input: str
    # expected_input: Union[str, ReservationRequest]


class IntAIResponse(BaseModel):
    id: int


class NoSuchPathException(Exception):
    pass
