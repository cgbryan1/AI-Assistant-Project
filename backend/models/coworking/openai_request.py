from pydantic import BaseModel

__authors__ = ["Emma Coye", "Manasi Chaudhary", "Caroline Bryan", "Kathryn Brown"]
__copyright__ = "Copyright 2025"
__license__ = "MIT"

class GeneralAIResponse(BaseModel):
    method: str
    expected_input: str

class NoSuchPathException(Exception):
    pass