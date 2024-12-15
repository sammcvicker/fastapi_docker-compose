from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from documents.documents_schema import Document
from users.users_schema import User
from users.users_model import get_current_user
from documents.documents_model import (
    insert_document,
    get_documents_by_user_id,
    edit_document,
)


class NewDocumentRequestForm:
    def __init__(self, title: str):
        self.title = title


class EditDocumentRequestForm:
    def __init__(self, title: str, content: str):
        self.title = title
        self.content = content


documents_router = APIRouter(prefix="/documents")


@documents_router.get("/", response_model=list[Document])
async def get_user_documents(
    current_user: Annotated[User, Depends(get_current_user)],
):
    documents = await get_documents_by_user_id(current_user.id)
    return documents


@documents_router.post("/new", response_model=Document)
async def create_new_document(
    current_user: Annotated[User, Depends(get_current_user)],
    form_data: Annotated[NewDocumentRequestForm, Depends()],
):
    document = await insert_document(current_user.id, form_data.title)
    return document


# Get a particular document the user owns by its id
@documents_router.get("/{document_id}", response_model=Document)
async def get_user_document_by_id(
    current_user: Annotated[User, Depends(get_current_user)],
    document_id: int,
):
    documents = await get_documents_by_user_id(current_user.id)
    document = next((doc for doc in documents if doc.id == document_id), None)
    if document:
        return document
    else:
        raise HTTPException(status_code=404, detail="Document not found")


# Edit the contents of a particular document the user owns by its id
@documents_router.put("/edit/{document_id}", response_model=Document)
async def edit_user_document_by_id(
    current_user: Annotated[User, Depends(get_current_user)],
    document_id: int,
    form_data: Annotated[EditDocumentRequestForm, Depends()],
):
    documents = await get_documents_by_user_id(current_user.id)
    document = next((doc for doc in documents if doc.id == document_id), None)
    if document:
        document = await edit_document(
            current_user.id, document_id, form_data.title, form_data.content
        )
        return document
    else:
        raise HTTPException(status_code=404, detail="Document not found")
