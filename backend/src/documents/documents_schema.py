from pydantic import BaseModel


class Document(BaseModel):
    id: int | None = None
    user_id: int
    title: str
    content: str | None = None
