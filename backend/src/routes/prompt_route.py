from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from users.users_schema import User
from users.users_model import get_current_user
from pydantic import BaseModel
import os
import anthropic

prompt_router = APIRouter(prefix="/prompt")


class PromptPutRequestForm(BaseModel):
    prompt: str


def make_user_message(user_message: str) -> dict:
    return {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": user_message,
            }
        ],
    }


@prompt_router.put("", response_model=dict)
async def put_new_prompt(
    current_user: Annotated[User, Depends(get_current_user)],
    form_data: Annotated[PromptPutRequestForm, Depends()],
):
    client = anthropic.Anthropic()
    messages = [make_user_message(form_data.prompt)]
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4096,
        temperature=0.5,
        messages=messages,
    )
    response_text = " ".join(
        [block.text for block in response.content if block.type == "text"]
    )
    # TODO: Store the prompt and its response in the database, implement a GET route to retrieve the prompt and its response
    return {"response": response_text}
