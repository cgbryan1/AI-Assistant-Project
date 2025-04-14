from pydantic import BaseModel

__authors__ = ["Emma Coye", "Manasi Chaudhary", "Caroline Bryan", "Kathryn Brown"]
__copyright__ = "Copyright 2025"
__license__ = "MIT"

class AIResponse(BaseModel):
    message: str

class NoSuchPathException(Exception):
    pass