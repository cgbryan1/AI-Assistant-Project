from .user_details import UserDetails

__authors__ = ["Caroline Bryan", "Emma Coye", "Manasi Chaudhary", "Kathryn Brown"]
__copyright__ = "Copyright 2023"
__license__ = "MIT"


class ActiveUser(UserDetails):
    """
    Pydantic model to represent an `ActiveUser` in the CSXL, including the permissions
    a UserDetails has.

    This model is based on the `UserDetails` model (because this model contains details about classes).
    """

    # from user details we have sections (list of classes they're in)
    ghost_mode: bool  # true if in ghost mode, false if open to be found
    currently_active: bool  # true if checked in

    # TODO figure out how to tie in reservations - probably on reservation end or thru status.py
    # status.py in coworking checks status of the XL coworking space, including reservations, for a given user
