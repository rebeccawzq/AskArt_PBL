from typing import Optional

from pydantic import BaseModel


class PromptRequest(BaseModel):
    user_prompt: str


class ImgPromptRequest(BaseModel):
    user_prompt: str
    key_words: Optional[list[str]] = []
