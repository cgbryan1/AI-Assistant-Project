from backend.services.openai import OpenAIService
from backend.models.coworking.openai_request import (
    GeneralAIResponse,
    NoSuchPathException,
)
from typing import Annotated
from fastapi import Depends
from backend.services.coworking.students import ActiveUserService

__authors__ = ["Emma Coye", "Manasi Chaudhary", "Caroline Bryan", "Kathryn Brown"]
__copyright__ = "Copyright 2025"
__license__ = "MIT"


class AIRequestService:
    """Takes in request from the frontend and has OpenAI decides which API route to use."""

    def __init__(
        self,
        openai_svc: Annotated[OpenAIService, Depends()],
        active_user_svc: Annotated[ActiveUserService, Depends()],
    ):
        """Initialize the User Service."""
        self._openai_svc = openai_svc
        self._active_user_svc = active_user_svc

    def determine_request(self, user_prompt: str):
        # 1 context
        # 2 user input
        # 3 expected response

        context: str = (
            "You are an assistant that interprets user input - be aware that there may be typos in user input and be logical about matches. "
            "The client is requesting help in carrying out a certain reservation action. "
            "You will receive a dictionary of service methods and their expected input and descriptions in the form {method signature: description & input expectations} and be asked to determine which method to call based on the user's request. "
            "Compare the input against the dictionary. If you're able to match the user's input with a function, send back a string of the corresponding method and a string of the user's prompt that matches the expected method input. "
            "Be conscious of potential typos/misspellings and please try to only return one endpoint. "
            "If there is no method match, return an empty string. "
            "The functions are {'check_user_activity': 'Checking whether a specifed user is active and visible in the XL. Finding user by PID, onyen, email, or name. Expecting an input name.', 'get_active_classmates': 'Get active users in a specified course. Expecting a course number.'}. "
        )

        try:
            ai_response: GeneralAIResponse = self._openai_svc.prompt(
                system_prompt=context,
                user_prompt=user_prompt,
                response_model=GeneralAIResponse,
            )
            # know that ai_response is populating correctly from testing
        except ValueError:
            raise ValueError(
                "AI request unable to choose method."
            )  # catching and rethrowing ai error

        if len(ai_response.method) > 0:
            if ai_response.method == "check_user_activity":
                try:
                    return self._active_user_svc.check_if_active_by_string(
                        ai_response.expected_input
                    )
                except Exception as e:
                    return f"Request couldn't be completed, please reattempt with more details. Error: {e}."

            elif ai_response.method == "get_active_classmates":
                try:
                    return self._active_user_svc.get_active_classmates(
                        ai_response.expected_input
                    )
                except Exception as e:
                    return f"Request couldn't be completed, please reattempt with more details. Error: {e}."
        else:
            raise NoSuchPathException()  # thrown if ai returns empty string
