from datetime import datetime
from fastapi import Depends

from backend.models.coworking.reservation import ReservationState
from backend.models.coworking.time_range import TimeRange
from backend.models.office_hours.course_site import CourseSite
from backend.models.user import User
from backend.models.user_details import UserDetails
from ..user import UserService
from reservation import ReservationService
from backend.services.academics.course_site import CourseSiteService
from backend.services.academics import SectionService

__authors__ = ["Emma Coye", "Manasi Chaudhary", "Caroline Bryan", "Kathryn Brown"]
__copyright__ = "Copyright 2025"
__license__ = "MIT"


class ActiveUserService:
    _user: UserService
    reservation_service: ReservationService
    course_site_service: CourseSiteService
    section_service: SectionService

    def __init__(self, user_service: UserService = Depends()):
        """Initialize the User Service."""
        self._user = user_service
        self.reservation_service: ReservationService = Depends()

    def check_if_active_by_pid(self, pid: int) -> dict[User, str]:
        user: User = self._user_service.get(pid)

        reservations = self._reservation_service.get_current_reservations_for_user(
            subject=user,
            focus=user,
            state=ReservationState.CHECKED_IN,
        )
        if len(reservations) > 0:
            return {user: reservations[0]._seat_svc}
        else:
            return {User: None}

    def check_if_active_by_string(self, name: str) -> dict[User, str]:

        # AI integration here!
        # Input for AI:
        # 1. The user's input (string)
        # 2. Context of request, including a warning to AI that there might be a typo
        # 3. List of active users in XL

        # TODO need get active user helper method

        # Expected output: a User object and its corresponding reservation

        return None

    def check_if_active(self, input: str | int) -> dict[User, str]:
        """Umbrella method for API call"""
        if input is str:
            return self.check_if_active_by_string(input)
        if input is int:
            return self.check_if_active_by_pid(input)

    def get_active_classmates(self, course: str) -> bool:
        # AI integration here!
        # Input for AI:
        # 1. The user's input (string)
        # 2. Context of request, including a warning to AI that there might be a typo
        # 3. List of active users in XL

        # Input:
        # "This is the user's input: ________.
        # These are the classes that the user is in ___.
        # If the user is looking for a specific class, return a list with their course abbreviation, number, and section (each as an index).
        # If they're searching for people in any class, please return an empty list."

        # Expected output: a list - empty if searching all classes, with search params if by section

        # We'll use this response to figure out which helper method to call.

        # TODO figure out helper methods here
        # TODO need get active users helper method
        return None


# -------------------------------- Code Graveyard

"""
    # Removing for the below purpose - will come back to this if needed, so don't want to delete in case
    # TODO i feel less confident in this implementation but if we do it right it could be more efficient? idk.
    def check_if_active_by_pid2(self, pid: int) -> dict[User, str]:
        user: User = self._user_service.get(pid)  # get the user by pid
        now = datetime.now()

        max_duration = (
            self._reservation_service._policy_svc.maximum_initial_reservation_duration(
                user
            )
        )  # max time a reservation can last
        time_range = TimeRange(start=now - max_duration, end=now + max_duration)

        reservations = (
            self._reservation_service._get_active_reservations_for_user_by_state(
                focus=user, time_range=time_range, state=ReservationState.CHECKED_IN
            )
        )

        if len(reservations) > 0:
            return {user, reservations[0]._seat_svc}
        else:
            return {user, None}
    """

# also not directly related or needed for current user story
"""
    def get_all_active(self) -> list[UserDetails]:
        # use get_seat_reservations() ?
        active_users = {}  # sort by user id
        now = datetime.now()
        # TODO should we directly query the database here?
        """

# old implementation without AI:
"""
    def check_if_active_by_string(self, name: str) -> dict[User, str]:

        # AI integration here!
        # Input for AI:
        # 1. The user's input (string)
        # 2. Context of requesdt, including a warning to AI that there might be a typo
        # 3. List of active users in XL
        
        # Expected output: a User object and its corresponding reservation

        possible_users: list[User] = self._user_service.search(
            self, name
        )  # returns list of users matching params

        now = datetime.now()

        max_duration = (
            self._reservation_service._policy_svc.maximum_initial_reservation_duration(
                user
            )
        )
        time_range = TimeRange(start=now - max_duration, end=now + max_duration)

        reservations: list[ReservationState] = []
        for user in possible_users:
            reservations.append(
                self._reservation_service._get_active_reservations_for_user_by_state(
                    focus=user, time_range=time_range, state=ReservationState.CHECKED_IN
                )
            )

        response: dict[User, str] = {}
        for reservation in reservations:
            response[reservation._user] = {reservation[0]._seat_svc}
        return response
        """

# non-ai method for getting active classmates
"""
    def get_active_classmates(self, course: str) -> bool:
        course: CourseSite = (
            self.section_service.get()
        )  # returns a CatalogSection TODO how to work with it?

        roster = self.course_site_service.get_course_site_roster(
            self._user, course.id
        )  # TODO add pagination params
        # returns Paginated[CourseMemberOverview]:

        active_classmates = []
        for classmate in roster:
            if self.check_if_active_by_pid1(classmate.pid):
                active_classmates.append(classmate)
        # Will this return all user info? Do we need to put in this service layer method?
        return active_classmates 
        """