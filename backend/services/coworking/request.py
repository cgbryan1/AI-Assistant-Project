from backend.services.openai import OpenAIService
from backend.models.coworking.request import AIResponse, NoSuchPathException
from typing import Annotated
from fastapi import Depends
from backend.api.coworking.students import check_user_activity, get_active_classmates
# currently importing functions that match API endpoints - DEFINITELY bad practice

__authors__ = ["Emma Coye", "Manasi Chaudhary", "Caroline Bryan", "Kathryn Brown"]
__copyright__ = "Copyright 2025"
__license__ = "MIT"

class AIRequestService:
    """Takes in request from the frontend and has OpenAI decides which API route to use."""

    def __init__(
        self,
        openai_svc: Annotated[OpenAIService, Depends()],
    ):
        """Initialize the User Service."""
        self._openai_svc = openai_svc

    def determine_request(self, user_prompt: str):
        #1 context
        #2 user input
        #3 expected response

        context: str = (
            "You are an assistant that interprets user input - be aware that there may be typos in user input and be logical about matches. "
            "The client is requesting help in carrying out a certain reservation action. "
            "You will receive a dictionary of function and their descriptions in the form {function signature: description} and be asked to determine which function to call based on the user's request. "
            "Compare the input against the dictionary. If you're able to match the user's input with a function, send back a string of the corresponding function. "
            "Be conscious of potential typos/misspellings and please try to only return one endpoint. "
            "If there is no function match, return an empty string. "
            "The functions are {'check_user_activity': 'Checking whether a specifed user is active and visible in the XL. Finding user by PID, onyen, email, or name.', 'get_active_classmates': 'Get active users in a specified course.'}. "
        )

        # TODO: Add in other paths and descriptions as we implement them

        try:
            ai_response: AIResponse = self._openai_svc.prompt(system_prompt=context, user_prompt=user_prompt, response_model=AIResponse)
        except ValueError:
            raise ValueError # catching and rethrowing ai error

        if len(ai_response.message) > 0:
            if ai_response.message == "check_user_activity":
                return check_user_activity(user_prompt)
            elif ai_response.message == "get_active_classmates":
                return get_active_classmates(user_prompt)
        else:
            raise NoSuchPathException # thrown if ai returns empty string