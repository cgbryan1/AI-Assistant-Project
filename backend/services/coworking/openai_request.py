# Request Service
from backend.services.openai import OpenAIService
from backend.models.coworking.openai_request import (
    GeneralAIResponse,
    NoSuchPathException,
)
from backend.models.coworking.reservation import (
    ReservationState,
    ReservationPartial,
    ReservationRequest,
)
from typing import Annotated
from fastapi import Depends
from backend.services.coworking.students import ActiveUserService
from backend.services.coworking.reservation import ReservationService
from backend.api.authentication import registered_user
from datetime import datetime, date
from ...models import User
import re

__authors__ = ["Emma Coye", "Manasi Chaudhary", "Caroline Bryan", "Kathryn Brown"]
__copyright__ = "Copyright 2025"
__license__ = "MIT"


class AIRequestService:
    """Takes in request from the frontend and has OpenAI decides which API route to use."""

    def __init__(
        self,
        openai_svc: Annotated[OpenAIService, Depends()],
        active_user_svc: Annotated[ActiveUserService, Depends()],
        reservation_svc: Annotated[ReservationService, Depends()],
        user: Annotated[User, Depends(registered_user)],
    ):
        """Initialize the User Service."""
        self._openai_svc = openai_svc
        self._active_user_svc = active_user_svc
        self._reservation_svc = reservation_svc
        self._subject = user

    def determine_request(self, user_prompt: str) -> str:
        """Service method that uses AI and a user prompt to determine what action to take."""

        if re.search(r"\b(?:hi|hello|hey)\b", user_prompt, re.IGNORECASE):
            return "Hi! What can I help you with"

        if re.search(r"\b(?:who|anyone)\b", user_prompt, re.IGNORECASE):
            return "I'll need to know a little more information. Who would you like me to check for in the XL?"

        if re.search(r"\bclass(es)?\b", user_prompt, re.IGNORECASE) or re.search(
            r"\b[A-Za-z]{2,4}\s*\d{2,4}\b", user_prompt  # Found online
        ):
            return "The CSXL chat does not currently have any functionality that matches your request. Stay tuned for when you can!"

        context: str = (
            "You are an assistant that interprets user input - be aware that there may be typos in user input and be logical about matches. Be friendly and use proper punctuation and capitalization. "
            "If the user is being conversational, for example saying hi or hello, return an appropriate response as the method. "
            "The client is requesting help in carrying out a certain reservation action. You will receive their request and today's date and day of the week. "
            "You will also receive a dictionary of service methods and their expected input and descriptions in the form {method signature: description & input expectations}. "
            "You are expected to determine which service method to call based on the user's input, and then parse their request to match the chosen method's expected input. "
            "Compare the user's input against the dictionary. If you're able to match the user's input with a method, send back a string of the corresponding method as the 'method' and the parsed input as 'expected_input'. "
            "Be conscious of potential typos/misspellings and please try to only return one endpoint. "
            "If there is no method match, and the user is not just making conversation, return an empty string. "
            "The service methods are {'check_user_activity': 'Checking whether a specified user is active and visible in the XL. Finding user by name. Expecting an input name as a string.', 'cancel_reservation': 'Cancels the specified reservation. You could receive the date of the reservation to cancel in a variety of date formats, including 'today', 'tomorrow', or a day of the week, potentially along with a reservation time. If there is no date stated, and only a time, assume the day is today. Please be aware of the current date, how it relates to weekdays, and translate the user's input date and time so that it is formatted as a string with the format '%Y-%m-%d %H:%M:%S'; if there is not enough information please return 'Not enough reservation info' as the method.'}. "
        )

        # not yet implemented methods: 'get_active_classmates': 'Get active users in a specified course. Expecting a course department and number.', 'draft_reservation': 'When a user begins the process of making a reservation, a draft holds its place until confirmed. Expecting a ReservationRequest; if there is not enough information please return 'Not enough reservation info' as the method.',

        weekday_num: int = date.today().weekday()
        if weekday_num == 0:
            weekday = "Monday"
        elif weekday_num == 1:
            weekday = "Tuesday"
        elif weekday_num == 2:
            weekday = "Wednesday"
        elif weekday_num == 3:
            weekday = "Thursday"
        elif weekday_num == 4:
            weekday = "Friday"
        elif weekday_num == 5:
            weekday = "Saturday"
        elif weekday_num == 6:
            weekday = "Sunday"
        else:
            weekday = ""

        conditional_prompt: str = (
            f"This is the user's request: {user_prompt}. And this is today's date: {weekday}, {str(date.today())}."
        )

        try:
            ai_response: GeneralAIResponse = self._openai_svc.prompt(
                system_prompt=context,
                user_prompt=conditional_prompt,
                response_model=GeneralAIResponse,
            )
        except ValueError as e:
            raise ValueError(f"AI request unable to choose method: {e}.")

        if len(ai_response.method) > 0:
            if ai_response.method == "check_user_activity":
                try:
                    # Check if user exists in database
                    if not self._active_user_svc.user_exists(
                        ai_response.expected_input
                    ):
                        return f"'{ai_response.expected_input}' does not appear to be a valid user in our system. Please check the name and try again."

                    # Otherwise check if active
                    return self._active_user_svc.check_if_active(
                        ai_response.expected_input
                    )
                except Exception as e:
                    return f"Request couldn't be completed, please reattempt with more details. Error: {e}."
            elif ai_response.method == "cancel_reservation":
                # ai formatting date correctly, datetime converting to string correctly
                # return self._reservation_svc.determine_reservation_to_cancel(
                #     reservation_date=datetime.strptime(
                #         ai_response.expected_input, "%Y-%m-%d %H:%M:%S"
                #     )
                # )
                try:
                    reservation_date = datetime.strptime(
                        ai_response.expected_input, "%Y-%m-%d %H:%M:%S"
                    )
                except Exception:
                    upcoming = self._reservation_svc.get_current_reservations_for_user(
                        self._subject, self._subject
                    )
                    if len(upcoming) == 1:
                        return self._reservation_svc.determine_reservation_to_cancel(
                            reservation_date=upcoming[0].start
                        )
                    return "You have multiple reservations. Please give more information about your reservation so we don't cancel the wrong one!"

                return self._reservation_svc.determine_reservation_to_cancel(
                    reservation_date=reservation_date
                )
            # elif ai_response.method == "get_active_classmates":
            #     return "We can't handle this request at this time. Stay tuned for when you can!"
            #    try:
            #        return self._active_user_svc.get_active_classmates(
            #            ai_response.expected_input
            #        )
            #    except Exception as e:
            #        return f"Request couldn't be completed, please reattempt with more details. Error: {e}."
            # elif ai_response.method == "draft_reservation":
            #    try:
            #        self._reservation_svc.draft_reservation(self._subject, ReservationRequest(UserIdentity(self._subject.id), ai_response.expected_input)
            #        return "Reservation made!"
            #    except Exception as e:
            #        return f'{str(e)}'
            elif ai_response.method == "Not enough reservation info":
                return "Not enough reservation info."
            else:
                return ai_response.method
        else:
            raise NoSuchPathException()  # thrown if ai returns empty string
