from datetime import datetime
from typing import Annotated
from fastapi import Depends
from pydantic import ValidationError

from backend.models.academics.my_courses import CourseSiteOverview, TermOverview
from backend.models.active_students_response import (
    ActiveStudentResponse,
    ClassSearchResponse,
)
from backend.models.coworking.reservation import ReservationState
from backend.models.coworking.time_range import TimeRange
from backend.models.office_hours.course_site import CourseSite
from backend.models.user import User
from backend.models.user_details import UserDetails
from backend.services.openai import OpenAIService
from ..user import UserService
from backend.services.coworking.reservation import ReservationService
from backend.services.academics.course_site import CourseSiteService
from backend.services.academics import SectionService

__authors__ = ["Emma Coye", "Manasi Chaudhary", "Caroline Bryan", "Kathryn Brown"]
__copyright__ = "Copyright 2025"
__license__ = "MIT"


class ActiveUserService:
    _user: UserService
    _reservation_svc: ReservationService
    course_site_service: CourseSiteService
    section_service: SectionService

    def __init__(
        self,
        openai_svc: Annotated[OpenAIService, Depends()],
        user_service: UserService = Depends(),
        reservation_service: ReservationService = Depends(),
    ):
        """Initialize the User Service."""
        self._user_svc = user_service
        self._reservation_svc = reservation_service
        self._openai_svc = openai_svc

    def check_if_active_by_pid(self, pid: int) -> dict[User, str]:
        user: User = self._user_svc.get(pid)

        reservations = self._reservation_svc.get_current_reservations_for_user(
            subject=user,
            focus=user,
            state=ReservationState.CHECKED_IN,
        )
        if len(reservations) > 0:
            return {user: reservations[0]._seat_svc}
        else:
            return {User: None}

    def check_if_active_by_string(self, name: str) -> dict[User, str]:
        """This method checks if a User is active in the CSXL based on a provided string (name, email, etc.).
        AI is used to match the input across associated User fields and deal with typos.
        """

        context: str = (
            "You are an assistant that interprets user input - be aware that there may be typos in user input and be logical about matches. "
            "The client is requesting a user by name - we need to know if this user is active in the coworking space, and if the user is active, what room they are in. "
            "You will recieve a dictionary with Users as keys and their reservations as values."
            "Compare the input against the dictionary. If you're able to match the client's input with an active user, send back a dictionary with the key being the User object and the corresponding reservation. "
            "Be conscious of potential typos/misspellings and please try to only return one user. "
            "If you cannot decide between more than one potential option, you may return multiple key value pairs in the dictionary."
            "If there is no name match, return an empty dictionary. "
        )

        active_users: dict[User, str] = self.get_all_active_users(self._user)

        conditional_input: str = (
            f"This is a dictionary of active users and corresponding reservations in the coworking space: {active_users}. Here is the user's input: {name}."
        )

        ai_output: dict[
            User, str
        ]  # We'll use this response to figure out which helper method to call.

        response_model = ActiveStudentResponse

        try:
            ai_output = self._openai_svc.prompt(
                context, conditional_input, response_model
            )
            return ai_output
        except (KeyError, AttributeError, ValidationError) as e:
            return ActiveStudentResponse(ai_output={})

    def check_if_active(self, input: str | int) -> dict[User, str]:
        """Umbrella method for API call"""
        if input is str:
            return self.check_if_active_by_string(input)
        if input is int:
            return self.check_if_active_by_pid(input)

    def get_active_classmates(self, course: str) -> dict[User, str]:
        """This method checks if any user is active in the CSXL based on a provided class filter).
        AI is used to match the input across associated User fields and deal with typos.
        """
        # Classes in which the user is currently enrolled.
        term_overview: list[TermOverview] = (
            self.course_site_service.get_user_course_sites(self._user)
        )
        current_classes: list[CourseSiteOverview] = []
        for term in term_overview:
            for desired_course in course.sites:
                current_classes.append(desired_course)

        # yapped here. very much welcome to revisions to be more concise!!! -caroline
        context: str = (
            "You are an assistant that interprets user input to enable other functions, chosen for the ability to look past potential typos. "
            "The student is sharing a course that they may or may not be a member of. "
            "Compare their input against the courses that they are registered for. Send back a list of strings. "
            "If the user inputs NO course then return this list empty. "
            "If you're able to match the user's input with one of their registered courses, return a list with the first index being the course subject abbreviation (eg. COMP), the second index being the number (eg. 436) and the third index being the section (eg. 001). "
            "If you cannot fulfill the request due to an error (e.g., invalid input, missing information), return the list with a singular value: a concise error message to be sent directly to the user."
        )

        conditional_input: str = (
            f"This is the user's input: {course}. This is a list of the courses that the user is in: {current_classes}."
        )
        response_model = ClassSearchResponse

        ai_output: list[str] = (
            []
        )  # We'll use this response to figure out which helper method to call.

        # helper methods:
        active_users: dict[User, str] = self.get_all_active_users(self._user)
        common_users: dict[User, str] = {}

        try:
            ai_output = self._openai_svc.prompt(
                context, conditional_input, response_model
            )
        except (KeyError, AttributeError, ValidationError) as e:
            ai_output = []

        if len(ai_output == 1):
            raise ValueError(ai_output[0])
        if len(ai_output) > 0:  # check specific class
            site_id = ai_output[0]
            pagination_params = ai_output[1]  # sample output
            self.course_site_service.get_course_site_roster(
                self._user, site_id, pagination_params
            )

            for member in ai_output:
                # check to see if the user is with itself
                if member == self._user:
                    continue
                if member in active_users:
                    # add to list of common users
                    temp = self.check_if_active_by_string(member)
                    for key in temp:
                        common_users[key] = temp[key]
            return common_users

        else:  # check all classes
            own_site_ids = {
                course.site_id for course in current_classes
            }  # get the site_id

            for other_user in active_users.keys():
                # check to see if the user is with itself
                if other_user == self._user:
                    continue

                other_user_classes = self.course_site_service.get_user_course_sites(
                    other_user
                )
                other_user_class_ids = {course.site_id for course in other_user_classes}

                for id in own_site_ids:
                    if id in other_user_class_ids:
                        temp = self.check_if_active(other_user)
                        for key in temp:
                            common_users[key] = temp[key]
                            ai_output.append(other_user)
                        break

            return common_users

    def get_all_active_users(self, subject: User) -> dict[User, str]:
        """Helper method for getting all active users (need ambassador permissions).
        Takes in the user making the request to make sure appropriate permissions are granted.
        Returned dict is used as input to AI."""

        # Collect all reservations (upcoming and active using ReservationService helper methods)
        # TODO for future story: implement ghost mode; we will exclude any students who can be on this list but activated ghost mode
        xl_reservations = self._reservation_svc.list_all_active_and_upcoming_for_xl(
            subject
        )
        room_reservations = (
            self._reservation_svc.list_all_active_and_upcoming_for_rooms(subject)
        )
        active_users = {}  # Store User object and location

        # process XL reservations
        for reservation in xl_reservations:
            if reservation.state == ReservationState.CHECKED_IN:
                for user in reservation.users:
                    # Get seat loc
                    if reservation.seats and len(reservation.seats) > 0:
                        seat_location = reservation.seats[
                            0
                        ].location  # Assuming first seat is relevant

                        # use title for a more descriptive name for output
                        active_users[user] = f"{seat_location.title}"

        # process room reservations
        for reservation in room_reservations:
            if reservation.state == ReservationState.CHECKED_IN:
                for user in reservation.users:
                    # Get room loc
                    room_id = reservation.room.id
                    active_users[user] = f"{room_id}"

        return active_users


"""
    def get_all_active_users(self, subject: User) -> dict[User, str]:
        # Helper method for getting all active users (need ambassador permissions)
        # takes in the user making the request to make sure appropriate permissions are granted
        # Return as input to AI for parsing a dictionary of active users and returning based on required details

        # Collect all reservations (upcoming and active using ReservationService helper methods)
        # TODO implement ghost mode; we will exclude any students who can be on this list but activated ghost mode
        xl_reservations = self._reservation_svc.list_all_active_and_upcoming_for_xl(
            subject
        )
        room_reservations = (
            self._reservation_svc.list_all_active_and_upcoming_for_rooms(subject)
        )
        active_users = {}  # Store User object and location

        # process XL reservations
        for reservation in xl_reservations:
            if reservation.state == ReservationState.CHECKED_IN:
                for user in reservation.users:
                    # Get seat loc
                    if reservation.seats and len(reservation.seats) > 0:
                        seat_location = reservation.seats[
                            0
                        ].location  # Assuming first seat is relevant

                        # Use title isntead of id for a more descriptive name for user output
                        active_users[user] = {seat_location.title}

        # process room reservations
        for reservation in room_reservations:
            if reservation.state == ReservationState.CHECKED_IN:
                for user in reservation.users:
                    # Get room loc
                    room_id = reservation.room.id
                    active_users[user] = f"{room_id}"

        return active_users
"""  # could not tell you why I had two here


# -------------------------------- Code Graveyard

"""
    # Removing for the below purpose - will come back to this if needed, so don't want to delete in case
    # TODO i feel less confident in this implementation but if we do it right it could be more efficient? idk.
    def check_if_active_by_pid2(self, pid: int) -> dict[User, str]:
        user: User = self._user_svc.get(pid)  # get the user by pid
        now = datetime.now()

        max_duration = (
            self._reservation_svc._policy_svc.maximum_initial_reservation_duration(
                user
            )
        )  # max time a reservation can last
        time_range = TimeRange(start=now - max_duration, end=now + max_duration)

        reservations = (
            self._reservation_svc._get_active_reservations_for_user_by_state(
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

        possible_users: list[User] = self._user_svc.search(
            self, name
        )  # returns list of users matching params

        now = datetime.now()

        max_duration = (
            self._reservation_svc._policy_svc.maximum_initial_reservation_duration(
                user
            )
        )
        time_range = TimeRange(start=now - max_duration, end=now + max_duration)

        reservations: list[ReservationState] = []
        for user in possible_users:
            reservations.append(
                self._reservation_svc._get_active_reservations_for_user_by_state(
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
