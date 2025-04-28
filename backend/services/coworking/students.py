from typing import Annotated
from fastapi import Depends
from pydantic import ValidationError
from backend.test.services import user_data
from backend.models.academics.my_courses import CourseSiteOverview, TermOverview
from backend.models.active_students_response import (
    ActiveStudentResponse,
    ClassSearchResponse,
)
from backend.models.coworking.reservation import ReservationState
from backend.models.user import User
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
    _course_site_svc: CourseSiteService
    _section_svc: SectionService
    _openai_svc: OpenAIService

    def __init__(
        self,
        openai_svc: Annotated[OpenAIService, Depends()],
        user_service: UserService = Depends(),
        reservation_service: ReservationService = Depends(),
        course_site_svc: CourseSiteService = Depends(),
        section_svc: SectionService = Depends(),
    ):
        self._user = user_service
        self._reservation_svc = reservation_service
        self._course_site_svc = course_site_svc
        self._section_svc = section_svc
        self._openai_svc = openai_svc

    def check_if_active(self, name: str) -> str:
        context: str = (
            "You are an assistant that interprets user input - be aware that there may be typos in user input and be logical about matches. "
            "The client is requesting a user by name - we need to know if this user is active in the coworking space, and if the user is active, what room they are in. "
            "You will recieve a dictionary with Users as keys and their reservations as values."
            "Compare the input against the dictionary. If you're able to match the client's input with an active user, send back an active users dictionary with the key being the User object and the corresponding reservation, as well as a string message confirming or denying if the user is in the XL and where they are based on their reservation. "
            "Be conscious of potential typos/misspellings and please try to only return one user. "
            "If you cannot decide between more than one potential option, you may return multiple key value pairs in the dictionary."
            "If there is no name match, return an empty model. "
        )

        active_users: dict[str, str] = self.get_all_active_users()
        conditional_input: str = (
            f"This is a dictionary of active users and their corresponding reservations in the coworking space: {active_users}. Here is the name of the person the user is searching for: {name}."
        )

        try:
            response: ActiveStudentResponse = self._openai_svc.prompt(
                context, conditional_input, ActiveStudentResponse
            )
            # result is empty or active_users is None - use this message
            if response.active_users is None or not response.active_users:
                return f"{name} is not in the XL right now."
            return response.message
        except ValueError as ve:
            return str(ve)
        except Exception as e:
            return f"Error processing request: {e}"

    def get_active_classmates(self, course: str) -> dict[User, str]:
        """This method checks if any user is active in the CSXL based on a provided class filter).
        AI is used to match the input across associated User fields and deal with typos.
        """
        # Classes in which the user is currently enrolled.
        term_overview: list[TermOverview] = self._course_site_svc.get_user_course_sites(
            self._user
        )
        current_classes: list[CourseSiteOverview] = []
        for term in term_overview:
            for desired_course in course.sites:
                current_classes.append(desired_course)

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

        active_users: dict[User, str] = self.get_all_active_users()
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
            self._course_site_svc.get_course_site_roster(
                self._user, site_id, pagination_params
            )

            for member in ai_output:
                # check to see if the user is with itself
                if member == self._user:
                    continue
                if member in active_users:
                    # add to list of common users
                    temp = self.check_if_active(member)
                    for key in temp:
                        common_users[key] = temp[key]
            return common_users

        else:  # check all classes
            own_site_ids = {course.site_id for course in current_classes}

            for other_user in active_users.keys():
                # check to see if the user is with itself
                if other_user == self._user:
                    continue

                other_user_classes = self._course_site_svc.get_user_course_sites(
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

    def get_all_active_users(self) -> dict[str, str]:
        active_users = {}
        try:
            room_reservations = (
                self._reservation_svc.list_all_active_and_upcoming_for_rooms(
                    user_data.root
                )
            )
            print("Room Reservations:", room_reservations)
        except Exception as e:
            print("Issue getting room reservations:", e)
            room_reservations = []

        try:
            xl_reservations = self._reservation_svc.list_all_active_and_upcoming_for_xl(
                user_data.root
            )
        except Exception as e:
            print(f"Error getting XL reservations: {e}")
            xl_reservations = []

        for reservation in xl_reservations:
            if reservation.state == ReservationState.CHECKED_IN:
                if reservation.seats and len(reservation.seats) > 0:
                    seat_location = reservation.seats[0].title
                    for user in reservation.users:
                        active_users[str(user)] = seat_location

        for reservation in room_reservations:
            if reservation.state == ReservationState.CHECKED_IN:
                for user in reservation.users:
                    room_id = reservation.room.id
                    active_users[str(user)] = str(room_id)

        return active_users
