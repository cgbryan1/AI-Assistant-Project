from fastapi import APIRouter, Depends, HTTPException
from backend.services.coworking.openai_request import AIRequestService 
from backend.models.coworking.openai_request import NoSuchPathException

__authors__ = ["Emma Coye, Manasi Chaudhary, Caroline Bryan, Kathryn Brown"]
__copyright__ = "Copyright 2025"
__license__ = "MIT"

api = APIRouter(prefix="/api/ai_request")
openapi_tags = {
    "name": "AI",
    "description": "Make a chat request to OpenAI.",
}

@api.get('/',
    summary="Make a chat request to OpenAI",
    description="Determining which API path should be called based on user request.",
    responses={
        200: {
            "description": "Path returned!",
        },
        404: {
            "description": "No current functionality matches your request.",
        },
    },
    tags=["AI"])
def determine_request(
    user_prompt: str,
    request_svc: AIRequestService = Depends()) -> str:
    try:
        # returning endpoint rn just for viewing purposes
        # in actuality would call endpoint function
        return request_svc.determine_request(user_prompt)
        # return "successful AI response!"
    except ValueError:
        return "AI error"
    except NoSuchPathException:
        return "No current functionality matches your request."
    except:
        return "Students endpoint error."