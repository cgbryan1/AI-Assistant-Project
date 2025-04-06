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

    # TODO there might be other methods to utilize to better achieve this but i do feel better about this one even if its less efficient
    def check_if_active_by_pid1(self, pid: int) -> dict[User, str]:
        user: User = self._user_service.get(pid)  # get the user by pid

        reservations = self._reservation_service.get_current_reservations_for_user(
            subject=user,
            focus=user,
            state=ReservationState.CHECKED_IN,  # only want if checked in (ex no unfulfilled reservations)
        )
        # Use colons instead of commas because it's a dictionary ????
        if len(reservations) > 0:
            return {user: reservations[0]._seat_svc}
        else:
            return {User: None}

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

    # TODO not sure how to handle response
    def check_if_active_by_string(self, name: str) -> dict[User, str]:
        # name, onyen, email

        possible_users: list[User] = self._user_service.search(
            self, name
        )  # returns list of users matching params

        # TODO use ai here to determine which is which?

        now = datetime.now()

        max_duration = (
            self._reservation_service._policy_svc.maximum_initial_reservation_duration(
                user
            )
        )  # max time a reservation can last
        time_range = TimeRange(start=now - max_duration, end=now + max_duration)

        reservations: list[ReservationState] = []
        for user in possible_users:
            reservations.append(
                self._reservation_service._get_active_reservations_for_user_by_state(
                    focus=user, time_range=time_range, state=ReservationState.CHECKED_IN
                )
            )

        # return reservations # currently returns list of reservations that are active and matching
        response: dict[User, str] = {}
        for reservation in reservations:
            response[reservation._user] = {reservation[0]._seat_svc}
        return response

    def check_if_active(self, input: str | int) -> dict[User, str]:
        """Umbrella method for API call"""
        if input is str:
            return self.check_if_active_by_string(input)
        if input is int:
            return self.check_if_active_by_pid1(input)

    def get_active_classmates(self, course: str) -> bool:
        # TODO use AI to parse the input for the get() method? would need subject doe, course number, and section number.
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


# removing this because not directly related or needed for current user story
"""
    def get_all_active(self) -> list[UserDetails]:
        # use get_seat_reservations() ?
        active_users = {}  # sort by user id
        now = datetime.now()
        # TODO should we directly query the database here?
        """

# maybe we have the AI analyze te input and decide which function to call?
# might be helpful because it can read and interpret the diff data types and format a nice response for the user

# this is another story so removing for now
# def check_if_visible(self):
# check_if_active() and not ghost mode

# TODO
# we would need to start using our extended userdetails here instead of user which is gonna be a pain.
# do we rewrite the entire reservation.py folder and have it inherit our child class instead?

# update: this is a future story i think
