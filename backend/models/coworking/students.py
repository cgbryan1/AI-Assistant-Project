"""Creating new model based on User for students_entity.py"""

from pydantic import BaseModel
from backend.models.user import User, UserIdentity
from datetime import datetime, timezone
from .reservation import Reservation

__authors__ = ["Manasi Chaudhary", "Emma Coye", "Caroline Bryan", "Kathryn Brown"]
__copyright__ = "Copyright 2023 - 2024"
__license__ = "MIT"


class Students(BaseModel):
    """
    Pydantic model to represent User information as well as reservation information
    """

    # Present/not
    is_present: bool = False
    # Ghost mode (TODO -- see if we actually need it)
    is_ghost_mode: bool = False
    # Timestamp (TODO not sure if there's eastern version of UTC)
    last_checked_in: datetime = datetime.now(timezone.utc)
    # Reservation information -- TODO
    reservations: list[Reservation] = []


# FLAG could this be deleted?
