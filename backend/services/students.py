from fastapi import Depends
from .user import UserService

__authors__ = ["Emma Coye", "Manasi Chaudhary", "Caroline Bryan", "Kathryn Brown"]
__copyright__ = "Copyright 2025"
__license__ = "MIT"


class ActiveUserService:
    _user: UserService

    def __init__(self, user_service: UserService = Depends()):
        """Initialize the User Service."""
        self._user = user_service

    # Helper method to find students under a query
    def search_current(self, _subject: User, query: str) -> list[User]:
        """Search for users by their name, onyen, email, TODO: by class.

        Args:
            subject: The user performing the action.
            query: The search query.

        Returns:
            list[User]: The list of users matching the query.
        """

    # Helper method to find active students under above query from above method

    # Helper method to see if student is under ghost mode or not
    # def find_visible():
