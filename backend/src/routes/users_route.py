from typing import Optional, List, Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from users import users_model
from users.users_schema import User, UserInDB
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from users.users_model import (
    get_current_user,
    insert_user,
)
from users.users_schema import Token
from datetime import timedelta

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

users_router = APIRouter(prefix="/users")


@users_router.post("/new")
async def create_new_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    new_user = User(
        username=form_data.username,
    )
    user = await insert_user(new_user, form_data.password)
    return {"detail": f"User {user.username} created successfully"}


# Important that this uses the User response_model and not the UserInDB model (no hashed_password returned)
@users_router.get("/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user
